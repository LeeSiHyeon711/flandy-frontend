"""
상수 정의
앱에서 사용하는 상수들을 정의
"""

# 색상 팔레트 (플랜디 테마)
COLOR_MAP = {
    "업무": "#4A90E2",      # 플랜디 메인 블루
    "휴식": "#6BCF7F",      # 플랜디 블루와 조화되는 그린
    "개인": "#FF8A65",      # 플랜디 블루와 조화되는 오렌지
    "운동": "#4FC3F7",      # 플랜디 블루 계열 라이트 블루
    "학습": "#81C784",      # 플랜디 블루와 조화되는 라이트 그린
    "기타": "#B0BEC5"       # 플랜디 블루와 조화되는 그레이
}

# 워라벨 점수 기준
IDEAL_WORK_RATIO = 0.6
IDEAL_REST_RATIO = 0.4

# 차트 설정
CHART_WIDTH = 600
CHART_HEIGHT = 600
GAUGE_HEIGHT = 250
PIE_HEIGHT = 250

# 사이드바 설정
SIDEBAR_WIDTH = 300
LOGO_WIDTH = 180

# 자동 새로고침 간격 (초)
AUTO_REFRESH_INTERVAL = 5

# 대화방 목록
CONVERSATIONS = [
    {"name": "📅 일정 관리", "last_msg": "오늘 일정을 확인해주세요", "clicked": True},
    {"name": "⚖️ 워라벨 상담", "last_msg": "워라벨 점수를 개선해보세요", "clicked": False},
    {"name": "🎯 목표 설정", "last_msg": "이번 주 목표를 설정해보세요", "clicked": False},
    {"name": "📊 분석 리포트", "last_msg": "주간 리포트를 확인하세요", "clicked": False}
]