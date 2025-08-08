"""
MeetingMind - API Tests with Mocks
Test the FastAPI endpoints without external dependencies

Author: Claude
Date: 2025-01-08
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

# Mock the GeminiService to avoid API key requirement
class MockGeminiService:
    def __init__(self):
        self.api_key = "mock_api_key"
        self.base_url = "https://mock-api.com"
        self.model = "mock-model"
        
    async def analyze_meeting_text(self, text, context=None):
        """Mock analysis that returns structured data"""
        return {
            "success": True,
            "data": {
                "content_type": "action_item" if "완료" in text or "해주세요" in text else "discussion",
                "key_points": [text[:50] + "..." if len(text) > 50 else text],
                "insights": [
                    {
                        "type": "key_point",
                        "content": f"분석된 내용: {text[:30]}...",
                        "importance": "medium",
                        "confidence": 0.8
                    }
                ],
                "action_items": [
                    {
                        "description": "모의 액션 아이템",
                        "assignee": context.get("speaker") if context else "미정",
                        "due_date": "2025-01-10",
                        "priority": "medium",
                        "confidence": 0.75
                    }
                ] if "완료" in text or "해주세요" in text else [],
                "sentiment": "positive" if "좋" in text else "neutral",
                "urgency_level": "high" if "긴급" in text or "빨리" in text else "medium",
                "follow_up_needed": True,
                "related_topics": ["회의", "프로젝트"],
                "summary": f"요약: {text[:50]}..."
            }
        }

# Patch the GeminiService import before importing main
with patch('gemini_service.GeminiService', MockGeminiService):
    from main import app

class TestMeetingAPIMock:
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_root_endpoint(self, client):
        """Test the root endpoint serves HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_create_meeting_success(self, client):
        """Test successful meeting creation"""
        meeting_data = {
            "title": "테스트 회의",
            "participants": ["김철수", "이영희"],
            "duration_estimate": 60
        }
        
        response = client.post("/api/meetings", json=meeting_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "meeting_id" in data
        assert data["status"] == "created"
        assert "websocket_url" in data
        assert "meeting_" in data["meeting_id"]
        
        # Verify websocket URL format
        expected_ws_url = f"ws://localhost:8000/ws/{data['meeting_id']}"
        assert data["websocket_url"] == expected_ws_url
    
    def test_create_meeting_minimal_data(self, client):
        """Test meeting creation with minimal data"""
        meeting_data = {
            "title": "최소 데이터 회의"
        }
        
        response = client.post("/api/meetings", json=meeting_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "created"
        assert data["meeting_id"]
    
    def test_create_meeting_validation_error(self, client):
        """Test meeting creation with invalid data"""
        # Missing required title field
        meeting_data = {
            "participants": ["김철수"]
        }
        
        response = client.post("/api/meetings", json=meeting_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_meeting_not_found(self, client):
        """Test getting a non-existent meeting"""
        response = client.get("/api/meetings/nonexistent_meeting")
        assert response.status_code == 404
    
    def test_get_meeting_success(self, client):
        """Test getting an existing meeting"""
        # First create a meeting
        meeting_data = {
            "title": "테스트 회의 조회",
            "participants": ["김철수", "이영희"]
        }
        
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Then get the meeting
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["title"] == "테스트 회의 조회"
        assert data["participants"] == ["김철수", "이영희"]
        assert data["status"] == "created"
        assert "insights" in data
        assert "action_items" in data
        assert isinstance(data["insights"], list)
        assert isinstance(data["action_items"], list)
    
    def test_analyze_text_success(self, client):
        """Test successful text analysis with mock"""
        # Create a meeting first
        meeting_data = {"title": "분석 테스트 회의"}
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Test text analysis
        analysis_data = {
            "meeting_id": meeting_id,
            "text": "내일까지 보고서를 완료해주세요",
            "speaker": "김철수",
            "timestamp": "2025-01-08T10:00:00Z"
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        analysis_result = data["data"]
        assert analysis_result["content_type"] == "action_item"
        assert len(analysis_result["action_items"]) > 0
        assert analysis_result["action_items"][0]["assignee"] == "김철수"
        assert "완료해주세요" in analysis_result["key_points"][0] or "보고서" in analysis_result["key_points"][0]
    
    def test_analyze_text_discussion(self, client):
        """Test text analysis for general discussion"""
        # Create a meeting first
        meeting_data = {"title": "일반 논의 테스트"}
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Test general discussion
        analysis_data = {
            "meeting_id": meeting_id,
            "text": "오늘 날씨가 정말 좋네요. 프로젝트 진행 상황은 어떻게 되고 있나요?",
            "speaker": "이영희"
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        analysis_result = data["data"]
        assert analysis_result["content_type"] == "discussion"
        assert len(analysis_result["insights"]) > 0
    
    def test_analyze_text_empty_text(self, client):
        """Test text analysis with empty text"""
        analysis_data = {
            "meeting_id": "test_meeting",
            "text": "",
            "speaker": "김철수"
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "Text is required" in data["detail"]
    
    def test_analyze_text_missing_fields(self, client):
        """Test text analysis with missing required fields"""
        analysis_data = {
            "meeting_id": "test_meeting",
            "speaker": "김철수"
            # Missing 'text' field
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 422  # Validation error
    
    def test_full_meeting_workflow(self, client):
        """Test complete meeting workflow"""
        # 1. Create meeting
        meeting_data = {
            "title": "완전한 워크플로우 테스트",
            "participants": ["김철수", "이영희", "박민수"],
            "duration_estimate": 45
        }
        
        create_response = client.post("/api/meetings", json=meeting_data)
        assert create_response.status_code == 200
        meeting_id = create_response.json()["meeting_id"]
        
        # 2. Add multiple text analyses
        texts = [
            "안녕하세요, 오늘 회의를 시작하겠습니다.",
            "김철수님, 다음 주까지 디자인 작업을 완료해주세요.",
            "이영희님은 API 개발을 담당하시고, 박민수님은 테스트를 맡아주세요.",
            "회의를 마치겠습니다. 수고하셨습니다."
        ]
        
        speakers = ["진행자", "진행자", "진행자", "진행자"]
        
        for text, speaker in zip(texts, speakers):
            analysis_data = {
                "meeting_id": meeting_id,
                "text": text,
                "speaker": speaker
            }
            
            response = client.post("/api/analyze/text", json=analysis_data)
            assert response.status_code == 200
        
        # 3. Check final meeting state
        final_response = client.get(f"/api/meetings/{meeting_id}")
        assert final_response.status_code == 200
        
        final_data = final_response.json()
        
        # Should have accumulated transcript
        assert len(final_data["transcript"]) > 0
        assert "안녕하세요" in final_data["transcript"]
        assert "수고하셨습니다" in final_data["transcript"]
        
        # Should have insights and action items
        assert len(final_data["insights"]) > 0
        assert len(final_data["action_items"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])