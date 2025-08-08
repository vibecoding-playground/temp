"""
MeetingMind - Data Models
Pydantic models for API requests and responses

Author: Claude
Date: 2025-01-08
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ActionItem(BaseModel):
    """Action item model"""
    id: str = Field(default_factory=lambda: f"ai_{uuid.uuid4().hex[:8]}")
    meeting_id: str
    description: str
    assignee: Optional[str] = None
    due_date: Optional[str] = None  # ISO date string
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|cancelled)$")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Insight(BaseModel):
    """Meeting insight model"""
    id: str = Field(default_factory=lambda: f"insight_{uuid.uuid4().hex[:8]}")
    type: str  # key_point, decision, question, concern
    content: str
    importance: str = Field(default="medium", pattern="^(high|medium|low)$")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    speaker: Optional[str] = None
    timestamp: Optional[datetime] = None

class ParticipantStats(BaseModel):
    """Participant statistics model"""
    name: str
    speaking_time_minutes: float = 0.0
    word_count: int = 0
    participation_rate: float = 0.0
    contribution_type: List[str] = []  # ideas, questions, decisions, etc.

class Meeting(BaseModel):
    """Meeting model"""
    id: str
    title: str
    participants: List[str] = []
    status: str = Field(default="created", pattern="^(created|active|paused|completed|cancelled)$")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    transcript: Optional[str] = ""
    insights: List[Dict[str, Any]] = []
    efficiency_score: Optional[float] = None
    summary: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class MeetingCreate(BaseModel):
    """Request model for creating a meeting"""
    title: str = Field(..., min_length=1, max_length=200)
    participants: List[str] = []
    duration_estimate: Optional[int] = None  # minutes
    agenda: Optional[str] = None

class MeetingResponse(BaseModel):
    """Response model for meeting creation"""
    meeting_id: str
    status: str
    websocket_url: str

class TextAnalysisRequest(BaseModel):
    """Request model for text analysis"""
    meeting_id: str
    text: str = Field(..., min_length=1)
    speaker: Optional[str] = "Unknown"
    timestamp: Optional[str] = None

class TextAnalysisResponse(BaseModel):
    """Response model for text analysis"""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    extracted_items: List[Dict[str, Any]] = []
    error: Optional[str] = None

class MeetingSummary(BaseModel):
    """Comprehensive meeting summary model"""
    meeting_id: str
    title: str
    date: str
    duration_minutes: float
    participants: Dict[str, Any]
    key_insights: Dict[str, Any]
    efficiency_analysis: Dict[str, Any]
    action_items: List[ActionItem] = []

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str
    data: Dict[str, Any] = {}
    timestamp: Optional[str] = None
    sender: Optional[str] = None

class RealTimeInsight(BaseModel):
    """Real-time insight model"""
    insight_type: str  # meeting_start, action_item_detected, decision_made, etc.
    content: str
    suggestions: List[str] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_confirmation: bool = False

class MeetingEfficiency(BaseModel):
    """Meeting efficiency analysis model"""
    overall_score: float = Field(ge=0.0, le=10.0)
    time_allocation: Dict[str, float]  # productive, off_topic, administrative
    participation_balance: str  # balanced, unbalanced
    decision_efficiency: float = Field(ge=0.0, le=1.0)
    action_item_clarity: float = Field(ge=0.0, le=1.0)
    improvement_suggestions: List[str] = []

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    services: Optional[Dict[str, str]] = None

# Enum-like constants
class MeetingStatus:
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Priority:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ActionItemStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InsightType:
    KEY_POINT = "key_point"
    DECISION = "decision"
    ACTION_ITEM = "action_item"
    QUESTION = "question"
    CONCERN = "concern"
    OFF_TOPIC = "off_topic"

class WebSocketMessageType:
    # Client to Server
    TEXT_INPUT = "text_input"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
    USER_TYPING = "user_typing"
    PING = "ping"
    CONFIRM_ACTION_ITEM = "confirm_action_item"
    
    # Server to Client
    CONNECTION_ESTABLISHED = "connection_established"
    TEXT_RECEIVED = "text_received"
    ANALYSIS_RESULT = "analysis_result"
    REAL_TIME_INSIGHT = "real_time_insight"
    ACTION_ITEM_DETECTED = "action_item_detected"
    ACTION_ITEM_CONFIRMED = "action_item_confirmed"
    PARTICIPANT_JOINED = "participant_joined"
    PARTICIPANT_LEFT = "participant_left"
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"
    PONG = "pong"
    ERROR = "error"

# Validation functions
def validate_meeting_id(meeting_id: str) -> bool:
    """Validate meeting ID format"""
    return bool(meeting_id and isinstance(meeting_id, str) and len(meeting_id) > 0)

def validate_priority(priority: str) -> bool:
    """Validate priority value"""
    return priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]

def validate_status(status: str) -> bool:
    """Validate meeting status"""
    return status in [
        MeetingStatus.CREATED, 
        MeetingStatus.ACTIVE, 
        MeetingStatus.PAUSED, 
        MeetingStatus.COMPLETED, 
        MeetingStatus.CANCELLED
    ]

# Sample data for development/testing
SAMPLE_MEETING = Meeting(
    id="meeting_20250108_100000",
    title="주간 팀 미팅",
    participants=["김철수", "이영희", "박민수"],
    status=MeetingStatus.ACTIVE,
    insights=[
        {
            "type": InsightType.KEY_POINT,
            "content": "이번 주 프로젝트 진행률은 75%입니다",
            "importance": Priority.HIGH,
            "confidence": 0.9
        }
    ]
)

SAMPLE_ACTION_ITEMS = [
    ActionItem(
        meeting_id="meeting_20250108_100000",
        description="UI 디자인 시안 작성",
        assignee="이영희",
        due_date="2025-01-15",
        priority=Priority.HIGH,
        confidence_score=0.85
    ),
    ActionItem(
        meeting_id="meeting_20250108_100000",
        description="백엔드 API 문서 작성",
        assignee="김철수",
        due_date="2025-01-12",
        priority=Priority.MEDIUM,
        confidence_score=0.92
    )
]