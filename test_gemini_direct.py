#!/usr/bin/env python3
"""
직접 Gemini API 테스트 스크립트
실제 API 키를 사용하여 Gemini 연동을 테스트합니다.

Author: Claude
Date: 2025-01-08
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Add backend to path
sys.path.insert(0, 'backend')

from gemini_service import GeminiService

async def test_gemini_api():
    """실제 Gemini API 테스트"""
    print("🧪 Gemini API 실제 연동 테스트 시작")
    print("=" * 50)
    
    try:
        # GeminiService 초기화
        print("1. GeminiService 초기화...")
        service = GeminiService()
        print(f"   ✅ API 키: {service.api_key[:10]}..." if service.api_key else "   ❌ API 키 없음")
        print(f"   ✅ 모델: {service.model}")
        
        # 테스트 텍스트들
        test_cases = [
            {
                "name": "간단한 인사",
                "text": "안녕하세요, 오늘 회의를 시작하겠습니다.",
                "speaker": "진행자"
            },
            {
                "name": "액션 아이템 포함",
                "text": "김철수님은 내일까지 UI 디자인을 완료해주시고, 이영희님은 다음 주까지 API 개발을 마무리해주세요.",
                "speaker": "프로젝트 매니저"
            },
            {
                "name": "의사결정",
                "text": "논의 결과, React를 사용하여 프론트엔드를 개발하기로 결정했습니다.",
                "speaker": "기술 리드"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. 테스트: {test_case['name']}")
            print(f"   텍스트: {test_case['text'][:50]}...")
            
            try:
                # API 호출
                result = await service.analyze_meeting_text(
                    text=test_case['text'],
                    context={"speaker": test_case['speaker']}
                )
                
                if result.get("success"):
                    data = result["data"]
                    print(f"   ✅ 분석 성공!")
                    print(f"   📊 유형: {data.get('content_type', 'N/A')}")
                    print(f"   💡 핵심 포인트: {len(data.get('key_points', []))}개")
                    print(f"   📋 액션 아이템: {len(data.get('action_items', []))}개")
                    print(f"   😊 감정: {data.get('sentiment', 'N/A')}")
                    print(f"   ⚡ 긴급도: {data.get('urgency_level', 'N/A')}")
                    
                    # 액션 아이템 상세 출력
                    if data.get('action_items'):
                        print("   🎯 액션 아이템 상세:")
                        for item in data['action_items']:
                            print(f"      - {item.get('description', 'N/A')}")
                            print(f"        담당자: {item.get('assignee', '미정')}")
                            print(f"        기한: {item.get('due_date', '미정')}")
                            print(f"        우선순위: {item.get('priority', '미정')}")
                else:
                    print(f"   ❌ 분석 실패: {result.get('error', '알 수 없는 오류')}")
                    
            except Exception as e:
                print(f"   ❌ 오류 발생: {e}")
        
        # API 연결 상태 정리
        print(f"\n{'=' * 50}")
        print("📊 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(test_gemini_api())