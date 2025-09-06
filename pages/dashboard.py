import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from components.api_client import PlandyAPIClient
from components.auth import get_current_user
import plotly.express as px
import plotly.graph_objects as go

def show_dashboard():
    """대시보드 페이지 표시"""
    st.header("📊 대시보드")
    
    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)
    
    # 오늘 날짜
    today = date.today()
    today_str = today.isoformat()
    
    # 데이터 로딩
    with st.spinner("데이터를 불러오는 중..."):
        # 오늘의 태스크
        today_tasks = api_client.get_tasks(date=today_str)
        
        # 오늘의 스케줄
        today_schedule = api_client.get_schedule_by_date(today_str)
        
        # 최근 워라밸 점수
        worklife_scores = api_client.get_worklife_scores()
        
        # 오늘의 습관 로그
        today_habits = api_client.get_habit_logs(date=today_str)
    
    # 메트릭 카드들
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pending_tasks = len([task for task in today_tasks if task.get('status') == 'pending'])
        in_progress_tasks = len([task for task in today_tasks if task.get('status') == 'in_progress'])
        completed_tasks = len([task for task in today_tasks if task.get('status') == 'completed'])
        
        st.metric(
            label="📋 오늘의 태스크",
            value=f"{completed_tasks}/{len(today_tasks)}",
            delta=f"진행중: {in_progress_tasks}"
        )
    
    with col2:
        st.metric(
            label="📅 오늘의 일정",
            value=len(today_schedule),
            delta="개"
        )
    
    with col3:
        if worklife_scores:
            latest_score = worklife_scores[0]
            st.metric(
                label="⚖️ 워라밸 점수",
                value=f"{latest_score.get('overall_score', 0):.1f}",
                delta=f"스트레스: {latest_score.get('stress_level', 0)}"
            )
        else:
            st.metric(
                label="⚖️ 워라밸 점수",
                value="N/A",
                delta="데이터 없음"
            )
    
    with col4:
        completed_habits = len([habit for habit in today_habits if habit.get('completed')])
        total_habits = len(today_habits)
        st.metric(
            label="🎯 습관 달성",
            value=f"{completed_habits}/{total_habits}",
            delta="개"
        )
    
    st.markdown("---")
    
    # 메인 콘텐츠 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 오늘의 태스크
        st.subheader("📋 오늘의 태스크")
        if today_tasks:
            for task in today_tasks:
                with st.container():
                    status_emoji = {
                        'pending': '⏳',
                        'in_progress': '🔄',
                        'completed': '✅',
                        'cancelled': '❌'
                    }.get(task.get('status'), '📝')
                    
                    priority_color = {
                        'low': '🟢',
                        'medium': '🟡',
                        'high': '🟠',
                        'urgent': '🔴'
                    }.get(task.get('priority'), '⚪')
                    
                    st.markdown(f"""
                    <div class="task-card">
                        <strong>{status_emoji} {task.get('title', '제목 없음')}</strong><br>
                        <small>{priority_color} {task.get('priority', 'medium').upper()} | 
                        마감: {task.get('deadline', 'N/A')}</small><br>
                        <span>{task.get('description', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("오늘 등록된 태스크가 없습니다.")
        
        # 오늘의 스케줄
        st.subheader("📅 오늘의 일정")
        if today_schedule:
            for schedule in today_schedule:
                start_time = schedule.get('start_time', '')
                end_time = schedule.get('end_time', '')
                if start_time and end_time:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    time_str = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
                else:
                    time_str = "시간 미정"
                
                st.markdown(f"""
                <div class="task-card">
                    <strong>📅 {schedule.get('title', '제목 없음')}</strong><br>
                    <small>⏰ {time_str}</small><br>
                    <span>{schedule.get('description', '')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("오늘 등록된 일정이 없습니다.")
    
    with col2:
        # 워라밸 점수 차트
        st.subheader("⚖️ 워라밸 점수")
        if worklife_scores and len(worklife_scores) > 0:
            # 최근 4주 데이터
            recent_scores = worklife_scores[:4]
            if recent_scores:
                try:
                    df_scores = pd.DataFrame(recent_scores)
                    df_scores['week_start'] = pd.to_datetime(df_scores['week_start'])
                    
                    fig = go.Figure()
                    
                    # overall_score 컬럼이 있는지 확인
                    if 'overall_score' in df_scores.columns:
                        fig.add_trace(go.Scatter(
                            x=df_scores['week_start'],
                            y=df_scores['overall_score'],
                            mode='lines+markers',
                            name='전체 점수',
                            line=dict(color='#FF2D20', width=3)
                        ))
                    
                    # work_score 컬럼이 있는지 확인
                    if 'work_score' in df_scores.columns:
                        fig.add_trace(go.Scatter(
                            x=df_scores['week_start'],
                            y=df_scores['work_score'],
                            mode='lines+markers',
                            name='업무 점수',
                            line=dict(color='#1F2937', width=2)
                        ))
                    
                    # life_score 컬럼이 있는지 확인
                    if 'life_score' in df_scores.columns:
                        fig.add_trace(go.Scatter(
                            x=df_scores['week_start'],
                            y=df_scores['life_score'],
                            mode='lines+markers',
                            name='생활 점수',
                            line=dict(color='#10B981', width=2)
                        ))
                    
                    fig.update_layout(
                        title="주간 워라밸 점수 추이",
                        xaxis_title="주차",
                        yaxis_title="점수",
                        height=300,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"차트 생성 중 오류: {str(e)}")
                    st.info("워라밸 점수 데이터를 확인해주세요.")
            else:
                st.info("워라밸 점수 데이터가 없습니다.")
        else:
            st.info("워라밸 점수 데이터가 없습니다.")
        
        # 습관 체크리스트
        st.subheader("🎯 오늘의 습관")
        if today_habits:
            for habit in today_habits:
                habit_type = habit.get('habit_type', '')
                completed = habit.get('completed', False)
                note = habit.get('note', '')
                
                status_icon = "✅" if completed else "⭕"
                st.markdown(f"{status_icon} **{habit_type}**")
                if note:
                    st.markdown(f"   <small>{note}</small>", unsafe_allow_html=True)
        else:
            st.info("오늘 등록된 습관이 없습니다.")
        
        # 빠른 액션 버튼들
        st.subheader("⚡ 빠른 액션")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📝 새 태스크", use_container_width=True):
                st.session_state.show_task_form = True
        
        with col_btn2:
            if st.button("📅 새 일정", use_container_width=True):
                st.session_state.show_schedule_form = True
    
    # 빠른 액션 폼들
    if st.session_state.get('show_task_form'):
        show_quick_task_form(api_client)
    
    if st.session_state.get('show_schedule_form'):
        show_quick_schedule_form(api_client)

def show_quick_task_form(api_client):
    """빠른 태스크 생성 폼"""
    st.markdown("---")
    st.subheader("📝 새 태스크 추가")
    
    with st.form("quick_task_form"):
        title = st.text_input("태스크 제목", placeholder="할 일을 입력하세요")
        description = st.text_area("설명 (선택사항)", placeholder="상세 설명을 입력하세요")
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("우선순위", ["low", "medium", "high", "urgent"])
        with col2:
            deadline = st.date_input("마감일", value=date.today() + timedelta(days=1))
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit = st.form_submit_button("추가", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("취소", use_container_width=True)
        
        if submit and title:
            if api_client.create_task(
                title=title,
                description=description,
                priority=priority,
                deadline=deadline.isoformat()
            ):
                st.success("태스크가 추가되었습니다!")
                st.session_state.show_task_form = False
                st.rerun()
            else:
                st.error("태스크 추가에 실패했습니다.")
        
        if cancel:
            st.session_state.show_task_form = False
            st.rerun()

def show_quick_schedule_form(api_client):
    """빠른 일정 생성 폼"""
    st.markdown("---")
    st.subheader("📅 새 일정 추가")
    
    with st.form("quick_schedule_form"):
        title = st.text_input("일정 제목", placeholder="일정을 입력하세요")
        description = st.text_area("설명 (선택사항)", placeholder="상세 설명을 입력하세요")
        
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("시작 시간", value=datetime.now().time())
        with col2:
            end_time = st.time_input("종료 시간", value=(datetime.now() + timedelta(hours=1)).time())
        
        schedule_date = st.date_input("날짜", value=date.today())
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit = st.form_submit_button("추가", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("취소", use_container_width=True)
        
        if submit and title:
            start_datetime = datetime.combine(schedule_date, start_time)
            end_datetime = datetime.combine(schedule_date, end_time)
            
            if api_client.create_schedule(
                title=title,
                description=description,
                start_time=start_datetime.isoformat(),
                end_time=end_datetime.isoformat()
            ):
                st.success("일정이 추가되었습니다!")
                st.session_state.show_schedule_form = False
                st.rerun()
            else:
                st.error("일정 추가에 실패했습니다.")
        
        if cancel:
            st.session_state.show_schedule_form = False
            st.rerun()
