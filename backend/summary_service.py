"""
MeetingMind - Meeting Summary Service
Generates comprehensive meeting summaries and reports

Author: Claude
Date: 2025-01-08
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
import logging
from gemini_service import GeminiService

logger = logging.getLogger(__name__)


class MeetingSummaryService:
    """Service for generating comprehensive meeting summaries"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    async def generate_meeting_summary(
        self, 
        meeting_id: str,
        transcript: str,
        insights: List[Dict],
        action_items: List[Dict],
        participants: List[str],
        duration_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive meeting summary report"""
        
        try:
            # Create context for summary generation
            context = {
                "meeting_id": meeting_id,
                "participants": participants,
                "duration_minutes": duration_minutes,
                "total_insights": len(insights),
                "total_action_items": len(action_items)
            }
            
            # Generate summary using Gemini
            summary_prompt = self._create_summary_prompt(
                transcript, insights, action_items, context
            )
            
            response = await self.gemini_service._call_gemini_api(summary_prompt)
            
            if response:
                summary_data = self.gemini_service._parse_gemini_response(response)
                
                # Enhance with metadata
                enhanced_summary = {
                    "meeting_id": meeting_id,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "participants": participants,
                    "duration_minutes": duration_minutes,
                    "summary": summary_data.get("data", {}),
                    "raw_data": {
                        "total_insights": len(insights),
                        "total_action_items": len(action_items),
                        "transcript_length": len(transcript)
                    }
                }
                
                return {
                    "success": True,
                    "data": enhanced_summary
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate summary"
                }
                
        except Exception as e:
            logger.error(f"Error generating meeting summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_summary_prompt(
        self,
        transcript: str, 
        insights: List[Dict],
        action_items: List[Dict],
        context: Dict
    ) -> str:
        """Create a comprehensive prompt for meeting summary generation"""
        
        # Format insights for context
        insights_text = "\n".join([
            f"- {insight.get('description', '')}" for insight in insights
        ]) if insights else "No specific insights captured."
        
        # Format action items for context  
        action_items_text = "\n".join([
            f"- {item.get('description', '')} (담당자: {item.get('assignee', '미정')}, 기한: {item.get('due_date', '미정')})"
            for item in action_items
        ]) if action_items else "No action items identified."
        
        participants_text = ", ".join(context.get("participants", ["참석자 정보 없음"]))
        
        prompt = f"""
다음 회의 내용을 바탕으로 종합적인 회의 요약 보고서를 작성해주세요.

**회의 정보:**
- 회의 ID: {context.get('meeting_id')}
- 참석자: {participants_text}
- 소요시간: {context.get('duration_minutes', '정보없음')}분
- 총 인사이트: {context.get('total_insights')}개
- 총 액션아이템: {context.get('total_action_items')}개

**회의 전체 대화록:**
{transcript}

**주요 인사이트:**
{insights_text}

**액션 아이템:**
{action_items_text}

위 정보를 종합하여 다음 구조로 회의 요약 보고서를 JSON 형식으로 작성해주세요:

{{
    "executive_summary": "회의의 핵심 내용을 2-3문장으로 요약",
    "key_decisions": [
        {{
            "decision": "결정된 사항",
            "rationale": "결정 이유",
            "impact": "예상 영향"
        }}
    ],
    "discussion_highlights": [
        {{
            "topic": "논의 주제",
            "summary": "논의 내용 요약",
            "participants": ["관련 참석자들"]
        }}
    ],
    "action_items_summary": [
        {{
            "category": "카테고리 (예: 개발, 디자인, 기획)",
            "items": [
                {{
                    "task": "할 일",
                    "assignee": "담당자",
                    "due_date": "기한",
                    "priority": "우선순위"
                }}
            ]
        }}
    ],
    "next_steps": [
        "다음 단계로 취해야 할 구체적인 행동들"
    ],
    "risks_and_concerns": [
        {{
            "risk": "위험 요소",
            "severity": "심각도 (high/medium/low)",
            "mitigation": "완화 방안"
        }}
    ],
    "follow_up_meeting": {{
        "needed": true/false,
        "suggested_date": "제안 날짜 또는 null",
        "agenda_items": ["다음 회의에서 논의할 항목들"]
    }},
    "meeting_effectiveness": {{
        "score": "1-10점 사이의 회의 효율성 점수",
        "strengths": ["회의의 강점들"],
        "improvements": ["개선 사항들"]
    }}
}}

**중요:** 응답은 반드시 유효한 JSON 형식이어야 합니다. 마크다운 코드 블록 없이 순수 JSON만 반환해주세요.
"""
        return prompt
    
    async def export_summary_to_format(
        self, 
        summary_data: Dict, 
        format_type: str = "markdown"
    ) -> Dict[str, Any]:
        """Export meeting summary to different formats"""
        
        try:
            if format_type == "markdown":
                content = self._format_as_markdown(summary_data)
                return {
                    "success": True,
                    "content": content,
                    "format": "markdown",
                    "filename": f"meeting_summary_{summary_data.get('meeting_id')}.md"
                }
            elif format_type == "json":
                content = json.dumps(summary_data, ensure_ascii=False, indent=2)
                return {
                    "success": True,
                    "content": content,
                    "format": "json",
                    "filename": f"meeting_summary_{summary_data.get('meeting_id')}.json"
                }
            elif format_type == "txt":
                content = self._format_as_text(summary_data)
                return {
                    "success": True,
                    "content": content,
                    "format": "txt",
                    "filename": f"meeting_summary_{summary_data.get('meeting_id')}.txt"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format_type}"
                }
                
        except Exception as e:
            logger.error(f"Error exporting summary to {format_type}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_as_markdown(self, summary_data: Dict) -> str:
        """Format summary as Markdown"""
        summary = summary_data.get("summary", {})
        
        md_content = f"""# 회의 요약 보고서

## 기본 정보
- **회의 ID**: {summary_data.get('meeting_id')}
- **생성일시**: {summary_data.get('generated_at')}
- **참석자**: {', '.join(summary_data.get('participants', []))}
- **소요시간**: {summary_data.get('duration_minutes', 'N/A')}분

## 📋 요약
{summary.get('executive_summary', 'N/A')}

## 🎯 주요 결정사항
"""
        
        for decision in summary.get('key_decisions', []):
            md_content += f"""
### {decision.get('decision')}
- **이유**: {decision.get('rationale')}
- **예상 영향**: {decision.get('impact')}
"""
        
        md_content += "\n## 💬 논의 하이라이트\n"
        
        for highlight in summary.get('discussion_highlights', []):
            md_content += f"""
### {highlight.get('topic')}
{highlight.get('summary')}
- **관련 참석자**: {', '.join(highlight.get('participants', []))}
"""
        
        md_content += "\n## ✅ 액션 아이템\n"
        
        for category in summary.get('action_items_summary', []):
            md_content += f"\n### {category.get('category')}\n"
            for item in category.get('items', []):
                md_content += f"- **{item.get('task')}**\n"
                md_content += f"  - 담당자: {item.get('assignee')}\n"
                md_content += f"  - 기한: {item.get('due_date')}\n"
                md_content += f"  - 우선순위: {item.get('priority')}\n"
        
        md_content += "\n## 🚀 다음 단계\n"
        for step in summary.get('next_steps', []):
            md_content += f"- {step}\n"
        
        md_content += "\n## ⚠️ 위험 요소 및 우려사항\n"
        for risk in summary.get('risks_and_concerns', []):
            md_content += f"- **{risk.get('risk')}** (심각도: {risk.get('severity')})\n"
            md_content += f"  - 완화방안: {risk.get('mitigation')}\n"
        
        follow_up = summary.get('follow_up_meeting', {})
        if follow_up.get('needed'):
            md_content += f"\n## 📅 후속 회의\n"
            md_content += f"- **필요성**: 예\n"
            md_content += f"- **제안 날짜**: {follow_up.get('suggested_date', 'TBD')}\n"
            md_content += "- **안건**:\n"
            for item in follow_up.get('agenda_items', []):
                md_content += f"  - {item}\n"
        
        effectiveness = summary.get('meeting_effectiveness', {})
        md_content += f"\n## 📊 회의 효율성\n"
        md_content += f"- **점수**: {effectiveness.get('score')}/10\n"
        md_content += "- **강점**:\n"
        for strength in effectiveness.get('strengths', []):
            md_content += f"  - {strength}\n"
        md_content += "- **개선사항**:\n"
        for improvement in effectiveness.get('improvements', []):
            md_content += f"  - {improvement}\n"
        
        return md_content
    
    def _format_as_text(self, summary_data: Dict) -> str:
        """Format summary as plain text"""
        summary = summary_data.get("summary", {})
        
        text_content = f"""회의 요약 보고서
====================

기본 정보:
- 회의 ID: {summary_data.get('meeting_id')}
- 생성일시: {summary_data.get('generated_at')}
- 참석자: {', '.join(summary_data.get('participants', []))}
- 소요시간: {summary_data.get('duration_minutes', 'N/A')}분

요약:
{summary.get('executive_summary', 'N/A')}

주요 결정사항:
"""
        
        for i, decision in enumerate(summary.get('key_decisions', []), 1):
            text_content += f"""
{i}. {decision.get('decision')}
   이유: {decision.get('rationale')}
   예상 영향: {decision.get('impact')}
"""
        
        text_content += "\n액션 아이템:\n"
        for category in summary.get('action_items_summary', []):
            text_content += f"\n[{category.get('category')}]\n"
            for item in category.get('items', []):
                text_content += f"- {item.get('task')} (담당: {item.get('assignee')}, 기한: {item.get('due_date')})\n"
        
        return text_content


# Global summary service instance
summary_service = MeetingSummaryService()