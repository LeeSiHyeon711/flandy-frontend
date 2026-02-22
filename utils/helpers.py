from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import streamlit as st

def format_datetime(dt_string: str) -> str:
    """ISO 형식의 날짜시간 문자열을 한국어 형식으로 변환"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_string

def format_date(date_string: str) -> str:
    """ISO 형식의 날짜 문자열을 한국어 형식으로 변환"""
    try:
        d = datetime.fromisoformat(date_string).date()
        return d.strftime('%Y년 %m월 %d일')
    except:
        return date_string

def get_priority_color(priority: str) -> str:
    """우선순위에 따른 색상 반환"""
    colors = {
        'low': '#10B981',
        'medium': '#F59E0B', 
        'high': '#F97316',
        'urgent': '#EF4444'
    }
    return colors.get(priority, '#6B7280')

def get_status_color(status: str) -> str:
    """상태에 따른 색상 반환"""
    colors = {
        'pending': '#6B7280',
        'in_progress': '#3B82F6',
        'completed': '#10B981',
        'cancelled': '#EF4444'
    }
    return colors.get(status, '#6B7280')

def get_priority_emoji(priority: str) -> str:
    """우선순위에 따른 이모지 반환"""
    emojis = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🟠', 
        'urgent': '🔴'
    }
    return emojis.get(priority, '⚪')

def get_status_emoji(status: str) -> str:
    """상태에 따른 이모지 반환"""
    emojis = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅',
        'cancelled': '❌'
    }
    return emojis.get(status, '📝')

def is_deadline_urgent(deadline: str) -> bool:
    """마감일이 임박했는지 확인 (24시간 이내)"""
    try:
        deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        now = datetime.now()
        time_diff = deadline_dt - now
        return 0 < time_diff.total_seconds() <= 86400  # 24시간
    except:
        return False

def is_deadline_overdue(deadline: str) -> bool:
    """마감일이 지났는지 확인"""
    try:
        deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        now = datetime.now()
        return deadline_dt < now
    except:
        return False

def get_week_start(date_obj: date) -> date:
    """주어진 날짜의 주 시작일(월요일) 반환"""
    return date_obj - timedelta(days=date_obj.weekday())

def get_week_end(date_obj: date) -> date:
    """주어진 날짜의 주 종료일(일요일) 반환"""
    return date_obj + timedelta(days=6 - date_obj.weekday())

def calculate_completion_rate(tasks: List[Dict]) -> float:
    """태스크 완료율 계산"""
    if not tasks:
        return 0.0
    
    completed = len([t for t in tasks if t.get('status') == 'completed'])
    return (completed / len(tasks)) * 100

def get_task_statistics(tasks: List[Dict]) -> Dict[str, int]:
    """태스크 통계 반환"""
    stats = {
        'total': len(tasks),
        'pending': 0,
        'in_progress': 0,
        'completed': 0,
        'cancelled': 0
    }
    
    for task in tasks:
        status = task.get('status', 'pending')
        if status in stats:
            stats[status] += 1
    
    return stats

def filter_tasks_by_priority(tasks: List[Dict], priority: str) -> List[Dict]:
    """우선순위별 태스크 필터링"""
    if priority == "전체":
        return tasks
    return [t for t in tasks if t.get('priority') == priority]

def filter_tasks_by_status(tasks: List[Dict], status: str) -> List[Dict]:
    """상태별 태스크 필터링"""
    if status == "전체":
        return tasks
    return [t for t in tasks if t.get('status') == status]

def sort_tasks_by_priority(tasks: List[Dict]) -> List[Dict]:
    """우선순위별 태스크 정렬"""
    priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
    return sorted(tasks, key=lambda x: priority_order.get(x.get('priority', 'medium'), 2), reverse=True)

def sort_tasks_by_deadline(tasks: List[Dict]) -> List[Dict]:
    """마감일별 태스크 정렬"""
    return sorted(tasks, key=lambda x: x.get('deadline', ''), reverse=False)

def get_habit_completion_rate(habits: List[Dict]) -> float:
    """습관 완료율 계산"""
    if not habits:
        return 0.0
    
    completed = len([h for h in habits if h.get('completed')])
    return (completed / len(habits)) * 100

def get_worklife_score_trend(scores: List[Dict], field: str) -> float:
    """워라밸 점수 트렌드 계산 (최근 2주 비교)"""
    if len(scores) < 2:
        return 0.0
    
    current = scores[0].get(field, 0)
    previous = scores[1].get(field, 0)
    return current - previous

def format_duration(start_time: str, end_time: str) -> str:
    """시작시간과 종료시간으로부터 지속시간 계산"""
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration = end - start
        
        hours = duration.total_seconds() // 3600
        minutes = (duration.total_seconds() % 3600) // 60
        
        if hours > 0:
            return f"{int(hours)}시간 {int(minutes)}분"
        else:
            return f"{int(minutes)}분"
    except:
        return "시간 계산 오류"

def get_time_of_day_emoji(hour: int) -> str:
    """시간대에 따른 이모지 반환"""
    if 5 <= hour < 12:
        return "🌅"  # 아침
    elif 12 <= hour < 17:
        return "☀️"  # 오후
    elif 17 <= hour < 21:
        return "🌆"  # 저녁
    else:
        return "🌙"  # 밤

def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """비밀번호 강도 검증"""
    result = {
        'valid': True,
        'errors': [],
        'strength': 'weak'
    }
    
    if len(password) < 6:
        result['valid'] = False
        result['errors'].append('비밀번호는 6자 이상이어야 합니다.')
    
    if not any(c.isupper() for c in password):
        result['strength'] = 'medium'
    
    if not any(c.islower() for c in password):
        result['strength'] = 'medium'
    
    if not any(c.isdigit() for c in password):
        result['strength'] = 'medium'
    
    if any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password):
        result['strength'] = 'strong'
    
    return result

def show_success_message(message: str):
    """성공 메시지 표시"""
    st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)

def show_error_message(message: str):
    """에러 메시지 표시"""
    st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)

def show_warning_message(message: str):
    """경고 메시지 표시"""
    st.warning(f"⚠️ {message}")

def show_info_message(message: str):
    """정보 메시지 표시"""
    st.info(f"ℹ️ {message}")

def clear_session_state():
    """세션 상태 초기화"""
    keys_to_clear = [
        'show_task_form', 'edit_task_id',
        'show_schedule_form', 'edit_schedule_id',
        'show_score_form', 'show_habit_form',
        'chat_history'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_user_timezone():
    """사용자 시간대 반환"""
    return "Asia/Seoul"  # 기본값

def format_relative_time(dt_string: str) -> str:
    """상대적 시간 표시 (예: 2시간 전, 3일 전)"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 전"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"
    except:
        return dt_string
