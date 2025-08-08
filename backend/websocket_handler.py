"""
MeetingMind - WebSocket Handler
Manages real-time WebSocket connections for meetings

Author: Claude
Date: 2025-01-08
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Dictionary to store active connections by meeting_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, meeting_id: str, user_info: Dict = None):
        """Accept WebSocket connection and add to meeting room"""
        await websocket.accept()
        
        # Initialize meeting room if it doesn't exist
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = set()
        
        # Add connection to meeting room
        self.active_connections[meeting_id].add(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "meeting_id": meeting_id,
            "user_info": user_info or {},
            "connected_at": None  # Could add timestamp
        }
        
        logger.info(f"WebSocket connected to meeting {meeting_id}. "
                   f"Total connections: {len(self.active_connections[meeting_id])}")
        
        # Send welcome message
        await self.send_personal_message(websocket, {
            "type": "connection_established",
            "data": {
                "meeting_id": meeting_id,
                "message": "연결되었습니다. 회의를 시작하세요!"
            }
        })
        
        # Notify other participants about new connection
        await self.broadcast(meeting_id, {
            "type": "participant_joined",
            "data": {
                "meeting_id": meeting_id,
                "participant_count": len(self.active_connections[meeting_id])
            }
        }, exclude_websocket=websocket)
    
    def disconnect(self, websocket: WebSocket, meeting_id: str = None):
        """Remove WebSocket connection"""
        # Get meeting_id from metadata if not provided
        if not meeting_id and websocket in self.connection_metadata:
            meeting_id = self.connection_metadata[websocket]["meeting_id"]
        
        # Remove from active connections
        if meeting_id and meeting_id in self.active_connections:
            self.active_connections[meeting_id].discard(websocket)
            
            # Clean up empty meeting rooms
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
                logger.info(f"Meeting room {meeting_id} cleaned up (no active connections)")
        
        # Remove connection metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        logger.info(f"WebSocket disconnected from meeting {meeting_id}")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            # Connection might be closed, remove it
            meeting_id = self.connection_metadata.get(websocket, {}).get("meeting_id")
            if meeting_id:
                self.disconnect(websocket, meeting_id)
    
    async def broadcast(self, meeting_id: str, message: Dict, exclude_websocket: WebSocket = None):
        """Send message to all connections in a meeting room"""
        if meeting_id not in self.active_connections:
            logger.warning(f"No active connections for meeting {meeting_id}")
            return
        
        # Create a copy of connections to iterate over (to handle concurrent modifications)
        connections = self.active_connections[meeting_id].copy()
        
        # Remove dead connections
        dead_connections = []
        
        for websocket in connections:
            if websocket == exclude_websocket:
                continue
                
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                dead_connections.append(websocket)
        
        # Clean up dead connections
        for dead_ws in dead_connections:
            self.disconnect(dead_ws, meeting_id)
        
        logger.info(f"Broadcasted message to {len(connections) - len(dead_connections)} "
                   f"connections in meeting {meeting_id}")
    
    async def send_to_specific_user(self, meeting_id: str, user_id: str, message: Dict):
        """Send message to a specific user in a meeting"""
        if meeting_id not in self.active_connections:
            return False
        
        for websocket in self.active_connections[meeting_id]:
            metadata = self.connection_metadata.get(websocket, {})
            user_info = metadata.get("user_info", {})
            
            if user_info.get("user_id") == user_id:
                await self.send_personal_message(websocket, message)
                return True
        
        return False
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict]:
        """Get list of participants in a meeting"""
        if meeting_id not in self.active_connections:
            return []
        
        participants = []
        for websocket in self.active_connections[meeting_id]:
            metadata = self.connection_metadata.get(websocket, {})
            user_info = metadata.get("user_info", {})
            participants.append({
                "user_id": user_info.get("user_id", "anonymous"),
                "name": user_info.get("name", "Unknown User"),
                "connected_at": metadata.get("connected_at")
            })
        
        return participants
    
    def get_connection_count(self, meeting_id: str) -> int:
        """Get number of active connections for a meeting"""
        if meeting_id not in self.active_connections:
            return 0
        return len(self.active_connections[meeting_id])
    
    def get_all_meetings(self) -> List[str]:
        """Get list of all active meeting IDs"""
        return list(self.active_connections.keys())
    
    async def handle_message(self, websocket: WebSocket, message: Dict, gemini_service=None):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            # Get meeting_id for this connection
            metadata = self.connection_metadata.get(websocket, {})
            meeting_id = metadata.get("meeting_id")
            
            if not meeting_id:
                await self.send_personal_message(websocket, {
                    "type": "error",
                    "data": {"message": "Meeting ID not found"}
                })
                return
            
            logger.info(f"Handling WebSocket message type: {message_type} for meeting: {meeting_id}")
            
            # Handle different message types
            if message_type == "text_input":
                await self._handle_text_input(websocket, meeting_id, data, gemini_service)
            
            elif message_type == "start_recording":
                await self._handle_start_recording(meeting_id)
            
            elif message_type == "stop_recording":
                await self._handle_stop_recording(meeting_id)
            
            elif message_type == "user_typing":
                await self._handle_user_typing(websocket, meeting_id, data)
            
            elif message_type == "ping":
                await self.send_personal_message(websocket, {
                    "type": "pong",
                    "data": {"timestamp": data.get("timestamp")}
                })
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_personal_message(websocket, {
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message_type}"}
                })
        
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_personal_message(websocket, {
                "type": "error",
                "data": {"message": "Message processing failed"}
            })
    
    async def _handle_text_input(self, websocket: WebSocket, meeting_id: str, data: Dict, gemini_service=None):
        """Handle text input from client"""
        text = data.get("text", "").strip()
        speaker = data.get("speaker", "Unknown")
        
        if not text:
            return
        
        # Broadcast the text input to all participants
        await self.broadcast(meeting_id, {
            "type": "text_received",
            "data": {
                "text": text,
                "speaker": speaker,
                "timestamp": data.get("timestamp")
            }
        })
        
        # If Gemini service is available, analyze the text
        if gemini_service:
            try:
                analysis_result = await gemini_service.analyze_meeting_text(
                    text=text,
                    context={"speaker": speaker, "meeting_id": meeting_id}
                )
                
                if analysis_result.get("success"):
                    # Send analysis results to all participants
                    await self.broadcast(meeting_id, {
                        "type": "analysis_result",
                        "data": {
                            "original_text": text,
                            "speaker": speaker,
                            "analysis": analysis_result["data"],
                            "timestamp": data.get("timestamp")
                        }
                    })
                
            except Exception as e:
                logger.error(f"Error analyzing text in WebSocket: {e}")
    
    async def _handle_start_recording(self, meeting_id: str):
        """Handle recording start event"""
        await self.broadcast(meeting_id, {
            "type": "recording_started",
            "data": {
                "message": "녹음이 시작되었습니다.",
                "timestamp": None  # Could add timestamp
            }
        })
    
    async def _handle_stop_recording(self, meeting_id: str):
        """Handle recording stop event"""
        await self.broadcast(meeting_id, {
            "type": "recording_stopped",
            "data": {
                "message": "녹음이 중지되었습니다.",
                "timestamp": None  # Could add timestamp
            }
        })
    
    async def _handle_user_typing(self, websocket: WebSocket, meeting_id: str, data: Dict):
        """Handle user typing indicator"""
        await self.broadcast(meeting_id, {
            "type": "user_typing",
            "data": {
                "user": data.get("user", "Someone"),
                "is_typing": data.get("is_typing", False)
            }
        }, exclude_websocket=websocket)