"""
MeetingMind - Main FastAPI Server
AI-powered real-time meeting insights tool

Author: Claude
Date: 2025-01-08
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

from gemini_service import GeminiService
from websocket_handler import WebSocketManager
from models import Meeting, ActionItem, MeetingResponse
from metrics import metrics_collector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MeetingMind API",
    description="AI-powered real-time meeting insights tool",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # POC mode - allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with flexible path handling
import os
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(backend_dir), "frontend")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
else:
    # Fallback: create a minimal static handler for testing
    @app.get("/static/{file_path:path}")
    async def serve_static_fallback(file_path: str):
        return {"message": f"Static file {file_path} not available in test mode"}

# Initialize services
gemini_service = GeminiService()
websocket_manager = WebSocketManager()

# In-memory storage for POC (will be replaced with database)
meetings_db: Dict[str, Meeting] = {}
action_items_db: Dict[str, List[ActionItem]] = {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        html_path = os.path.join(frontend_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>MeetingMind</h1><p>Frontend not available in test mode</p>")

@app.post("/api/meetings", response_model=MeetingResponse)
async def create_meeting(meeting_data: dict):
    """Create a new meeting session"""
    try:
        meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        meeting = Meeting(
            id=meeting_id,
            title=meeting_data.get("title", "Untitled Meeting"),
            participants=meeting_data.get("participants", []),
            status="created"
        )
        
        meetings_db[meeting_id] = meeting
        action_items_db[meeting_id] = []
        
        # Update metrics
        metrics_collector.increment("meetings_created")
        metrics_collector.set_gauge("meetings_active", len([m for m in meetings_db.values() if m.status == "active"]))
        
        logger.info(f"Created meeting: {meeting_id}")
        
        return MeetingResponse(
            meeting_id=meeting_id,
            status="created",
            websocket_url=f"ws://localhost:8000/ws/{meeting_id}"
        )
        
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/{meeting_id}")
async def get_meeting(meeting_id: str):
    """Get meeting details and insights"""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting = meetings_db[meeting_id]
    action_items = action_items_db.get(meeting_id, [])
    
    return {
        "meeting_id": meeting_id,
        "title": meeting.title,
        "status": meeting.status,
        "start_time": meeting.start_time.isoformat() if meeting.start_time else None,
        "participants": meeting.participants,
        "transcript": meeting.transcript,
        "insights": meeting.insights,
        "action_items": [item.dict() for item in action_items]
    }

@app.post("/api/analyze/text")
async def analyze_text(data: dict):
    """Analyze meeting text and extract insights"""
    try:
        meeting_id = data.get("meeting_id")
        text = data.get("text", "").strip()
        speaker = data.get("speaker", "Unknown")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Analyze with Gemini
        metrics_collector.increment("gemini_api_calls")
        analysis_result = await gemini_service.analyze_meeting_text(
            text=text,
            context={"speaker": speaker, "meeting_id": meeting_id}
        )
        
        if not analysis_result.get("success"):
            metrics_collector.increment("gemini_api_errors")
            raise HTTPException(status_code=500, detail="Analysis failed")
        
        metrics_collector.increment("text_analyses_performed")
        
        # Update meeting transcript
        if meeting_id and meeting_id in meetings_db:
            meeting = meetings_db[meeting_id]
            if meeting.transcript:
                meeting.transcript += f"\n[{speaker}] {text}"
            else:
                meeting.transcript = f"[{speaker}] {text}"
            
            # Add insights
            if "insights" in analysis_result["data"]:
                insights_count = len(analysis_result["data"]["insights"])
                meeting.insights.extend(analysis_result["data"]["insights"])
                metrics_collector.increment("insights_generated", insights_count)
            
            # Add action items
            if "action_items" in analysis_result["data"]:
                action_items_count = len(analysis_result["data"]["action_items"])
                metrics_collector.increment("action_items_generated", action_items_count)
                
                for item_data in analysis_result["data"]["action_items"]:
                    action_item = ActionItem(
                        meeting_id=meeting_id,
                        description=item_data["description"],
                        assignee=item_data.get("assignee"),
                        due_date=item_data.get("due_date"),
                        priority=item_data.get("priority", "medium"),
                        confidence_score=item_data.get("confidence", 0.0)
                    )
                    action_items_db[meeting_id].append(action_item)
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    """WebSocket endpoint for real-time meeting communication"""
    await websocket_manager.connect(websocket, meeting_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received WebSocket message: {message}")
            
            if message["type"] == "text_input":
                # Process text input
                text = message["data"]["text"]
                speaker = message["data"].get("speaker", "Unknown")
                
                # Analyze text
                analysis_result = await gemini_service.analyze_meeting_text(
                    text=text,
                    context={"speaker": speaker, "meeting_id": meeting_id}
                )
                
                if analysis_result.get("success"):
                    # Send real-time insights to all clients
                    insights_message = {
                        "type": "real_time_insight",
                        "data": {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "analysis": analysis_result["data"],
                            "original_text": text,
                            "speaker": speaker
                        }
                    }
                    await websocket_manager.broadcast(meeting_id, insights_message)
                
                    # Update meeting data
                    if meeting_id in meetings_db:
                        meeting = meetings_db[meeting_id]
                        if meeting.transcript:
                            meeting.transcript += f"\n[{speaker}] {text}"
                        else:
                            meeting.transcript = f"[{speaker}] {text}"
                        
                        # Update insights
                        if "insights" in analysis_result["data"]:
                            meeting.insights.extend(analysis_result["data"]["insights"])
                
            elif message["type"] == "confirm_action_item":
                # Handle action item confirmation
                item_data = message["data"]
                if meeting_id in action_items_db:
                    action_item = ActionItem(
                        meeting_id=meeting_id,
                        description=item_data["description"],
                        assignee=item_data.get("assignee"),
                        due_date=item_data.get("due_date"),
                        priority=item_data.get("priority", "medium"),
                        status="confirmed"
                    )
                    action_items_db[meeting_id].append(action_item)
                    
                    # Broadcast confirmation
                    await websocket_manager.broadcast(meeting_id, {
                        "type": "action_item_confirmed",
                        "data": action_item.dict()
                    })
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, meeting_id)
        logger.info(f"WebSocket disconnected for meeting: {meeting_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket, meeting_id)

@app.get("/api/health")
async def health_check():
    """Enhanced health check endpoint with metrics"""
    health_status = metrics_collector.get_health_status()
    return health_status

@app.get("/api/metrics")
async def get_metrics():
    """Get application metrics in JSON format"""
    return {
        "system": metrics_collector.get_system_metrics(),
        "application": metrics_collector.get_application_metrics(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/metrics")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    from fastapi import Response
    return Response(
        content=metrics_collector.get_prometheus_format(),
        media_type="text/plain"
    )

if __name__ == "__main__":
    # Load environment variables
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "localhost")
    
    logger.info(f"Starting MeetingMind server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )