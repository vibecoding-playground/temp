# MeetingMind - 시스템 아키텍처 & API 명세

## 🏗 시스템 아키텍처

### 전체 구조도
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Audio      │  │  Real-time   │  │    Dashboard     │   │
│  │   Input      │  │  Display     │  │   & Insights     │   │
│  │   (WebAPI)   │  │ (WebSocket)  │  │                  │   │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬────────┘   │
│         │                 │                    │            │
└─────────┼─────────────────┼────────────────────┼────────────┘
          │                 │                    │
          │        ┌────────▼────────┐           │
          │        │   WebSocket     │           │
          │        │   Connection    │           │
          │        └────────┬────────┘           │
          │                 │                    │
┌─────────▼─────────────────▼────────────────────▼────────────┐
│                   Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Audio      │  │  WebSocket   │  │   REST API       │  │
│  │  Processing  │  │   Handler    │  │   Endpoints      │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬────────┘  │
│         │                 │                    │           │
│  ┌──────▼─────────────────▼────────────────────▼──────────┐ │
│  │              Gemini Service Layer                     │ │
│  │   ┌────────────┐  ┌─────────────┐  ┌──────────────┐  │ │
│  │   │Text Analysis│ │ Insight Gen │  │Action Items  │  │ │
│  │   └────────────┘  └─────────────┘  └──────────────┘  │ │
│  └───────────────────────┬───────────────────────────────┘ │
└──────────────────────────┼─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                 External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Gemini     │  │   Database   │  │     Future       │ │
│  │     API      │  │   (SQLite)   │  │   Integrations   │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

## 📡 데이터 흐름

### 실시간 회의 분석 플로우
```
1. [사용자] 음성 입력 
   ↓
2. [Browser] Web Speech API → 텍스트 변환
   ↓
3. [WebSocket] 실시간 텍스트 전송
   ↓
4. [Backend] 텍스트 수신 및 큐잉
   ↓
5. [Gemini API] AI 분석 요청
   ↓
6. [Backend] 분석 결과 처리
   ↓
7. [WebSocket] 실시간 인사이트 전송
   ↓
8. [Frontend] UI 업데이트 및 표시
```

## 🔌 API 명세서

### REST API Endpoints

#### 1. 회의 관리
```http
POST /api/meetings
Content-Type: application/json

{
    "title": "주간 팀 미팅",
    "participants": ["김철수", "이영희", "박민수"],
    "duration_estimate": 60
}

Response:
{
    "meeting_id": "meeting_123456",
    "status": "created",
    "websocket_url": "ws://localhost:8000/ws/meeting_123456"
}
```

```http
GET /api/meetings/{meeting_id}

Response:
{
    "meeting_id": "meeting_123456",
    "title": "주간 팀 미팅",
    "status": "active",
    "start_time": "2025-01-08T10:00:00Z",
    "participants": ["김철수", "이영희", "박민수"],
    "transcript": "안녕하세요. 오늘 회의를 시작하겠습니다...",
    "insights": {
        "key_points": ["프로젝트 진행 상황 점검", "다음 주 마감일 확인"],
        "action_items": [
            {
                "id": "action_001",
                "description": "UI 디자인 완성",
                "assignee": "이영희",
                "due_date": "2025-01-15",
                "priority": "high"
            }
        ],
        "decisions": ["React로 프론트엔드 구현 결정"],
        "efficiency_score": 8.5
    }
}
```

#### 2. 실시간 분석
```http
POST /api/analyze/text
Content-Type: application/json

{
    "meeting_id": "meeting_123456",
    "text": "다음 주까지 프로토타입을 완성해야 합니다.",
    "speaker": "김철수",
    "timestamp": "2025-01-08T10:15:30Z"
}

Response:
{
    "analysis": {
        "content_type": "action_item",
        "key_entities": ["프로토타입", "다음 주"],
        "urgency": "high",
        "sentiment": "neutral"
    },
    "extracted_items": [
        {
            "type": "action_item",
            "description": "프로토타입 완성",
            "due_date": "2025-01-15",
            "assignee": "추정불가",
            "confidence": 0.85
        }
    ]
}
```

#### 3. 회의 요약 및 리포트
```http
GET /api/meetings/{meeting_id}/summary?format=detailed

Response:
{
    "meeting_summary": {
        "title": "주간 팀 미팅",
        "date": "2025-01-08",
        "duration": "45분",
        "participants": {
            "total": 3,
            "list": ["김철수", "이영희", "박민수"],
            "participation_stats": {
                "김철수": {"speaking_time": "15분", "participation_rate": 0.33},
                "이영희": {"speaking_time": "20분", "participation_rate": 0.44},
                "박민수": {"speaking_time": "10분", "participation_rate": 0.23}
            }
        },
        "key_insights": {
            "main_topics": [
                "프로젝트 진행 상황",
                "기술 스택 선택",
                "일정 조정"
            ],
            "decisions_made": [
                "React 프론트엔드 도입 결정",
                "다음 주 프로토타입 완성 목표 설정"
            ],
            "action_items": [
                {
                    "id": "ai_001",
                    "description": "UI/UX 디자인 시안 작성",
                    "assignee": "이영희",
                    "due_date": "2025-01-12",
                    "priority": "high",
                    "status": "pending"
                },
                {
                    "id": "ai_002", 
                    "description": "백엔드 API 설계서 작성",
                    "assignee": "김철수",
                    "due_date": "2025-01-10",
                    "priority": "medium",
                    "status": "pending"
                }
            ],
            "follow_up_meetings": [
                {
                    "purpose": "프로토타입 리뷰",
                    "suggested_date": "2025-01-16",
                    "participants": ["김철수", "이영희"]
                }
            ]
        },
        "efficiency_analysis": {
            "overall_score": 8.5,
            "time_allocation": {
                "productive_discussion": 0.75,
                "off_topic": 0.15,
                "administrative": 0.10
            },
            "improvement_suggestions": [
                "사전 아젠다 준비로 효율성 향상 가능",
                "액션 아이템 담당자를 회의 중 명확히 지정"
            ]
        }
    }
}
```

### WebSocket API

#### 연결 및 실시간 통신
```javascript
// WebSocket 연결
const ws = new WebSocket('ws://localhost:8000/ws/meeting_123456');

// 클라이언트 → 서버 메시지
{
    "type": "text_input",
    "data": {
        "text": "안녕하세요, 오늘 회의를 시작하겠습니다.",
        "speaker": "김철수",
        "timestamp": "2025-01-08T10:00:15Z"
    }
}

// 서버 → 클라이언트 메시지 (실시간 분석 결과)
{
    "type": "real_time_insight",
    "data": {
        "timestamp": "2025-01-08T10:00:16Z",
        "insight_type": "meeting_start_detected",
        "content": "회의가 시작되었습니다.",
        "suggestions": ["참석자 확인", "아젠다 공유"]
    }
}

// 서버 → 클라이언트 메시지 (액션 아이템 감지)
{
    "type": "action_item_detected",
    "data": {
        "item": {
            "description": "프로토타입 완성",
            "potential_assignee": "추정불가",
            "due_date": "2025-01-15",
            "confidence": 0.85
        },
        "requires_confirmation": true
    }
}

// 클라이언트 → 서버 메시지 (확인/수정)
{
    "type": "confirm_action_item",
    "data": {
        "item_id": "temp_001",
        "confirmed": true,
        "modifications": {
            "assignee": "이영희",
            "priority": "high"
        }
    }
}
```

## 🗄 데이터베이스 스키마

### SQLite Tables (POC)

#### meetings 테이블
```sql
CREATE TABLE meetings (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    participants TEXT, -- JSON array
    transcript TEXT,
    summary TEXT,
    efficiency_score REAL
);
```

#### action_items 테이블
```sql
CREATE TABLE action_items (
    id TEXT PRIMARY KEY,
    meeting_id TEXT REFERENCES meetings(id),
    description TEXT NOT NULL,
    assignee TEXT,
    due_date DATE,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence_score REAL
);
```

#### insights 테이블
```sql
CREATE TABLE insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id TEXT REFERENCES meetings(id),
    type TEXT NOT NULL, -- 'key_point', 'decision', 'question'
    content TEXT NOT NULL,
    timestamp DATETIME,
    speaker TEXT,
    confidence_score REAL
);
```

## 🔒 보안 고려사항

### API 보안
- **API 키 관리**: 환경변수로 Gemini API 키 보관
- **입력 검증**: 모든 텍스트 입력에 대한 기본 검증
- **Rate Limiting**: API 호출 제한 (향후)

### 데이터 보안  
- **데이터 암호화**: 민감한 회의 내용 암호화 저장 (향후)
- **접근 제어**: 회의별 액세스 토큰 시스템 (향후)
- **데이터 보존**: 자동 삭제 정책 (향후)

## 📊 성능 최적화

### 실시간 처리
- **배치 처리**: 짧은 텍스트는 배치로 묶어서 처리
- **캐싱**: 자주 사용되는 분석 결과 캐싱
- **비동기 처리**: 모든 API 호출 비동기 처리

### 리소스 관리
- **연결 제한**: 동시 WebSocket 연결 수 제한
- **메모리 관리**: 긴 회의의 전체 텍스트 메모리 관리
- **API 호출 최적화**: Gemini API 호출 빈도 최적화

## 🔄 에러 처리 전략

### 클라이언트 에러
```javascript
// WebSocket 연결 실패
{
    "type": "error",
    "code": "WS_CONNECTION_FAILED",
    "message": "WebSocket 연결에 실패했습니다. 네트워크를 확인해주세요."
}

// 음성 인식 실패
{
    "type": "error", 
    "code": "SPEECH_RECOGNITION_FAILED",
    "message": "음성 인식에 실패했습니다. 마이크 권한을 확인해주세요."
}
```

### 서버 에러
```python
# Gemini API 에러 처리
{
    "success": False,
    "error": {
        "code": "GEMINI_API_ERROR",
        "message": "AI 분석 서비스가 일시적으로 사용할 수 없습니다.",
        "retry_after": 30
    }
}
```

## 🚀 확장성 계획

### 단계별 확장
1. **Phase 1 (POC)**: 단일 서버, SQLite, 기본 기능
2. **Phase 2 (MVP)**: Redis 캐싱, PostgreSQL, 사용자 인증  
3. **Phase 3 (Scale)**: 마이크로서비스, 로드밸런서, CDN

### 기술적 확장점
- **다중 언어**: 한국어/영어 동시 지원
- **음성 품질**: 노이즈 캔슬링, 화자 분리
- **AI 모델**: 다중 AI 모델 앙상블
- **통합**: Slack, Teams, Zoom API 연동