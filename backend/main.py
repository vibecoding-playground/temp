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

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

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
        with open("../frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>MeetingMind</h1><p>Frontend not found</p>")

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
        analysis_result = await gemini_service.analyze_meeting_text(
            text=text,
            context={"speaker": speaker, "meeting_id": meeting_id}
        )
        
        if not analysis_result.get("success"):
            raise HTTPException(status_code=500, detail="Analysis failed")
        
        # Update meeting transcript
        if meeting_id and meeting_id in meetings_db:
            meeting = meetings_db[meeting_id]
            if meeting.transcript:
                meeting.transcript += f"\n[{speaker}] {text}"
            else:
                meeting.transcript = f"[{speaker}] {text}"
            
            # Add insights
            if "insights" in analysis_result["data"]:
                meeting.insights.extend(analysis_result["data"]["insights"])
            
            # Add action items
            if "action_items" in analysis_result["data"]:
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

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