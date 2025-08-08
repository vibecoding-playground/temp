# MeetingMind - 프로젝트 계획서

## 🎯 프로젝트 비전
AI가 분석하는 실시간 회의 인사이트로 전 세계 회의 문화를 혁신한다.

## 📊 문제 정의
- **90%의 회의**가 비효율적이고 명확한 결론 없이 끝남
- **60%의 액션 아이템**이 추적되지 않아 실행되지 않음
- **참석자의 30%**만 적극적으로 참여
- **회의록 작성**에 평균 30분 소요

## 💡 솔루션
MeetingMind는 Gemini AI를 활용하여 실시간으로 회의를 분석하고 구조화된 인사이트를 제공합니다.

### 핵심 기능
1. **실시간 음성/텍스트 분석**
   - Web Speech API로 음성 실시간 변환
   - Gemini API로 맥락 이해 및 분석

2. **스마트 요약 생성**
   - 핵심 논의 사항 자동 추출
   - 의사결정 포인트 식별
   - 합의/미합의 사항 구분

3. **액션 아이템 자동 생성**
   - 담당자 자동 식별
   - 우선순위 및 기한 제안
   - 진행 상황 추적

4. **참석자 인사이트**
   - 발언 시간 및 빈도 분석
   - 참여도 점수 산출
   - 기여 유형 분류 (아이디어 제시, 의사결정, 질문 등)

5. **회의 효율성 분석**
   - 목표 달성도 평가
   - 시간 활용 효율성
   - 개선 포인트 제안

### 기술 아키텍처
```
Frontend (Web Interface)
├── Audio Input (Web Audio API)
├── Real-time Display (WebSocket)
└── Dashboard (Charts & Insights)

Backend (Python FastAPI)
├── WebSocket Handler
├── Audio Processing
├── Gemini API Integration
└── Data Storage

AI Processing
├── Real-time Transcription
├── Content Analysis (Gemini)
├── Insight Generation
└── Action Item Extraction
```

## 🎯 타깃 사용자
- **Primary**: 기업 팀 리더, 프로젝트 매니저
- **Secondary**: 스타트업 창업자, 컨설턴트
- **Tertiary**: 학회, 연구팀, 비영리 조직

## 🚀 개발 마일스톤

### Phase 1: POC (1-2주)
- [x] 기본 음성 인식 및 텍스트 처리
- [ ] Gemini API 연동
- [ ] 기본 요약 기능
- [ ] 간단한 웹 인터페이스

### Phase 2: MVP (3-4주)  
- [ ] 실시간 분석 최적화
- [ ] 액션 아이템 생성
- [ ] 참석자 분석
- [ ] 데이터 저장 및 이력

### Phase 3: Production (5-8주)
- [ ] 고도화된 인사이트
- [ ] 다양한 출력 형식
- [ ] 성능 최적화
- [ ] 보안 강화

## 💰 비즈니스 모델
1. **Freemium**: 월 10회 무료, 무제한 유료
2. **Enterprise**: 팀/조직 단위 구독
3. **API**: 타사 서비스 통합

## 📈 성공 지표
- **사용자 만족도**: 4.5/5.0 이상
- **시간 절약**: 회의 후 정리 시간 80% 단축
- **액션 아이템 실행률**: 기존 40% → 80% 향상
- **월간 활성 사용자**: 10,000명 (6개월 목표)

## 🔮 향후 확장 계획
- 다국어 지원 (한국어, 영어, 일본어, 중국어)
- Slack, Teams, Zoom 통합
- 모바일 앱 개발
- AI 회의 코치 기능