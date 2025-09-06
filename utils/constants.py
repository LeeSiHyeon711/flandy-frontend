# Plandy 애플리케이션 상수 정의

# API 관련 상수
API_BASE_URL = "http://127.0.0.1:8000/api"
API_TIMEOUT = 30

# 페이지 관련 상수
PAGE_TITLE = "Plandy - AI 생산성 관리"
PAGE_ICON = "📅"

# 색상 팔레트
COLORS = {
    'primary': '#FF2D20',      # Laravel Red
    'secondary': '#1F2937',    # Dark Gray
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Yellow
    'error': '#EF4444',        # Red
    'info': '#3B82F6',         # Blue
    'light': '#F8FAFC',        # Light Gray
    'dark': '#1F2937',         # Dark Gray
    'muted': '#6B7280'         # Muted Gray
}

# 우선순위 관련 상수
PRIORITY_LEVELS = {
    'low': {
        'label': '낮음',
        'color': '#10B981',
        'emoji': '🟢',
        'order': 1
    },
    'medium': {
        'label': '보통',
        'color': '#F59E0B',
        'emoji': '🟡',
        'order': 2
    },
    'high': {
        'label': '높음',
        'color': '#F97316',
        'emoji': '🟠',
        'order': 3
    },
    'urgent': {
        'label': '긴급',
        'color': '#EF4444',
        'emoji': '🔴',
        'order': 4
    }
}

# 태스크 상태 관련 상수
TASK_STATUS = {
    'pending': {
        'label': '대기',
        'color': '#6B7280',
        'emoji': '⏳',
        'order': 1
    },
    'in_progress': {
        'label': '진행중',
        'color': '#3B82F6',
        'emoji': '🔄',
        'order': 2
    },
    'completed': {
        'label': '완료',
        'color': '#10B981',
        'emoji': '✅',
        'order': 3
    },
    'cancelled': {
        'label': '취소',
        'color': '#EF4444',
        'emoji': '❌',
        'order': 4
    }
}

# 스케줄 상태 관련 상수
SCHEDULE_STATUS = {
    'scheduled': {
        'label': '예정',
        'color': '#3B82F6',
        'emoji': '📅',
        'order': 1
    },
    'in_progress': {
        'label': '진행중',
        'color': '#F59E0B',
        'emoji': '🔄',
        'order': 2
    },
    'completed': {
        'label': '완료',
        'color': '#10B981',
        'emoji': '✅',
        'order': 3
    },
    'cancelled': {
        'label': '취소',
        'color': '#EF4444',
        'emoji': '❌',
        'order': 4
    }
}

# 스케줄 소스 관련 상수
SCHEDULE_SOURCE = {
    'user': {
        'label': '사용자',
        'emoji': '👤'
    },
    'ai': {
        'label': 'AI',
        'emoji': '🤖'
    }
}

# 습관 타입 관련 상수
HABIT_TYPES = [
    '운동',
    '독서',
    '명상',
    '수면',
    '식사',
    '공부',
    '취미',
    '가족시간',
    '친구만남',
    '여행',
    '기타'
]

# 워라밸 점수 관련 상수
WORKLIFE_SCORES = {
    'min_score': 0.0,
    'max_score': 10.0,
    'default_score': 7.0,
    'stress_min': 1,
    'stress_max': 5,
    'satisfaction_min': 1,
    'satisfaction_max': 5
}

# 시간 관련 상수
TIME_CONSTANTS = {
    'default_task_duration_hours': 1,
    'default_schedule_duration_hours': 1,
    'deadline_warning_hours': 24,
    'deadline_urgent_hours': 2
}

# UI 관련 상수
UI_CONSTANTS = {
    'sidebar_width': 300,
    'chart_height': 400,
    'card_padding': '1rem',
    'border_radius': '8px',
    'animation_duration': '0.3s'
}

# 메시지 관련 상수
MESSAGES = {
    'success': {
        'task_created': '태스크가 성공적으로 생성되었습니다!',
        'task_updated': '태스크가 성공적으로 수정되었습니다!',
        'task_deleted': '태스크가 성공적으로 삭제되었습니다!',
        'schedule_created': '일정이 성공적으로 생성되었습니다!',
        'schedule_updated': '일정이 성공적으로 수정되었습니다!',
        'schedule_deleted': '일정이 성공적으로 삭제되었습니다!',
        'score_created': '워라밸 점수가 성공적으로 저장되었습니다!',
        'habit_created': '습관 로그가 성공적으로 저장되었습니다!',
        'login_success': '로그인이 성공적으로 완료되었습니다!',
        'logout_success': '로그아웃이 성공적으로 완료되었습니다!'
    },
    'error': {
        'api_connection': '서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.',
        'authentication_required': '인증이 필요합니다. 다시 로그인해주세요.',
        'invalid_input': '입력한 정보가 올바르지 않습니다.',
        'task_not_found': '태스크를 찾을 수 없습니다.',
        'schedule_not_found': '일정을 찾을 수 없습니다.',
        'login_failed': '로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.',
        'registration_failed': '회원가입에 실패했습니다.',
        'ai_response_failed': 'AI 응답을 받을 수 없습니다. 다시 시도해주세요.'
    },
    'info': {
        'no_tasks': '등록된 태스크가 없습니다.',
        'no_schedules': '등록된 일정이 없습니다.',
        'no_scores': '워라밸 점수 데이터가 없습니다.',
        'no_habits': '등록된 습관이 없습니다.',
        'no_data': '표시할 데이터가 없습니다.',
        'loading': '데이터를 불러오는 중...',
        'processing': '처리 중...'
    }
}

# AI 관련 상수
AI_CONSTANTS = {
    'quick_actions': [
        {
            'label': '태스크 추천',
            'message': '오늘 할 일을 추천해줘',
            'icon': '📋'
        },
        {
            'label': '일정 최적화',
            'message': '내 일정을 최적화해줘',
            'icon': '📅'
        },
        {
            'label': '워라밸 분석',
            'message': '내 워라밸을 분석해줘',
            'icon': '⚖️'
        },
        {
            'label': '생산성 팁',
            'message': '생산성을 높이는 팁을 알려줘',
            'icon': '💡'
        }
    ],
    'context_fields': [
        'current_tasks',
        'today_tasks',
        'pending_tasks',
        'in_progress_tasks',
        'completed_tasks',
        'today_schedule_count',
        'worklife_score',
        'stress_level',
        'today_habits',
        'completed_habits'
    ]
}

# 차트 관련 상수
CHART_CONSTANTS = {
    'colors': [
        '#FF2D20', '#1F2937', '#10B981', '#F59E0B', '#3B82F6',
        '#8B5CF6', '#F97316', '#EF4444', '#06B6D4', '#84CC16'
    ],
    'default_height': 400,
    'default_width': '100%',
    'animation_duration': 1000
}

# 필터 관련 상수
FILTER_CONSTANTS = {
    'date_range_days': 30,
    'max_items_per_page': 50,
    'default_sort_order': 'desc'
}

# 검증 관련 상수
VALIDATION_CONSTANTS = {
    'min_password_length': 6,
    'max_title_length': 255,
    'max_description_length': 1000,
    'max_note_length': 500,
    'email_regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
}

# 개발 관련 상수
DEV_CONSTANTS = {
    'debug_mode': True,
    'log_level': 'INFO',
    'cache_ttl': 300,  # 5분
    'session_timeout': 86400  # 24시간
}
