"""
MeetingMind - Test Configuration
Pytest configuration and fixtures

Author: Claude
Date: 2025-01-08
"""

import pytest
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv("../.env")

# Configure pytest for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test markers configuration
pytest_plugins = []

def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require API keys)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may take longer to run)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )

# Fixtures for common test data
@pytest.fixture
def sample_meeting_data():
    """Sample meeting data for tests"""
    return {
        "title": "테스트 회의",
        "participants": ["김철수", "이영희", "박민수"],
        "duration_estimate": 60
    }

@pytest.fixture
def sample_text_analysis_data():
    """Sample text analysis data"""
    return {
        "meeting_id": "test_meeting_123",
        "text": "내일까지 프레젠테이션을 준비해주세요",
        "speaker": "김철수",
        "timestamp": "2025-01-08T10:00:00Z"
    }

@pytest.fixture
def sample_gemini_response():
    """Sample Gemini API response for mocking"""
    return {
        "success": True,
        "data": {
            "content_type": "action_item",
            "key_points": ["프레젠테이션 준비"],
            "insights": [
                {
                    "type": "action_item",
                    "content": "프레젠테이션 자료 준비가 필요함",
                    "importance": "high",
                    "confidence": 0.9
                }
            ],
            "action_items": [
                {
                    "description": "프레젠테이션 자료 준비",
                    "assignee": "김철수",
                    "due_date": "2025-01-09",
                    "priority": "high",
                    "confidence": 0.9
                }
            ],
            "sentiment": "neutral",
            "urgency_level": "high",
            "follow_up_needed": True,
            "related_topics": ["프레젠테이션", "업무"],
            "summary": "내일까지 프레젠테이션 준비가 필요합니다"
        }
    }

# Skip tests that require API keys if not available
@pytest.fixture(autouse=True)
def skip_if_no_api_key(request):
    """Skip integration tests if API key is not available"""
    if request.node.get_closest_marker("integration"):
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("Skipping integration test: GEMINI_API_KEY not available")

# Cleanup fixture for database operations (if we add database tests later)
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data before and after tests"""
    # Pre-test cleanup
    yield
    # Post-test cleanup
    pass