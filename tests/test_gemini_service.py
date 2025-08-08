"""
MeetingMind - Gemini Service Tests
Test the Gemini AI integration service

Author: Claude
Date: 2025-01-08
"""

import pytest
import asyncio
import os
import json
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv("../.env")

# Add backend to Python path
import sys
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

from gemini_service import GeminiService

class TestGeminiService:
    
    @pytest.fixture
    async def gemini_service(self):
        """Create a GeminiService instance for testing"""
        return GeminiService()
    
    @pytest.mark.asyncio
    async def test_gemini_service_initialization(self):
        """Test that GeminiService initializes correctly"""
        service = GeminiService()
        assert service.api_key is not None
        assert service.base_url == "https://generativelanguage.googleapis.com/v1beta"
        assert service.model == "gemini-2.5-flash"
        assert service.client is not None
    
    @pytest.mark.asyncio
    async def test_analyze_meeting_text_empty_input(self, gemini_service):
        """Test analyzing empty text input"""
        result = await gemini_service.analyze_meeting_text("")
        
        # Should return an error for empty input
        assert result["success"] == False
        assert "error" in result
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_analyze_meeting_text_success(self, mock_post, gemini_service):
        """Test successful text analysis"""
        # Mock successful API response
        mock_response_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "content_type": "action_item",
                                    "key_points": ["프로젝트 완료"],
                                    "insights": [
                                        {
                                            "type": "action_item",
                                            "content": "내일까지 보고서 작성",
                                            "importance": "high",
                                            "confidence": 0.9
                                        }
                                    ],
                                    "action_items": [
                                        {
                                            "description": "보고서 작성",
                                            "assignee": "김철수",
                                            "due_date": "2025-01-09",
                                            "priority": "high",
                                            "confidence": 0.9
                                        }
                                    ],
                                    "sentiment": "neutral",
                                    "urgency_level": "high",
                                    "follow_up_needed": True,
                                    "related_topics": ["프로젝트"],
                                    "summary": "내일까지 보고서를 완성해야 합니다"
                                })
                            }
                        ]
                    }
                }
            ]
        }
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response_data
        
        # Test the analysis
        result = await gemini_service.analyze_meeting_text(
            text="내일까지 보고서를 작성해주세요",
            context={"speaker": "김철수"}
        )
        
        assert result["success"] == True
        assert "data" in result
        assert result["data"]["content_type"] == "action_item"
        assert len(result["data"]["action_items"]) == 1
        assert result["data"]["action_items"][0]["description"] == "보고서 작성"
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_analyze_meeting_text_api_error(self, mock_post, gemini_service):
        """Test API error handling"""
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"
        
        result = await gemini_service.analyze_meeting_text(
            text="안녕하세요",
            context={"speaker": "테스트"}
        )
        
        assert result["success"] == False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_create_analysis_prompt(self, gemini_service):
        """Test prompt creation"""
        text = "우리는 내일 프로젝트를 완료해야 합니다"
        context = {"speaker": "김철수"}
        
        prompt = gemini_service._create_analysis_prompt(text, context)
        
        assert "김철수" in prompt
        assert text in prompt
        assert "JSON" in prompt
        assert "action_items" in prompt
    
    @pytest.mark.asyncio
    async def test_parse_gemini_response_valid_json(self, gemini_service):
        """Test parsing valid JSON response"""
        json_response = json.dumps({
            "content_type": "discussion",
            "key_points": ["테스트 포인트"],
            "insights": [],
            "action_items": [],
            "sentiment": "positive",
            "urgency_level": "low",
            "follow_up_needed": False,
            "related_topics": ["테스트"],
            "summary": "테스트 요약"
        })
        
        result = gemini_service._parse_gemini_response(json_response)
        
        assert result["content_type"] == "discussion"
        assert result["key_points"] == ["테스트 포인트"]
        assert result["sentiment"] == "positive"
    
    @pytest.mark.asyncio
    async def test_parse_gemini_response_invalid_json(self, gemini_service):
        """Test parsing invalid JSON response"""
        invalid_response = "This is not JSON"
        
        result = gemini_service._parse_gemini_response(invalid_response)
        
        # Should return fallback structure
        assert result["content_type"] == "discussion"
        assert "분석 중 오류가 발생했습니다" in result["insights"][0]["content"]
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_generate_meeting_summary(self, mock_post, gemini_service):
        """Test meeting summary generation"""
        transcript = "[김철수] 안녕하세요\n[이영희] 안녕하세요"
        
        mock_response_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps({
                                    "executive_summary": "간단한 인사 회의",
                                    "main_topics": ["인사"],
                                    "key_decisions": [],
                                    "action_items_summary": [],
                                    "participants_insights": {
                                        "most_active": "김철수",
                                        "participation_balance": "균형적",
                                        "collaboration_quality": "good"
                                    },
                                    "meeting_efficiency": {
                                        "score": 7.5,
                                        "strengths": ["명확한 커뮤니케이션"],
                                        "improvement_areas": ["더 구체적인 논의 필요"]
                                    },
                                    "follow_up_recommendations": [],
                                    "next_meeting_suggestions": {
                                        "needed": False,
                                        "purpose": "",
                                        "timeline": ""
                                    }
                                })
                            }
                        ]
                    }
                }
            ]
        }
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response_data
        
        result = await gemini_service.generate_meeting_summary(transcript)
        
        assert result["success"] == True
        assert "data" in result
        assert result["data"]["executive_summary"] == "간단한 인사 회의"

# Integration test (requires actual API key)
@pytest.mark.integration
class TestGeminiServiceIntegration:
    
    @pytest.mark.asyncio
    async def test_real_gemini_api_call(self):
        """Test actual Gemini API call (requires valid API key)"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not available for integration test")
        
        service = GeminiService()
        
        result = await service.analyze_meeting_text(
            text="내일까지 프레젠테이션 자료를 준비해주세요",
            context={"speaker": "김철수"}
        )
        
        # Basic checks for real API response
        assert "success" in result
        
        if result["success"]:
            assert "data" in result
            data = result["data"]
            assert "content_type" in data
            assert "summary" in data
        else:
            # If API call fails, should still have error handling
            assert "error" in result

if __name__ == "__main__":
    # Run tests with: python -m pytest test_gemini_service.py -v
    # Run integration tests with: python -m pytest test_gemini_service.py::TestGeminiServiceIntegration -v -m integration
    pytest.main([__file__, "-v"])