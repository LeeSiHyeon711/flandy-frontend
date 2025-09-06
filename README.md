# Plandy Frontend - Streamlit 기반 AI 생산성 관리 시스템

![Plandy Logo](assets/plandy-logo.png)

## 📋 프로젝트 개요

Plandy는 AI 기반 개인 생산성 관리 서비스의 Streamlit 프론트엔드입니다. Laravel 백엔드와 연동하여 태스크 관리, 스케줄 관리, 워라밸 분석, AI 어시스턴트 기능을 제공합니다.

## 🚀 빠른 시작

### 1. 백엔드 서버 실행

먼저 Laravel 백엔드 서버가 실행되어 있어야 합니다:

```bash
# 백엔드 디렉토리로 이동
cd ../plandy-backend

# 서버 실행
php artisan serve --host=127.0.0.1 --port=8000
```

### 2. 프론트엔드 실행

```bash
# 패키지 설치
pip install -r requirements.txt

# 애플리케이션 실행
python run.py
```

또는 직접 Streamlit으로 실행:

```bash
streamlit run src/app.py --server.port 8501
```

### 3. 브라우저에서 접속

http://127.0.0.1:8501 에서 애플리케이션에 접속할 수 있습니다.

## 🧪 테스트 계정

다음 테스트 계정으로 로그인할 수 있습니다:

| 이메일 | 비밀번호 | 이름 |
|--------|----------|------|
| kim@plandy.kr | **password123** | 김철수 |
| lee@plandy.kr | **password123** | 이영희 |
| park@plandy.kr | **password123** | 박민수 |
| choi@plandy.kr | **password123** | 최지영 |
| jung@plandy.kr | **password123** | 정현우 |

## 📁 프로젝트 구조

```
plandy-frontend/
├── src/
│   └── app.py                 # 메인 애플리케이션
├── components/
│   ├── api_client.py         # API 클라이언트
│   ├── auth.py               # 인증 시스템
│   └── sidebar.py            # 사이드바 네비게이션
├── pages/
│   ├── dashboard.py          # 대시보드
│   ├── tasks.py              # 태스크 관리
│   ├── schedule.py           # 스케줄 관리
│   ├── worklife.py           # 워라밸 분석
│   └── ai_assistant.py       # AI 어시스턴트
├── utils/
│   ├── helpers.py            # 유틸리티 함수
│   └── constants.py          # 상수 정의
├── requirements.txt          # Python 패키지 의존성
├── run.py                    # 실행 스크립트
└── README.md                 # 이 파일
```

## 🎯 주요 기능

### 1. 대시보드
- 오늘의 태스크 및 일정 개요
- 워라밸 점수 및 습관 달성률
- 빠른 액션 버튼
- 시각적 차트 및 통계

### 2. 태스크 관리
- 태스크 CRUD 기능
- 우선순위 및 상태 관리
- 필터링 및 검색
- 마감일 관리

### 3. 스케줄 관리
- 주간/일간/목록 뷰
- 일정 CRUD 기능
- 태스크와 일정 연동
- 시간 충돌 검사

### 4. 워라밸 분석
- 워라밸 점수 입력 및 분석
- 습관 추적 및 관리
- 트렌드 분석 및 시각화
- AI 기반 개선 제안

### 5. AI 어시스턴트
- 실시간 채팅 인터페이스
- 컨텍스트 기반 추천
- 빠른 액션 버튼
- 개인화된 생산성 팁

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Backend**: Laravel (API)
- **Database**: MySQL
- **Visualization**: Plotly
- **HTTP Client**: Requests
- **Data Processing**: Pandas

## 📊 API 연동

프론트엔드는 다음 API 엔드포인트와 연동됩니다:

- **인증 API**: 로그인, 회원가입, 로그아웃
- **태스크 API**: CRUD, 필터링, 상태 관리
- **스케줄 API**: CRUD, 날짜별 조회
- **워라밸 API**: 점수 관리, 습관 추적
- **AI API**: 채팅, 분석, 추천

## 🎨 UI/UX 특징

- **반응형 디자인**: 다양한 화면 크기 지원
- **직관적 네비게이션**: 사이드바 기반 메뉴
- **시각적 피드백**: 색상 코딩 및 이모지 활용
- **실시간 업데이트**: 데이터 변경 시 즉시 반영
- **에러 처리**: 사용자 친화적 오류 메시지

## 🔧 개발 환경 설정

### 필수 요구사항
- Python 3.8+
- Streamlit 1.28.0+
- Laravel 백엔드 서버 실행 중

### 개발 도구
- VS Code (권장)
- Python 확장
- Streamlit 확장

### 디버깅
```bash
# 개발 모드로 실행
streamlit run src/app.py --server.port 8501 --logger.level debug
```

## 📝 사용법

### 1. 로그인
- 테스트 계정 또는 새 계정으로 로그인
- 데모 계정 버튼으로 빠른 로그인 가능

### 2. 대시보드
- 오늘의 할 일과 일정을 한눈에 확인
- 빠른 액션으로 새 태스크/일정 추가

### 3. 태스크 관리
- 필터와 검색으로 원하는 태스크 찾기
- 드래그 앤 드롭으로 우선순위 조정
- 상태 변경으로 진행 상황 관리

### 4. 스케줄 관리
- 주간/일간 뷰로 일정 확인
- 시간 충돌 방지를 위한 시각적 표시
- 태스크와 일정 연동

### 5. 워라밸 분석
- 주간 점수 입력으로 워라밸 추적
- 습관 달성률 모니터링
- AI 분석으로 개선점 파악

### 6. AI 어시스턴트
- 자연어로 생산성 관련 질문
- 컨텍스트 기반 개인화된 추천
- 빠른 액션으로 자주 사용하는 기능 접근

## 🐛 문제 해결

### 백엔드 연결 오류
```bash
# 백엔드 서버 상태 확인
curl http://127.0.0.1:8000/api/health

# Laravel 서버 재시작
cd ../plandy-backend
php artisan serve --host=127.0.0.1 --port=8000
```

### 패키지 설치 오류
```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 재설치
pip install -r requirements.txt
```

### 포트 충돌
```bash
# 다른 포트로 실행
streamlit run src/app.py --server.port 8502
```

## 🤝 기여하기

1. 이슈 생성 또는 기존 이슈 확인
2. 기능 브랜치 생성
3. 코드 작성 및 테스트
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.

---

**Plandy** - AI와 함께하는 스마트한 생산성 관리 🚀