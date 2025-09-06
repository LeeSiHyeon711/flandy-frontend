import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from components.api_client import PlandyAPIClient
import plotly.express as px
import plotly.graph_objects as go

def show_schedule():
    """스케줄 관리 페이지 표시"""
    st.header("📅 스케줄 관리")
    
    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)
    
    # 뷰 선택
    view_type = st.radio(
        "뷰 선택",
        ["주간 뷰", "일간 뷰", "목록 뷰"],
        horizontal=True,
        key="schedule_view"
    )
    
    # 날짜 선택
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if view_type == "주간 뷰":
            selected_date = st.date_input(
                "주 선택",
                value=date.today(),
                key="week_date"
            )
            # 주의 시작일 계산 (월요일)
            week_start = selected_date - timedelta(days=selected_date.weekday())
            week_end = week_start + timedelta(days=6)
            st.caption(f"📅 {week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}")
        else:
            selected_date = st.date_input(
                "날짜 선택",
                value=date.today(),
                key="day_date"
            )
    
    # 새 일정 추가 버튼
    if st.button("➕ 새 일정 추가", use_container_width=True):
        st.session_state.show_schedule_form = True
    
    # 스케줄 데이터 로딩
    with st.spinner("일정을 불러오는 중..."):
        if view_type == "주간 뷰":
            start_date = week_start.isoformat()
            end_date = week_end.isoformat()
            schedules = api_client.get_schedule(start_date=start_date, end_date=end_date)
        else:
            schedules = api_client.get_schedule_by_date(selected_date.isoformat())
    
    # 뷰에 따른 표시
    if view_type == "주간 뷰":
        show_week_view(schedules, week_start, api_client)
    elif view_type == "일간 뷰":
        show_day_view(schedules, selected_date, api_client)
    else:
        show_list_view(schedules, api_client)
    
    # 새 일정 폼
    if st.session_state.get('show_schedule_form'):
        show_schedule_form(api_client, selected_date if view_type != "주간 뷰" else date.today())

def show_week_view(schedules, week_start, api_client):
    """주간 뷰 표시"""
    st.subheader("📅 주간 스케줄")
    
    # 주간 데이터를 일별로 그룹화
    week_schedules = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        week_schedules[day] = []
    
    for schedule in schedules:
        try:
            start_time = datetime.fromisoformat(schedule.get('start_time', '').replace('Z', '+00:00'))
            schedule_date = start_time.date()
            if schedule_date in week_schedules:
                week_schedules[schedule_date].append(schedule)
        except:
            continue
    
    # 주간 캘린더 표시
    days = ['월', '화', '수', '목', '금', '토', '일']
    cols = st.columns(7)
    
    for i, (day_date, day_schedules) in enumerate(week_schedules.items()):
        with cols[i]:
            # 날짜 헤더
            is_today = day_date == date.today()
            header_style = "background-color: #FF2D20; color: white;" if is_today else ""
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; {header_style} border-radius: 4px; margin-bottom: 0.5rem;">
                <strong>{days[i]}</strong><br>
                <small>{day_date.strftime('%m/%d')}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # 해당 날짜의 일정들
            for schedule in day_schedules:
                show_schedule_card(schedule, api_client, compact=True)

def show_day_view(schedules, selected_date, api_client):
    """일간 뷰 표시"""
    st.subheader(f"📅 {selected_date.strftime('%Y년 %m월 %d일')} 일정")
    
    if schedules:
        # 시간순 정렬
        schedules.sort(key=lambda x: x.get('start_time', ''))
        
        # 시간대별 그룹화
        time_slots = {}
        for schedule in schedules:
            try:
                start_time = datetime.fromisoformat(schedule.get('start_time', '').replace('Z', '+00:00'))
                hour = start_time.hour
                if hour not in time_slots:
                    time_slots[hour] = []
                time_slots[hour].append(schedule)
            except:
                continue
        
        # 시간대별 표시
        for hour in sorted(time_slots.keys()):
            st.markdown(f"### 🕐 {hour:02d}:00")
            for schedule in time_slots[hour]:
                show_schedule_card(schedule, api_client)
    else:
        st.info("이 날짜에는 등록된 일정이 없습니다.")

def show_list_view(schedules, api_client):
    """목록 뷰 표시"""
    st.subheader("📋 일정 목록")
    
    if schedules:
        # 날짜순 정렬
        schedules.sort(key=lambda x: x.get('start_time', ''))
        
        # 필터 옵션
        col1, col2 = st.columns(2)
        with col1:
            state_filter = st.selectbox(
                "상태 필터",
                ["전체", "scheduled", "in_progress", "completed", "cancelled"],
                key="state_filter"
            )
        with col2:
            source_filter = st.selectbox(
                "소스 필터",
                ["전체", "user", "ai"],
                key="source_filter"
            )
        
        # 필터 적용
        filtered_schedules = schedules
        if state_filter != "전체":
            filtered_schedules = [s for s in filtered_schedules if s.get('state') == state_filter]
        if source_filter != "전체":
            filtered_schedules = [s for s in filtered_schedules if s.get('source') == source_filter]
        
        # 일정 카드들 표시
        for schedule in filtered_schedules:
            show_schedule_card(schedule, api_client)
    else:
        st.info("등록된 일정이 없습니다.")

def show_schedule_card(schedule, api_client, compact=False):
    """일정 카드 표시"""
    schedule_id = schedule.get('id')
    title = schedule.get('title', '제목 없음')
    description = schedule.get('description', '')
    start_time = schedule.get('start_time', '')
    end_time = schedule.get('end_time', '')
    state = schedule.get('state', 'scheduled')
    source = schedule.get('source', 'user')
    task_id = schedule.get('task_id')
    
    # 시간 처리
    time_str = "시간 미정"
    if start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            time_str = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
            date_str = start_dt.strftime('%Y-%m-%d')
        except:
            time_str = "시간 오류"
            date_str = ""
    else:
        date_str = ""
    
    # 상태별 스타일
    state_info = {
        'scheduled': {'emoji': '📅', 'color': '#3B82F6'},
        'in_progress': {'emoji': '🔄', 'color': '#F59E0B'},
        'completed': {'emoji': '✅', 'color': '#10B981'},
        'cancelled': {'emoji': '❌', 'color': '#EF4444'}
    }
    
    # 소스별 아이콘
    source_emoji = "👤" if source == "user" else "🤖"
    
    state_emoji = state_info.get(state, {}).get('emoji', '📅')
    state_color = state_info.get(state, {}).get('color', '#3B82F6')
    
    if compact:
        # 컴팩트 모드 (주간 뷰용)
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 4px; 
                    padding: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid {state_color};">
            <div style="font-size: 0.8rem; font-weight: bold; color: #1F2937;">{state_emoji} {title}</div>
            <div style="font-size: 0.7rem; color: #6B7280;">{time_str}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 일반 모드
        with st.container():
            st.markdown(f"""
            <div class="task-card" style="border-left: 4px solid {state_color}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #1F2937;">{state_emoji} {title}</h4>
                        <p style="margin: 0.5rem 0; color: #6B7280; font-size: 0.9rem;">{description}</p>
                        <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: #6B7280;">
                            <span>⏰ {time_str}</span>
                            <span>📅 {date_str}</span>
                            <span>{source_emoji} {source}</span>
                            {f'<span>🔗 태스크 #{task_id}</span>' if task_id else ''}
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
            """, unsafe_allow_html=True)
            
            # 액션 버튼들
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✏️", key=f"edit_schedule_{schedule_id}", help="수정"):
                    st.session_state.edit_schedule_id = schedule_id
                    st.session_state.show_schedule_form = True
                    st.rerun()
            
            with col2:
                if state != 'completed':
                    if st.button("✅", key=f"complete_schedule_{schedule_id}", help="완료"):
                        if api_client.update_schedule(schedule_id, state='completed'):
                            st.success("일정이 완료되었습니다!")
                            st.rerun()
                        else:
                            st.error("일정 완료 처리에 실패했습니다.")
            
            with col3:
                if st.button("🗑️", key=f"delete_schedule_{schedule_id}", help="삭제"):
                    if api_client.delete_schedule(schedule_id):
                        st.success("일정이 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("일정 삭제에 실패했습니다.")
            
            st.markdown("</div></div></div>", unsafe_allow_html=True)
            st.markdown("---")

def show_schedule_form(api_client, default_date=None):
    """일정 생성/수정 폼"""
    st.markdown("---")
    
    # 수정 모드인지 확인
    is_edit = 'edit_schedule_id' in st.session_state
    schedule_id = st.session_state.get('edit_schedule_id')
    
    if is_edit:
        st.subheader("✏️ 일정 수정")
        # 기존 일정 데이터 로드
        schedules = api_client.get_schedule()
        schedule_data = next((s for s in schedules if s.get('id') == schedule_id), {})
    else:
        st.subheader("➕ 새 일정 추가")
        schedule_data = {}
    
    with st.form("schedule_form"):
        title = st.text_input(
            "일정 제목 *",
            value=schedule_data.get('title', ''),
            placeholder="일정을 입력하세요"
        )
        
        description = st.text_area(
            "설명",
            value=schedule_data.get('description', ''),
            placeholder="상세 설명을 입력하세요"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            schedule_date = st.date_input(
                "날짜",
                value=default_date or date.today()
            )
        with col2:
            state = st.selectbox(
                "상태",
                ["scheduled", "in_progress", "completed", "cancelled"],
                index=["scheduled", "in_progress", "completed", "cancelled"].index(schedule_data.get('state', 'scheduled'))
            )
        
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input(
                "시작 시간",
                value=datetime.fromisoformat(schedule_data.get('start_time', '')).time() if schedule_data.get('start_time') else datetime.now().time()
            )
        with col2:
            end_time = st.time_input(
                "종료 시간",
                value=datetime.fromisoformat(schedule_data.get('end_time', '')).time() if schedule_data.get('end_time') else (datetime.now() + timedelta(hours=1)).time()
            )
        
        # 태스크 연결 (선택사항)
        tasks = api_client.get_tasks()
        task_options = ["연결 안함"] + [f"{task.get('title', '제목 없음')} (ID: {task.get('id')})" for task in tasks]
        
        selected_task = st.selectbox(
            "연결할 태스크 (선택사항)",
            task_options,
            index=0
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit = st.form_submit_button("저장", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("취소", use_container_width=True)
        
        if submit and title:
            # 태스크 ID 추출
            task_id = None
            if selected_task != "연결 안함":
                try:
                    task_id = int(selected_task.split("ID: ")[1].split(")")[0])
                except:
                    pass
            
            # 날짜와 시간 결합
            start_datetime = datetime.combine(schedule_date, start_time)
            end_datetime = datetime.combine(schedule_date, end_time)
            
            if is_edit:
                # 수정
                if api_client.update_schedule(
                    schedule_id,
                    title=title,
                    description=description,
                    start_time=start_datetime.isoformat(),
                    end_time=end_datetime.isoformat(),
                    state=state,
                    task_id=task_id
                ):
                    st.success("일정이 수정되었습니다!")
                    st.session_state.show_schedule_form = False
                    if 'edit_schedule_id' in st.session_state:
                        del st.session_state.edit_schedule_id
                    st.rerun()
                else:
                    st.error("일정 수정에 실패했습니다.")
            else:
                # 생성
                if api_client.create_schedule(
                    title=title,
                    description=description,
                    start_time=start_datetime.isoformat(),
                    end_time=end_datetime.isoformat(),
                    task_id=task_id
                ):
                    st.success("일정이 추가되었습니다!")
                    st.session_state.show_schedule_form = False
                    st.rerun()
                else:
                    st.error("일정 추가에 실패했습니다.")
        
        if cancel:
            st.session_state.show_schedule_form = False
            if 'edit_schedule_id' in st.session_state:
                del st.session_state.edit_schedule_id
            st.rerun()
