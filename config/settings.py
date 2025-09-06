"""
Plandy 애플리케이션 설정
"""

import os
from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Streamlit 설정
STREAMLIT_CONFIG = {
    "page_title": "Plandy - AI 일정 관리 비서",
    "page_icon": "🎯",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 색상 테마
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff7f0e",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# 카테고리별 색상
CATEGORY_COLORS = {
    "업무": "#ff6b6b",
    "휴식": "#4ecdc4",
    "개인": "#45b7d1",
    "운동": "#96ceb4",
    "학습": "#feca57",
    "기타": "#cccccc"
}

# 시간 설정
TIME_SETTINGS = {
    "work_start": "09:00",
    "work_end": "18:00",
    "lunch_start": "12:00",
    "lunch_end": "13:00",
    "break_duration": 15,  # 분
    "meeting_buffer": 5    # 분
}

# 워라벨 설정
WORKLIFE_SETTINGS = {
    "ideal_work_ratio": 0.6,
    "ideal_rest_ratio": 0.4,
    "max_work_hours": 8,
    "min_break_hours": 1
}

# 알림 설정
NOTIFICATION_SETTINGS = {
    "enabled": True,
    "advance_minutes": 15,
    "sound_enabled": False
}

# 데이터베이스 설정 (향후 확장용)
DATABASE_SETTINGS = {
    "type": "sqlite",
    "path": DATA_DIR / "plandy.db"
}

# API 설정 (향후 백엔드 연동용)
API_SETTINGS = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retry_count": 3
}
