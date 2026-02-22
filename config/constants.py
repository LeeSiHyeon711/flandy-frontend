"""
상수 정의
앱에서 사용하는 상수들을 정의
"""

# 다크 테마 팔레트
THEME_DARK = {
    "bg_primary": "#0F172A",
    "bg_secondary": "#1E293B",
    "bg_tertiary": "#334155",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "accent": "#3B82F6",
    "accent_hover": "#2563EB",
    "border": "#334155",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#3B82F6",
}

# 라이트 테마 팔레트
THEME_LIGHT = {
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F1F5F9",
    "bg_tertiary": "#E2E8F0",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "border": "#CBD5E1",
    "success": "#16A34A",
    "warning": "#D97706",
    "danger": "#DC2626",
    "info": "#2563EB",
}

# 하위 호환 alias
COLORS = THEME_DARK

# 상태별 색상 (테마 불변)
STATUS_COLORS = {
    "pending": "#94A3B8",
    "in_progress": "#3B82F6",
    "completed": "#22C55E",
    "cancelled": "#EF4444",
}

# 우선순위 색상 (테마 불변)
PRIORITY_COLORS = {
    "low": "#10B981",
    "medium": "#F59E0B",
    "high": "#F97316",
    "urgent": "#EF4444",
}

# 카테고리 색상 (테마 불변)
CATEGORY_COLORS = {
    "업무": "#3B82F6",
    "휴식": "#22C55E",
    "개인": "#F59E0B",
    "운동": "#06B6D4",
    "학습": "#8B5CF6",
    "기타": "#64748B",
}

# 차트 설정
CHART_WIDTH = 600
CHART_HEIGHT = 600

# 사이드바 설정
SIDEBAR_WIDTH = 300
LOGO_WIDTH = 180

# 자동 새로고침 간격 (초)
AUTO_REFRESH_INTERVAL = 5
