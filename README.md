# 🎯 Plandy Frontend

> **"계획은 유연하게, 하루는 완벽하게!"**

직장인을 위한 AI 일정·워라벨 관리 비서의 프론트엔드 대시보드입니다.

## 📋 프로젝트 개요

Plandy는 단순한 캘린더가 아닌, 상황에 따라 **실시간으로 일정을 재조정**하고 **워라벨 지표**까지 챙겨주는 AI 비서입니다.

### 🎯 핵심 기능

- 📅 **일정 자동화**: 사용자 입력 → 마감·제약조건 반영해 일정 배치
- 🔄 **실시간 재조정**: "나 지금 10시에 일어났어" → 일정 싹 재배치
- 📊 **시각화**: 생활계획표 느낌의 원형 다이어그램 + 텍스트 일정표
- 🔔 **알림**: SMTP, SSE 기반 리마인더 전송
- ⚖️ **워라벨 점수**: 업무/휴식 균형 수치화, 주간 레벨 제공
- 🚬 **습관 기록**: 흡연/커피 횟수 기록, 효율·스트레스 관리 코칭

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
streamlit run src/app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📁 프로젝트 구조

```
flandy-frontend/
├── src/                    # 메인 애플리케이션 코드
│   ├── app.py             # Streamlit 메인 앱
│   ├── dashboard.py       # 대시보드 페이지
│   └── components/        # 재사용 가능한 컴포넌트
├── pages/                 # Streamlit 멀티페이지
│   ├── schedule.py        # 일정 관리 페이지
│   ├── worklife.py        # 워라벨 관리 페이지
│   └── habits.py          # 습관 관리 페이지
├── components/            # UI 컴포넌트
│   ├── schedule_chart.py  # 일정 차트 컴포넌트
│   ├── worklife_score.py  # 워라벨 점수 컴포넌트
│   └── habit_tracker.py   # 습관 추적 컴포넌트
├── utils/                 # 유틸리티 함수
│   ├── time_utils.py      # 시간 관련 유틸리티
│   ├── data_utils.py      # 데이터 처리 유틸리티
│   └── api_client.py      # API 클라이언트
├── config/                # 설정 파일
│   ├── settings.py        # 앱 설정
│   └── constants.py       # 상수 정의
├── assets/                # 정적 자산
│   ├── images/            # 이미지 파일
│   └── styles/            # CSS 스타일
├── data/                  # 데이터 파일
│   ├── sample_data.json   # 샘플 데이터
│   └── user_data/         # 사용자 데이터
├── requirements.txt       # Python 의존성
└── README.md             # 프로젝트 문서
```

## 🛠️ 개발 가이드

### 코드 스타일

- **함수 주석**: 입력/출력/상위 로직 영향까지 기록
- **변수명**: 명확하고 의미있는 이름 사용
- **구조**: 모듈화된 컴포넌트 구조 유지

### 확장성

- **카테고리 추가**: 새로운 기능을 플러그인처럼 쉽게 확장
- **Tool 인터페이스**: 추상화된 Tool 구조로 확장성 보장

## 🎨 UI/UX 특징

- **원형 다이어그램**: 생활계획표 느낌의 시각화
- **실시간 업데이트**: 일정 변경 시 즉시 반영
- **반응형 디자인**: 다양한 화면 크기 지원
- **직관적 인터페이스**: 직장인 친화적 UI

## 🔧 기술 스택

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Styling**: Custom CSS
- **State Management**: Streamlit Session State

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Plandy는 단순 캘린더가 아니라, 직장인의 워라벨을 챙겨주는 AI 코치입니다.** 🚀
