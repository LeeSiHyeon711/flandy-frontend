"""
Plandy 애플리케이션 상수 정의
"""

# 애플리케이션 정보
APP_NAME = "Plandy"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI 일정·워라벨 관리 비서"

# 메시지
MESSAGES = {
    "welcome": "🎯 Plandy에 오신 것을 환영합니다!",
    "schedule_updated": "일정이 성공적으로 업데이트되었습니다.",
    "schedule_rescheduled": "일정이 재조정되었습니다!",
    "data_saved": "데이터가 저장되었습니다!",
    "error_generic": "오류가 발생했습니다. 다시 시도해주세요.",
    "feature_coming_soon": "이 기능은 곧 출시될 예정입니다."
}

# 워라벨 점수 기준
WORKLIFE_SCORE_THRESHOLDS = {
    "excellent": 90,
    "good": 80,
    "fair": 70,
    "poor": 60,
    "critical": 50
}

# 워라벨 점수 메시지
WORKLIFE_MESSAGES = {
    "excellent": "🎉 완벽한 워라벨 균형입니다!",
    "good": "👍 좋은 워라벨 균형을 유지하고 있습니다.",
    "fair": "⚠️ 워라벨 균형을 조금 더 신경써보세요.",
    "poor": "😰 워라벨 균형이 좋지 않습니다. 휴식을 더 취하세요.",
    "critical": "🚨 워라벨 균형이 심각합니다. 즉시 휴식이 필요합니다."
}

# 일정 카테고리
SCHEDULE_CATEGORIES = [
    "업무",
    "휴식",
    "개인",
    "운동",
    "학습",
    "기타"
]

# 습관 카테고리
HABIT_CATEGORIES = [
    "흡연",
    "커피",
    "물 마시기",
    "운동",
    "독서",
    "명상"
]

# 시간 단위
TIME_UNITS = {
    "minutes": "분",
    "hours": "시간",
    "days": "일"
}

# 요일
WEEKDAYS = [
    "월요일",
    "화요일", 
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

# 월
MONTHS = [
    "1월", "2월", "3월", "4월", "5월", "6월",
    "7월", "8월", "9월", "10월", "11월", "12월"
]

# 우선순위
PRIORITIES = {
    "high": "높음",
    "medium": "보통", 
    "low": "낮음"
}

# 상태
STATUS = {
    "pending": "대기",
    "in_progress": "진행중",
    "completed": "완료",
    "cancelled": "취소"
}

# 파일 확장자
ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "document": [".pdf", ".doc", ".docx", ".txt"],
    "data": [".json", ".csv", ".xlsx", ".xls"]
}

# 최대 파일 크기 (MB)
MAX_FILE_SIZE = {
    "image": 5,
    "document": 10,
    "data": 2
}
