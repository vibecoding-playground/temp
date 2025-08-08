# 🔒 MeetingMind 보안 가이드

## ⚠️ 중요한 보안 공지

**API 키가 노출된 경우 즉시 다음 조치를 취하세요:**

1. **🔄 API 키 재생성**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 기존 키 삭제 후 새 키 생성
2. **🚫 노출된 키 비활성화**: 기존 키는 즉시 비활성화
3. **📋 사용 로그 확인**: 의심스러운 API 사용이 있는지 확인

## 🛡️ API 키 안전 관리

### 1. 환경변수로 관리
```bash
# ✅ 올바른 방법: .env 파일 사용
GEMINI_API_KEY=your_actual_api_key_here

# ❌ 잘못된 방법: 코드에 직접 입력
const API_KEY = "AIzaSyCH0lNIaG9Sumvd6c2Tuetg60H2b2r9H1w";  # 절대 금지!
```

### 2. .gitignore 확인
```gitignore
# 필수 항목들
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# 추가 보안 파일들
config/secrets.json
*.key
*.pem
```

### 3. 환경별 키 분리
```bash
# 개발 환경
.env.development
GEMINI_API_KEY=dev_key_here

# 프로덕션 환경  
.env.production
GEMINI_API_KEY=prod_key_here
```

## 🚀 안전한 배포 방법

### 로컬 개발 환경
1. `.env.example`을 `.env`로 복사
2. 실제 API 키로 교체
3. 절대 `.env` 파일을 Git에 커밋하지 않음

### 서버 배포 환경
```bash
# 서버 환경변수 설정
export GEMINI_API_KEY="your_production_key"
export ENVIRONMENT="production"

# 또는 Docker 사용 시
docker run -e GEMINI_API_KEY="your_key" meetingmind
```

### CI/CD 파이프라인
- **GitHub Secrets** 사용하여 API 키 저장
- **환경변수**로 런타임에 주입
- **암호화된 설정 파일** 사용

## 📋 보안 체크리스트

### ✅ 기본 보안
- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] 실제 API 키가 코드에 하드코딩되지 않음
- [ ] `.env.example`에는 placeholder만 존재
- [ ] Git 히스토리에 API 키 없음

### ✅ 고급 보안
- [ ] API 키별 권한 제한 설정
- [ ] IP 주소 제한 (프로덕션)
- [ ] API 사용량 모니터링
- [ ] 주기적 키 교체 (30-90일)

### ✅ 팀 개발
- [ ] 각 개발자별 개별 API 키 사용
- [ ] 공유 키 사용 금지
- [ ] API 키 공유 시 안전한 도구 사용 (1Password, Vault 등)

## 🔧 Google Gemini API 키 생성

### 1단계: Google AI Studio 접속
- [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

### 2단계: API 키 생성
1. **"Create API key"** 클릭
2. **프로젝트 선택** (기존 또는 새 프로젝트)
3. **키 생성 및 복사**

### 3단계: 권한 설정 (권장)
```bash
# API 키 사용 제한 설정
- IP 주소 제한
- 일일 요청 한도 설정  
- 특정 API만 허용
```

### 4단계: 안전한 저장
```bash
# .env 파일에 저장
echo "GEMINI_API_KEY=your_new_key_here" > .env

# 권한 제한
chmod 600 .env
```

## 🚨 보안 사고 대응

### API 키 노출 발견 시
1. **즉시 조치**
   ```bash
   # 1. Git에서 파일 제거 (이미 커밋된 경우)
   git rm .env
   git commit -m "Remove exposed API key"
   
   # 2. Git 히스토리에서 완전 제거
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   ```

2. **새 API 키 생성**
   - 기존 키 즉시 비활성화
   - 새 키 생성 및 교체
   - 팀원들에게 알림

3. **모니터링 강화**
   - API 사용 로그 확인
   - 비정상적 활동 탐지
   - 알림 설정 강화

## 📞 지원 및 신고

### 보안 취약점 신고
- **이메일**: security@meetingmind.com
- **GitHub Issues**: 🔒 Private로 설정하여 신고

### 추가 리소스
- [Google Cloud 보안 모범 사례](https://cloud.google.com/security/best-practices)
- [OWASP API 보안](https://owasp.org/www-project-api-security/)
- [GitHub 시크릿 관리](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 🛡️ 기억하세요!

> **"API 키는 비밀번호와 같습니다. 절대 공유하거나 공개하지 마세요!"**

- 🔐 **환경변수**로만 관리
- 🚫 **Git에 절대 커밋 금지**
- 🔄 **정기적 키 교체**
- 👥 **팀원과 안전하게 공유**

---

**마지막 업데이트**: 2025년 1월 8일  
**책임자**: MeetingMind 개발팀