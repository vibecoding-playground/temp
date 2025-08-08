"""
MeetingMind - Gemini AI Service
Handles all interactions with Google Gemini API

Author: Claude
Date: 2025-01-08
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.5-flash"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_meeting_text(self, text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze meeting text and extract insights, action items, and key points
        
        Args:
            text: The meeting text to analyze
            context: Additional context (speaker, meeting_id, etc.)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(text, context)
            
            # Make API call to Gemini
            response = await self._call_gemini_api(prompt)
            
            if response.get("success"):
                # Parse the response and structure it
                analysis_data = self._parse_gemini_response(response["data"])
                return {
                    "success": True,
                    "data": analysis_data
                }
            else:
                logger.error(f"Gemini API call failed: {response.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": response.get("error", "Analysis failed")
                }
                
        except Exception as e:
            logger.error(f"Error in analyze_meeting_text: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_analysis_prompt(self, text: str, context: Optional[Dict] = None) -> str:
        """Create a structured prompt for meeting analysis"""
        speaker = context.get("speaker", "Unknown") if context else "Unknown"
        
        prompt = f"""
당신은 회의 분석 전문가입니다. 다음 회의 발언을 분석하여 구조화된 인사이트를 제공해주세요.

발언자: {speaker}
발언 내용: "{text}"

다음 JSON 형식으로 응답해주세요:
{{
    "content_type": "해당 발언의 유형 (discussion, action_item, decision, question, off_topic)",
    "key_points": ["핵심 포인트 1", "핵심 포인트 2"],
    "insights": [
        {{
            "type": "key_point|decision|action_item|question",
            "content": "구체적인 인사이트 내용",
            "importance": "high|medium|low",
            "confidence": 0.85
        }}
    ],
    "action_items": [
        {{
            "description": "구체적인 액션 아이템",
            "assignee": "담당자 (명시되지 않은 경우 null)",
            "due_date": "마감일 (YYYY-MM-DD 형식, 명시되지 않은 경우 null)",
            "priority": "high|medium|low",
            "confidence": 0.90
        }}
    ],
    "sentiment": "positive|neutral|negative",
    "urgency_level": "high|medium|low",
    "follow_up_needed": true/false,
    "related_topics": ["관련 주제1", "관련 주제2"],
    "summary": "이 발언의 핵심 요약 (1-2문장)"
}}

분석 기준:
1. 액션 아이템: "~해야 한다", "~하겠다", "~까지 완료" 등의 표현
2. 의사결정: "결정했다", "선택하자", "~로 하자" 등의 표현  
3. 핵심 포인트: 중요한 정보나 논의 사항
4. 질문: 답변이 필요한 내용
5. 긴급도: 시간적 압박이나 우선순위 언급

반드시 유효한 JSON 형식으로만 응답하세요. 추가 설명은 하지 마세요.
"""
        return prompt
    
    async def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to Gemini"""
        try:
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,  # Lower temperature for more consistent JSON
                    "maxOutputTokens": 2048,
                    "topK": 1,
                    "topP": 0.8
                }
            }
            
            response = await self.client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if "candidates" in result and result["candidates"]:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "success": True,
                        "data": content.strip()
                    }
                else:
                    return {
                        "success": False,
                        "error": "No candidates in response"
                    }
            else:
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_gemini_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse Gemini API response and structure the data"""
        try:
            # Try to extract JSON from the response
            # Sometimes Gemini wraps JSON in markdown code blocks
            if "```json" in raw_response:
                start = raw_response.find("```json") + 7
                end = raw_response.find("```", start)
                json_text = raw_response[start:end].strip()
            elif "```" in raw_response:
                start = raw_response.find("```") + 3
                end = raw_response.rfind("```")
                json_text = raw_response[start:end].strip()
            else:
                json_text = raw_response.strip()
            
            # Parse JSON
            parsed_data = json.loads(json_text)
            
            # Validate and clean the data
            cleaned_data = {
                "content_type": parsed_data.get("content_type", "discussion"),
                "key_points": parsed_data.get("key_points", []),
                "insights": parsed_data.get("insights", []),
                "action_items": parsed_data.get("action_items", []),
                "sentiment": parsed_data.get("sentiment", "neutral"),
                "urgency_level": parsed_data.get("urgency_level", "medium"),
                "follow_up_needed": parsed_data.get("follow_up_needed", False),
                "related_topics": parsed_data.get("related_topics", []),
                "summary": parsed_data.get("summary", "")
            }
            
            return cleaned_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.error(f"Raw response: {raw_response}")
            
            # Fallback: create basic analysis
            return {
                "content_type": "discussion",
                "key_points": ["회의 내용 분석"],
                "insights": [
                    {
                        "type": "key_point",
                        "content": "AI 분석 중 오류가 발생했습니다",
                        "importance": "medium",
                        "confidence": 0.1
                    }
                ],
                "action_items": [],
                "sentiment": "neutral",
                "urgency_level": "medium",
                "follow_up_needed": False,
                "related_topics": [],
                "summary": "분석 오류로 인해 요약을 생성할 수 없습니다"
            }
    
    async def generate_meeting_summary(self, transcript: str, meeting_metadata: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive meeting summary"""
        try:
            prompt = f"""
다음은 완료된 회의의 전체 대화록입니다. 포괄적인 회의 요약을 생성해주세요.

회의 대화록:
{transcript}

다음 JSON 형식으로 회의 요약을 제공해주세요:
{{
    "executive_summary": "회의의 핵심 내용을 2-3문장으로 요약",
    "main_topics": ["주요 논의 주제1", "주요 논의 주제2"],
    "key_decisions": ["결정 사항1", "결정 사항2"],
    "action_items_summary": [
        {{
            "description": "액션 아이템",
            "assignee": "담당자",
            "due_date": "마감일",
            "priority": "우선순위"
        }}
    ],
    "participants_insights": {{
        "most_active": "가장 활발했던 참석자",
        "participation_balance": "균형적|불균형적",
        "collaboration_quality": "excellent|good|fair|poor"
    }},
    "meeting_efficiency": {{
        "score": 8.5,
        "strengths": ["강점1", "강점2"],
        "improvement_areas": ["개선점1", "개선점2"]
    }},
    "follow_up_recommendations": ["후속 조치 권장사항1", "권장사항2"],
    "next_meeting_suggestions": {{
        "needed": true/false,
        "purpose": "다음 회의 목적",
        "timeline": "권장 시기"
    }}
}}
"""
            
            response = await self._call_gemini_api(prompt)
            
            if response.get("success"):
                summary_data = self._parse_gemini_response(response["data"])
                return {
                    "success": True,
                    "data": summary_data
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "Summary generation failed")
                }
                
        except Exception as e:
            logger.error(f"Error generating meeting summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()