# 🧠 MeetingMind

> AI 기반 실시간 회의 분석 및 인사이트 도구

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MeetingMind는 Google Gemini AI를 활용하여 회의 내용을 실시간으로 분석하고, 핵심 포인트와 액션 아이템을 자동으로 추출하는 혁신적인 도구입니다.

## ✨ 주요 기능

### 🎤 실시간 음성 인식
- 브라우저 내장 Web Speech API 활용
- 연속 음성 인식 및 실시간 텍스트 변환
- 다국어 지원 (한국어, 영어)

### 🤖 AI 기반 인사이트 분석
- Google Gemini 2.5 Flash 모델 활용
- 핵심 포인트 자동 추출
- 의사결정 사항 식별
- 감정 분석 및 긴급도 평가

### 📋 스마트 액션 아이템 생성
- 담당자 자동 식별
- 마감일 추정
- 우선순위 분류
- 실행 가능한 할일 자동 생성

### 📊 실시간 회의 분석
- 참석자별 발언 시간 분석
- 회의 효율성 점수
- 개선 포인트 제안
- 실시간 요약 생성

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.9 이상
- Google Gemini API 키
- 모던 웹 브라우저 (Chrome, Firefox, Safari, Edge)

### 설치 방법

1. **저장소 클론**
   ```bash
   git clone https://github.com/vibecoding-playground/meetingmind.git
   cd meetingmind
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 또는
   venv\\Scripts\\activate  # Windows
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일에 Gemini API 키 입력
   ```

5. **서버 실행**
   ```bash
   cd backend
   python main.py
   ```

6. **웹 브라우저에서 접속**
   ```
   http://localhost:8000
   ```

## 📁 프로젝트 구조

```
meetingmind/
├── backend/                 # FastAPI 백엔드
│   ├── main.py             # 메인 서버
│   ├── gemini_service.py   # Gemini AI 서비스
│   ├── websocket_handler.py # WebSocket 처리
│   ├── models.py           # 데이터 모델
│   └── utils.py            # 유틸리티 함수
├── frontend/               # 프론트엔드
│   ├── index.html          # 메인 페이지
│   ├── app.js              # JavaScript 로직
│   └── styles.css          # 스타일시트
├── tests/                  # 테스트 파일
│   ├── test_api.py         # API 테스트
│   ├── test_gemini_service.py # Gemini 서비스 테스트
│   └── conftest.py         # 테스트 설정
├── docs/                   # 문서
│   ├── project_plan.md     # 프로젝트 계획
│   ├── system_architecture.md # 시스템 아키텍처
│   └── coding_conventions.md # 코딩 규칙
├── requirements.txt        # Python 의존성
├── .env.example           # 환경변수 예시
├── README.md              # 프로젝트 소개
└── CLAUDE.md              # 개발 상세 문서
```

## 🔧 사용법

### 1. 새 회의 시작

1. **회의 정보 입력**
   - 회의 제목 입력
   - 참석자 이름 추가 (쉼표로 구분)
   - 예상 시간 선택

2. **회의 시작 버튼 클릭**
   - WebSocket 연결 자동 설정
   - 회의실 생성 완료

### 2. 실시간 음성 인식

1. **마이크 버튼 클릭**
   - 브라우저 마이크 권한 허용
   - 음성 인식 자동 시작

2. **발언 시작**
   - 실시간 텍스트 변환
   - AI 분석 자동 진행

### 3. 수동 텍스트 입력

- 발언자 선택 후 텍스트 직접 입력
- 음성 인식과 동일한 AI 분석 제공

### 4. 인사이트 및 액션 아이템 확인

- **인사이트 탭**: AI 분석 결과 실시간 확인
- **액션 아이템 탭**: 자동 생성된 할일 목록
- **요약 탭**: 회의 진행 상황 요약

## 🔗 API 문서

### 주요 엔드포인트

#### 회의 생성
```http
POST /api/meetings
Content-Type: application/json

{
    "title": "주간 팀 미팅",
    "participants": ["김철수", "이영희"],
    "duration_estimate": 60
}
```

#### 텍스트 분석
```http
POST /api/analyze/text
Content-Type: application/json

{
    "meeting_id": "meeting_123",
    "text": "내일까지 보고서를 완성해주세요",
    "speaker": "김철수"
}
```

#### 회의 정보 조회
```http
GET /api/meetings/{meeting_id}
```

### WebSocket API

```javascript
// 연결
const ws = new WebSocket('ws://localhost:8000/ws/meeting_123');

// 텍스트 전송
ws.send(JSON.stringify({
    type: "text_input",
    data: {
        text: "회의 내용",
        speaker: "김철수"
    }
}));
```

## 🧪 테스트

### 단위 테스트 실행
```bash
pytest tests/ -v
```

### 특정 테스트 실행
```bash
pytest tests/test_gemini_service.py -v
```

### 통합 테스트 실행 (API 키 필요)
```bash
pytest tests/ -v -m integration
```

### 테스트 커버리지 확인
```bash
pytest --cov=backend tests/
```

## 🛠 개발

### 개발 환경 설정

1. **개발 서버 실행**
   ```bash
   cd backend
   python main.py
   ```

2. **API 문서 확인**
   ```
   http://localhost:8000/docs
   ```

3. **코드 스타일 검사**
   ```bash
   black backend/
   flake8 backend/
   ```

### 디버깅

- **로그 레벨 설정**: `.env`에서 `LOG_LEVEL=DEBUG`
- **개발자 도구**: 브라우저 F12 → Console 탭
- **API 로그**: 터미널에서 서버 로그 확인

## 🌐 배포

### 로컬 배포
```bash
# 프론트엔드 빌드 (필요시)
cd frontend && npm run build

# 백엔드 실행
cd backend && python main.py
```

### Docker 배포 (향후)
```bash
docker build -t meetingmind .
docker run -p 8000:8000 meetingmind
```

## ⚙️ 설정

### 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GEMINI_API_KEY` | Google Gemini API 키 | 필수 |
| `PORT` | 서버 포트 | 8000 |
| `HOST` | 서버 호스트 | localhost |
| `LOG_LEVEL` | 로그 레벨 | INFO |
| `ENVIRONMENT` | 환경 설정 | development |

### 브라우저 설정

- **마이크 권한**: 음성 인식 사용 시 필수
- **JavaScript 활성화**: 필수
- **WebSocket 지원**: 모던 브라우저는 모두 지원

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 개발 가이드라인

- [코딩 컨벤션](docs/coding_conventions.md) 준수
- 새 기능은 테스트 코드 포함
- 커밋 메시지는 [Conventional Commits](https://conventionalcommits.org/) 형식

## 🐛 버그 리포트

버그를 발견하시면 [Issues](https://github.com/vibecoding-playground/meetingmind/issues)에 신고해주세요.

### 리포트 시 포함 정보
- 운영체제 및 브라우저 정보
- 재현 단계
- 예상 결과 vs 실제 결과
- 스크린샷 (필요시)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 🙏 감사의 말

- **Google Gemini AI**: 강력한 AI 분석 기능 제공
- **FastAPI**: 현대적이고 빠른 API 프레임워크
- **Web Speech API**: 브라우저 내장 음성 인식
- **모든 기여자들**: 프로젝트 발전에 기여해주신 모든 분들

## 📞 연락처

- **프로젝트**: [GitHub Repository](https://github.com/vibecoding-playground/meetingmind)
- **이슈 및 제안**: [GitHub Issues](https://github.com/vibecoding-playground/meetingmind/issues)

---

<div align="center">

**MeetingMind로 더 똑똑한 회의를 경험하세요! 🚀**

[시작하기](#빠른-시작) | [문서](docs/) | [기여하기](#기여하기) | [라이선스](#라이선스)

</div>