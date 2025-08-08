#!/usr/bin/env python3
"""
회의 요약 보고서 기능 테스트 스크립트
새로 구현된 meeting summary 기능을 테스트합니다.

Author: Claude
Date: 2025-01-08
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Add backend to path
sys.path.insert(0, 'backend')

from summary_service import summary_service

async def test_summary_generation():
    """회의 요약 보고서 생성 테스트"""
    print("📋 회의 요약 보고서 기능 테스트")
    print("=" * 50)
    
    # Sample meeting data
    sample_transcript = """
    [프로젝트 매니저] 안녕하세요, 오늘은 Q1 프로젝트 진행 상황을 점검하고 다음 단계를 논의하겠습니다.
    
    [개발팀장] 현재 백엔드 API는 80% 완성되었고, 다음 주까지 완전히 마무리될 예정입니다.
    
    [디자이너] UI/UX 디자인은 95% 완료되었고, 남은 건 결제 화면 디자인뿐입니다.
    
    [프로젝트 매니저] 좋습니다. 그러면 김개발님은 다음 주 금요일까지 API 개발을 완료해주시고, 
    박디자인님은 화요일까지 결제 화면 디자인을 마무리해주세요.
    
    [QA팀장] 테스트 환경은 준비되었고, API가 완료되는 대로 바로 테스트를 시작할 수 있습니다.
    
    [프로젝트 매니저] 런칭 날짜는 3월 15일로 확정하고, 모든 테스트는 3월 1일까지 완료해야 합니다.
    """
    
    sample_insights = [
        {"description": "프로젝트 진행률이 전반적으로 양호함", "confidence": 0.9},
        {"description": "개발 일정이 타이트하지만 달성 가능해 보임", "confidence": 0.8},
        {"description": "팀 간 커뮤니케이션이 원활함", "confidence": 0.85}
    ]
    
    sample_action_items = [
        {
            "description": "백엔드 API 개발 완료",
            "assignee": "김개발",
            "due_date": "다음 주 금요일",
            "priority": "high"
        },
        {
            "description": "결제 화면 디자인 완료", 
            "assignee": "박디자인",
            "due_date": "화요일",
            "priority": "medium"
        },
        {
            "description": "모든 테스트 완료",
            "assignee": "QA팀",
            "due_date": "3월 1일",
            "priority": "high"
        }
    ]
    
    participants = ["프로젝트 매니저", "개발팀장", "디자이너", "QA팀장"]
    
    try:
        print("1. 회의 요약 생성 중...")
        
        # Generate meeting summary
        result = await summary_service.generate_meeting_summary(
            meeting_id="test_meeting_001",
            transcript=sample_transcript,
            insights=sample_insights,
            action_items=sample_action_items,
            participants=participants,
            duration_minutes=45
        )
        
        if result.get("success"):
            summary_data = result["data"]
            print("   ✅ 요약 생성 성공!")
            print(f"   📊 회의 ID: {summary_data['meeting_id']}")
            print(f"   👥 참석자: {len(summary_data['participants'])}명")
            print(f"   ⏱️  소요시간: {summary_data['duration_minutes']}분")
            
            # Display summary content
            summary_content = summary_data.get("summary", {})
            print(f"\n   📋 요약 내용:")
            print(f"      - 핵심 요약: {summary_content.get('executive_summary', 'N/A')}")
            print(f"      - 주요 결정: {len(summary_content.get('key_decisions', []))}개")
            print(f"      - 논의 하이라이트: {len(summary_content.get('discussion_highlights', []))}개")
            print(f"      - 액션 아이템 카테고리: {len(summary_content.get('action_items_summary', []))}개")
            
        else:
            print(f"   ❌ 요약 생성 실패: {result.get('error')}")
            return
        
        print("\n2. 다양한 형식으로 내보내기 테스트...")
        
        # Test different export formats
        formats = ["markdown", "json", "txt"]
        for format_type in formats:
            print(f"\n   📄 {format_type.upper()} 형식 내보내기...")
            
            export_result = await summary_service.export_summary_to_format(
                summary_data, format_type
            )
            
            if export_result.get("success"):
                print(f"      ✅ 성공! 파일명: {export_result['filename']}")
                content_preview = export_result["content"][:200]
                print(f"      📄 미리보기: {content_preview}...")
            else:
                print(f"      ❌ 실패: {export_result.get('error')}")
        
        print(f"\n{'=' * 50}")
        print("🎉 회의 요약 보고서 기능 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(test_summary_generation())