"""
MeetingMind - Basic Tests
Test basic functionality without external dependencies

Author: Claude
Date: 2025-01-08
"""

import pytest
import sys
import os

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

def test_imports():
    """Test that all modules can be imported"""
    try:
        from models import ActionItem, Meeting, MeetingResponse
        from websocket_handler import WebSocketManager
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")

def test_action_item_model():
    """Test ActionItem model creation"""
    from models import ActionItem
    
    action_item = ActionItem(
        meeting_id="test_meeting",
        description="Test action item",
        assignee="Test User",
        priority="high"
    )
    
    assert action_item.meeting_id == "test_meeting"
    assert action_item.description == "Test action item"
    assert action_item.assignee == "Test User"
    assert action_item.priority == "high"
    assert action_item.status == "pending"  # default value

def test_meeting_model():
    """Test Meeting model creation"""
    from models import Meeting
    
    meeting = Meeting(
        id="test_meeting_123",
        title="Test Meeting",
        participants=["Alice", "Bob"]
    )
    
    assert meeting.id == "test_meeting_123"
    assert meeting.title == "Test Meeting"
    assert meeting.participants == ["Alice", "Bob"]
    assert meeting.status == "created"  # default value
    assert meeting.transcript == ""  # default value

def test_websocket_manager():
    """Test WebSocketManager initialization"""
    from websocket_handler import WebSocketManager
    
    manager = WebSocketManager()
    
    assert isinstance(manager.active_connections, dict)
    assert isinstance(manager.connection_metadata, dict)
    assert len(manager.get_all_meetings()) == 0

def test_meeting_response_model():
    """Test MeetingResponse model"""
    from models import MeetingResponse
    
    response = MeetingResponse(
        meeting_id="test_123",
        status="created",
        websocket_url="ws://localhost:8000/ws/test_123"
    )
    
    assert response.meeting_id == "test_123"
    assert response.status == "created"
    assert response.websocket_url == "ws://localhost:8000/ws/test_123"

def test_validation_functions():
    """Test model validation functions"""
    from models import validate_meeting_id, validate_priority, validate_status
    
    # Test meeting ID validation
    assert validate_meeting_id("meeting_123") == True
    assert validate_meeting_id("") == False
    assert validate_meeting_id(None) == False
    
    # Test priority validation
    assert validate_priority("high") == True
    assert validate_priority("medium") == True
    assert validate_priority("low") == True
    assert validate_priority("invalid") == False
    
    # Test status validation  
    assert validate_status("created") == True
    assert validate_status("active") == True
    assert validate_status("completed") == True
    assert validate_status("invalid") == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])