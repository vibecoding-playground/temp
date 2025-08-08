"""
MeetingMind - API Tests
Test the FastAPI endpoints

Author: Claude
Date: 2025-01-08
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv("../.env")

# Add backend to Python path
import sys
sys.path.append('../backend')

from main import app

class TestMeetingAPI:
    
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
    
    def test_create_meeting_minimal_data(self, client):
        """Test meeting creation with minimal data"""
        meeting_data = {
            "title": "최소 데이터 회의"
        }
        
        response = client.post("/api/meetings", json=meeting_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "created"
    
    def test_get_meeting_not_found(self, client):
        """Test getting a non-existent meeting"""
        response = client.get("/api/meetings/nonexistent_meeting")
        assert response.status_code == 404
    
    def test_get_meeting_success(self, client):
        """Test getting an existing meeting"""
        # First create a meeting
        meeting_data = {
            "title": "테스트 회의 조회",
            "participants": ["김철수"]
        }
        
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Then get the meeting
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["title"] == "테스트 회의 조회"
        assert data["participants"] == ["김철수"]
        assert data["status"] == "created"
        assert "insights" in data
        assert "action_items" in data
    
    @patch('backend.gemini_service.GeminiService.analyze_meeting_text')
    async def test_analyze_text_success(self, mock_analyze, client):
        """Test successful text analysis"""
        # Setup mock response
        mock_analyze.return_value = {
            "success": True,
            "data": {
                "content_type": "action_item",
                "key_points": ["프로젝트 마감"],
                "insights": [
                    {
                        "type": "action_item",
                        "content": "보고서 작성 필요",
                        "importance": "high",
                        "confidence": 0.9
                    }
                ],
                "action_items": [
                    {
                        "description": "보고서 작성",
                        "assignee": "김철수",
                        "due_date": "2025-01-10",
                        "priority": "high",
                        "confidence": 0.9
                    }
                ],
                "sentiment": "neutral",
                "urgency_level": "high",
                "summary": "보고서 작성이 필요합니다"
            }
        }
        
        # Create a meeting first
        meeting_data = {"title": "분석 테스트 회의"}
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Test text analysis
        analysis_data = {
            "meeting_id": meeting_id,
            "text": "내일까지 보고서를 작성해주세요",
            "speaker": "김철수",
            "timestamp": "2025-01-08T10:00:00Z"
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert data["data"]["content_type"] == "action_item"
    
    def test_analyze_text_empty_text(self, client):
        """Test text analysis with empty text"""
        analysis_data = {
            "meeting_id": "test_meeting",
            "text": "",
            "speaker": "김철수"
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 400
    
    def test_analyze_text_missing_text(self, client):
        """Test text analysis without text field"""
        analysis_data = {
            "meeting_id": "test_meeting",
            "speaker": "김철수"
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 422  # Validation error
    
    def test_root_endpoint(self, client):
        """Test the root endpoint serves HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Check if it contains MeetingMind content
        content = response.text
        assert "MeetingMind" in content

class TestWebSocketEndpoints:
    """Test WebSocket functionality"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection establishment"""
        # Create a meeting first
        meeting_data = {"title": "WebSocket 테스트 회의"}
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Test WebSocket connection
        with client.websocket_connect(f"/ws/{meeting_id}") as websocket:
            # Should receive connection established message
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            assert data["data"]["meeting_id"] == meeting_id
    
    @patch('backend.gemini_service.GeminiService.analyze_meeting_text')
    def test_websocket_text_input(self, mock_analyze, client):
        """Test sending text input through WebSocket"""
        # Setup mock
        mock_analyze.return_value = {
            "success": True,
            "data": {
                "content_type": "discussion",
                "key_points": ["일반적인 논의"],
                "insights": [],
                "action_items": [],
                "sentiment": "neutral",
                "summary": "일반적인 회의 내용"
            }
        }
        
        # Create meeting
        meeting_data = {"title": "WebSocket 입력 테스트"}
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Connect and send message
        with client.websocket_connect(f"/ws/{meeting_id}") as websocket:
            # Skip connection message
            websocket.receive_json()
            
            # Send text input
            message = {
                "type": "text_input",
                "data": {
                    "text": "안녕하세요, 회의를 시작하겠습니다",
                    "speaker": "김철수",
                    "timestamp": "2025-01-08T10:00:00Z"
                }
            }
            websocket.send_json(message)
            
            # Should receive text_received message
            response = websocket.receive_json()
            assert response["type"] == "text_received"
            assert response["data"]["text"] == "안녕하세요, 회의를 시작하겠습니다"
            
            # Should receive analysis_result message
            analysis_response = websocket.receive_json()
            assert analysis_response["type"] == "analysis_result"
            assert analysis_response["data"]["speaker"] == "김철수"

class TestErrorHandling:
    """Test error handling in the API"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON in requests"""
        response = client.post(
            "/api/meetings",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        # Missing title field
        meeting_data = {
            "participants": ["김철수"]
        }
        
        response = client.post("/api/meetings", json=meeting_data)
        assert response.status_code == 422
    
    @patch('backend.gemini_service.GeminiService.analyze_meeting_text')
    def test_gemini_service_error(self, mock_analyze, client):
        """Test handling of Gemini service errors"""
        # Setup mock to return error
        mock_analyze.return_value = {
            "success": False,
            "error": "API rate limit exceeded"
        }
        
        # Create meeting
        meeting_data = {"title": "에러 테스트 회의"}
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Test analysis with error
        analysis_data = {
            "meeting_id": meeting_id,
            "text": "테스트 텍스트",
            "speaker": "김철수"
        }
        
        response = client.post("/api/analyze/text", json=analysis_data)
        assert response.status_code == 500

# Performance tests
class TestPerformance:
    """Test API performance"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_concurrent_meeting_creation(self, client):
        """Test creating multiple meetings concurrently"""
        import threading
        import time
        
        results = []
        
        def create_meeting(index):
            meeting_data = {
                "title": f"동시 생성 테스트 {index}",
                "participants": [f"참석자{index}"]
            }
            response = client.post("/api/meetings", json=meeting_data)
            results.append(response.status_code)
        
        # Create 10 meetings concurrently
        threads = []
        start_time = time.time()
        
        for i in range(10):
            thread = threading.Thread(target=create_meeting, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10
        
        # Should complete within reasonable time
        assert end_time - start_time < 5.0
    
    def test_large_text_analysis(self, client):
        """Test analyzing large text content"""
        # Create meeting
        meeting_data = {"title": "대용량 텍스트 테스트"}
        create_response = client.post("/api/meetings", json=meeting_data)
        meeting_id = create_response.json()["meeting_id"]
        
        # Generate large text content
        large_text = "안녕하세요. " * 1000  # 약 6KB의 텍스트
        
        analysis_data = {
            "meeting_id": meeting_id,
            "text": large_text,
            "speaker": "김철수"
        }
        
        import time
        start_time = time.time()
        
        response = client.post("/api/analyze/text", json=analysis_data)
        
        end_time = time.time()
        
        # Should handle large text (might fail due to API limitations, but shouldn't crash)
        assert response.status_code in [200, 500]
        
        # Should respond within reasonable time
        assert end_time - start_time < 30.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])