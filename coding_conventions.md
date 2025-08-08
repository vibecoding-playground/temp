# MeetingMind - 코딩 컨벤션 & 개발 가이드라인

## 🎯 개발 철학: POC Sprint Mode
- **단순성 우선**: 복잡한 추상화보다 작동하는 코드
- **실용성 중심**: 이론적 완벽함보다 실제 문제 해결
- **빠른 반복**: 작은 기능 단위로 빠르게 구현 및 테스트

## 📁 프로젝트 구조
```
meetingmind/
├── backend/
│   ├── main.py              # FastAPI 메인 서버
│   ├── gemini_service.py    # Gemini API 통합
│   ├── websocket_handler.py # 실시간 통신
│   ├── models.py           # 데이터 모델
│   └── utils.py            # 유틸리티 함수
├── frontend/
│   ├── index.html          # 메인 페이지
│   ├── app.js              # 메인 JavaScript
│   ├── styles.css          # 스타일시트
│   └── components/         # 재사용 컴포넌트 (필요시)
├── tests/                  # 테스트 파일
├── docs/                   # 추가 문서
├── requirements.txt        # Python 의존성
├── README.md              # 프로젝트 소개
├── CLAUDE.md              # 개발 상세 문서
└── .env.example           # 환경변수 예시
```

## 🐍 Python 코딩 스타일

### 기본 원칙
- **PEP 8** 준수하되, 실용성 우선
- **함수명**: snake_case
- **클래스명**: PascalCase  
- **상수**: UPPER_CASE
- **변수**: snake_case

### 파일 헤더 템플릿
```python
"""
MeetingMind - [모듈명]
AI-powered real-time meeting insights tool

Author: Claude
Date: 2025-01-08
"""

import logging
from typing import Dict, List, Optional, Any
```

### 함수 작성 규칙
```python
def process_meeting_text(text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    회의 텍스트를 분석하여 인사이트 추출
    
    Args:
        text: 분석할 회의 텍스트
        context: 추가 맥락 정보 (선택)
    
    Returns:
        Dict containing insights, action_items, summary
    """
    if not text.strip():
        return {"error": "Empty text provided"}
    
    # 실제 구현...
    return {"insights": [], "action_items": [], "summary": ""}
```

### 에러 처리
```python
# POC 모드: 간단한 에러 처리
try:
    result = gemini_api_call(text)
    return {"success": True, "data": result}
except Exception as e:
    logger.error(f"Gemini API error: {e}")
    return {"success": False, "error": str(e)}
```

## 🌐 JavaScript 코딩 스타일

### 기본 원칙
- **Vanilla JavaScript** 사용 (프레임워크 없음)
- **camelCase** 함수/변수명
- **PascalCase** 클래스명
- **UPPER_CASE** 상수

### 기본 구조
```javascript
// app.js - 메인 애플리케이션 로직
class MeetingMind {
    constructor() {
        this.websocket = null;
        this.isRecording = false;
        this.currentMeeting = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
    }

    // 각 메소드는 단일 책임 원칙
    setupEventListeners() {
        document.getElementById('start-btn').addEventListener('click', 
            () => this.startMeeting());
    }
}

// 전역 상수
const GEMINI_API_ENDPOINT = '/api/analyze';
const WEBSOCKET_URL = 'ws://localhost:8000/ws';

// 앱 초기화
const app = new MeetingMind();
```

### 함수 작성
```javascript
/**
 * 회의 시작 함수
 * @param {Object} config - 회의 설정
 * @returns {Promise<boolean>} 성공 여부
 */
async function startMeeting(config = {}) {
    try {
        const response = await fetch('/api/meeting/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Meeting start failed:', error);
        showErrorMessage('회의 시작에 실패했습니다.');
        return false;
    }
}
```

## 🎨 CSS 스타일 가이드

### 구조
```css
/* styles.css */

/* 1. CSS Reset & Base */
* { margin: 0; padding: 0; box-sizing: border-box; }

/* 2. CSS Variables */
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --error-color: #ef4444;
    --bg-color: #f8fafc;
    --text-color: #1e293b;
    --border-radius: 8px;
    --spacing-unit: 1rem;
}

/* 3. Layout Components */
.container { max-width: 1200px; margin: 0 auto; padding: 0 var(--spacing-unit); }
.btn { padding: 12px 24px; border: none; border-radius: var(--border-radius); }
.btn-primary { background: var(--primary-color); color: white; }

/* 4. Specific Components */
.meeting-dashboard { /* ... */ }
.insight-panel { /* ... */ }
```

### 네이밍 규칙
- **BEM 방법론** 적용: `.block__element--modifier`
- **기능 기반** 네이밍: `.meeting-controls`, `.insight-display`

## 🧪 테스트 전략

### 테스트 레벨
1. **Unit Tests**: 개별 함수/모듈 테스트
2. **Integration Tests**: API 통합 테스트  
3. **E2E Tests**: 전체 워크플로우 테스트 (향후)

### Python 테스트
```python
# test_gemini_service.py
import pytest
from backend.gemini_service import analyze_meeting_text

def test_analyze_empty_text():
    result = analyze_meeting_text("")
    assert result["success"] == False
    assert "error" in result

def test_analyze_valid_text():
    text = "우리는 내일까지 프로젝트를 완료해야 합니다."
    result = analyze_meeting_text(text)
    assert result["success"] == True
    assert "action_items" in result["data"]
```

### JavaScript 테스트 (향후)
- **Jest** 또는 **Vitest** 사용 예정
- **브라우저 호환성** 테스트

## 🔧 개발 도구 & 환경

### 필수 도구
- **Python**: 3.9+
- **Node.js**: 18+ (개발 도구용)
- **Git**: 버전 관리
- **VS Code**: 권장 IDE

### 권장 VS Code 확장
- Python
- Pylint
- Black Formatter
- Live Server
- GitLens

### 환경 변수
```bash
# .env 파일
GEMINI_API_KEY=your_api_key_here
ENVIRONMENT=development
LOG_LEVEL=INFO
PORT=8000
```

## 📝 커밋 메시지 규칙

### 형식: `[type]: [description]`

**타입**:
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `refactor`: 코드 리팩토링
- `style`: 코드 스타일 변경
- `docs`: 문서 수정
- `test`: 테스트 추가/수정
- `chore`: 빌드, 설정 등

**예시**:
- `feat: Gemini API 통합 및 실시간 분석 기능 구현`
- `fix: WebSocket 연결 끊김 문제 해결`
- `refactor: 회의 데이터 모델 구조 개선`

## 🚀 배포 & 운영 (향후)

### 개발 환경
```bash
# 백엔드 실행
cd backend && python -m uvicorn main:app --reload --port 8000

# 프론트엔드 실행
cd frontend && python -m http.server 3000
```

### 프로덕션 고려사항 (V2)
- **Docker** 컨테이너화
- **Nginx** 리버스 프록시
- **PostgreSQL** 데이터베이스
- **Redis** 캐싱
- **SSL/HTTPS** 보안

---

## ⚡ POC Sprint 특별 규칙

1. **하드코딩 허용**: 설정값, API 키 등은 코드에 직접 작성 (추후 환경변수 이전)
2. **단일 파일 우선**: 로직이 복잡하지 않으면 한 파일에 모든 기능 구현
3. **완벽한 에러 처리 미룸**: 기본적인 try-catch만 구현
4. **최소한의 추상화**: 재사용이 명확하지 않으면 코드 복사-붙여넣기 허용
5. **빠른 프로토타이핑**: 작동하는 것을 먼저, 최적화는 나중에

> "Make it work, then make it better" - 작동하게 만든 후, 개선한다