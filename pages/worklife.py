import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from components.api_client import PlandyAPIClient
import plotly.express as px
import plotly.graph_objects as go

def show_worklife():
    """워라밸 분석 페이지 표시"""
    st.header("⚖️ 워라밸 분석")
    
    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📊 점수 분석", "🎯 습관 관리", "📈 트렌드 분석"])
    
    with tab1:
        show_score_analysis(api_client)
    
    with tab2:
        show_habit_management(api_client)
    
    with tab3:
        show_trend_analysis(api_client)

def show_score_analysis(api_client):
    """워라밸 점수 분석"""
    st.subheader("📊 워라밸 점수 분석")
    
    # 워라밸 점수 데이터 로딩
    with st.spinner("워라밸 점수를 불러오는 중..."):
        scores = api_client.get_worklife_scores()
    
    if scores:
        # 최신 점수 표시
        latest_score = scores[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "전체 점수",
                f"{latest_score.get('overall_score', 0):.1f}/10",
                delta=f"이전 주 대비 {get_score_change(scores, 'overall_score'):+.1f}"
            )
        
        with col2:
            st.metric(
                "업무 점수",
                f"{latest_score.get('work_score', 0):.1f}/10",
                delta=f"이전 주 대비 {get_score_change(scores, 'work_score'):+.1f}"
            )
        
        with col3:
            st.metric(
                "생활 점수",
                f"{latest_score.get('life_score', 0):.1f}/10",
                delta=f"이전 주 대비 {get_score_change(scores, 'life_score'):+.1f}"
            )
        
        with col4:
            st.metric(
                "스트레스 레벨",
                f"{latest_score.get('stress_level', 0)}/5",
                delta=f"이전 주 대비 {get_score_change(scores, 'stress_level'):+.1f}"
            )
        
        # 점수 분포 차트
        st.subheader("📈 점수 분포")
        
        # 최근 8주 데이터
        recent_scores = scores[:8]
        if len(recent_scores) >= 2:
            df_scores = pd.DataFrame(recent_scores)
            df_scores['week_start'] = pd.to_datetime(df_scores['week_start'])
            
            fig = go.Figure()
            
            # 전체 점수
            fig.add_trace(go.Scatter(
                x=df_scores['week_start'],
                y=df_scores['overall_score'],
                mode='lines+markers',
                name='전체 점수',
                line=dict(color='#FF2D20', width=3),
                marker=dict(size=8)
            ))
            
            # 업무 점수
            fig.add_trace(go.Scatter(
                x=df_scores['week_start'],
                y=df_scores['work_score'],
                mode='lines+markers',
                name='업무 점수',
                line=dict(color='#1F2937', width=2),
                marker=dict(size=6)
            ))
            
            # 생활 점수
            fig.add_trace(go.Scatter(
                x=df_scores['week_start'],
                y=df_scores['life_score'],
                mode='lines+markers',
                name='생활 점수',
                line=dict(color='#10B981', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title="주간 워라밸 점수 추이",
                xaxis_title="주차",
                yaxis_title="점수",
                height=400,
                showlegend=True,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 스트레스와 만족도 분석
        st.subheader("😌 스트레스 & 만족도 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 스트레스 레벨 차트
            if len(recent_scores) >= 2:
                fig_stress = px.bar(
                    df_scores,
                    x='week_start',
                    y='stress_level',
                    title='주간 스트레스 레벨',
                    color='stress_level',
                    color_continuous_scale='Reds'
                )
                fig_stress.update_layout(height=300)
                st.plotly_chart(fig_stress, use_container_width=True)
        
        with col2:
            # 만족도 차트
            if len(recent_scores) >= 2:
                fig_satisfaction = px.bar(
                    df_scores,
                    x='week_start',
                    y='satisfaction',
                    title='주간 만족도',
                    color='satisfaction',
                    color_continuous_scale='Greens'
                )
                fig_satisfaction.update_layout(height=300)
                st.plotly_chart(fig_satisfaction, use_container_width=True)
        
        # 새 점수 입력
        st.subheader("📝 새 점수 입력")
        if st.button("➕ 새 주간 점수 추가", use_container_width=True):
            st.session_state.show_score_form = True
        
        if st.session_state.get('show_score_form'):
            show_score_form(api_client)
    
    else:
        st.info("워라밸 점수 데이터가 없습니다. 첫 번째 점수를 입력해보세요!")
        if st.button("➕ 첫 번째 점수 입력", use_container_width=True):
            st.session_state.show_score_form = True
        
        if st.session_state.get('show_score_form'):
            show_score_form(api_client)

def show_habit_management(api_client):
    """습관 관리"""
    st.subheader("🎯 습관 관리")
    
    # 오늘 날짜
    today = date.today()
    today_str = today.isoformat()
    
    # 오늘의 습관 로그 로딩
    with st.spinner("습관 데이터를 불러오는 중..."):
        today_habits = api_client.get_habit_logs(date=today_str)
        all_habits = api_client.get_habit_logs()
    
    # 습관 통계
    if all_habits:
        # 습관 타입별 통계
        habit_types = list(set([h.get('habit_type') for h in all_habits]))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_habits = len(all_habits)
            completed_habits = len([h for h in all_habits if h.get('completed')])
            completion_rate = (completed_habits / total_habits * 100) if total_habits > 0 else 0
            
            st.metric(
                "전체 습관 달성률",
                f"{completion_rate:.1f}%",
                delta=f"{completed_habits}/{total_habits}"
            )
        
        with col2:
            st.metric(
                "습관 종류",
                len(habit_types),
                delta="개"
            )
        
        with col3:
            # 연속 달성일 계산
            consecutive_days = calculate_consecutive_days(all_habits)
            st.metric(
                "최대 연속 달성",
                f"{consecutive_days}일",
                delta="일"
            )
    
    # 오늘의 습관 체크리스트
    st.subheader(f"📅 {today.strftime('%Y년 %m월 %d일')} 습관 체크")
    
    if today_habits:
        for habit in today_habits:
            show_habit_card(habit, api_client)
    else:
        st.info("오늘 등록된 습관이 없습니다.")
    
    # 새 습관 추가
    st.subheader("➕ 새 습관 추가")
    if st.button("🎯 새 습관 로그 추가", use_container_width=True):
        st.session_state.show_habit_form = True
    
    if st.session_state.get('show_habit_form'):
        show_habit_form(api_client)

def show_trend_analysis(api_client):
    """트렌드 분석"""
    st.subheader("📈 트렌드 분석")
    
    # 데이터 로딩
    with st.spinner("분석 데이터를 불러오는 중..."):
        scores = api_client.get_worklife_scores()
        habits = api_client.get_habit_logs()
    
    if scores and habits:
        # 월별 트렌드 분석
        st.subheader("📊 월별 트렌드")
        
        # 점수 데이터를 월별로 그룹화
        df_scores = pd.DataFrame(scores)
        df_scores['week_start'] = pd.to_datetime(df_scores['week_start'])
        df_scores['month'] = df_scores['week_start'].dt.to_period('M')
        
        monthly_scores = df_scores.groupby('month').agg({
            'overall_score': 'mean',
            'work_score': 'mean',
            'life_score': 'mean',
            'stress_level': 'mean',
            'satisfaction': 'mean'
        }).reset_index()
        
        # 월별 점수 차트
        fig_monthly = go.Figure()
        
        fig_monthly.add_trace(go.Scatter(
            x=monthly_scores['month'].astype(str),
            y=monthly_scores['overall_score'],
            mode='lines+markers',
            name='전체 점수',
            line=dict(color='#FF2D20', width=3)
        ))
        
        fig_monthly.add_trace(go.Scatter(
            x=monthly_scores['month'].astype(str),
            y=monthly_scores['work_score'],
            mode='lines+markers',
            name='업무 점수',
            line=dict(color='#1F2937', width=2)
        ))
        
        fig_monthly.add_trace(go.Scatter(
            x=monthly_scores['month'].astype(str),
            y=monthly_scores['life_score'],
            mode='lines+markers',
            name='생활 점수',
            line=dict(color='#10B981', width=2)
        ))
        
        fig_monthly.update_layout(
            title="월별 워라밸 점수 추이",
            xaxis_title="월",
            yaxis_title="점수",
            height=400
        )
        
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # 습관 달성률 분석
        st.subheader("🎯 습관 달성률 분석")
        
        df_habits = pd.DataFrame(habits)
        df_habits['date'] = pd.to_datetime(df_habits['date'])
        df_habits['month'] = df_habits['date'].dt.to_period('M')
        
        # 월별 습관 달성률
        monthly_habits = df_habits.groupby('month').agg({
            'completed': ['count', 'sum']
        }).reset_index()
        
        monthly_habits.columns = ['month', 'total_habits', 'completed_habits']
        monthly_habits['completion_rate'] = (monthly_habits['completed_habits'] / monthly_habits['total_habits'] * 100)
        
        fig_habits = px.bar(
            monthly_habits,
            x='month',
            y='completion_rate',
            title='월별 습관 달성률',
            color='completion_rate',
            color_continuous_scale='Greens'
        )
        fig_habits.update_layout(height=300)
        st.plotly_chart(fig_habits, use_container_width=True)
        
        # AI 분석 요청
        st.subheader("🤖 AI 워라밸 분석")
        if st.button("🔍 AI 분석 요청", use_container_width=True):
            with st.spinner("AI가 워라밸을 분석하는 중..."):
                analysis_result = api_client.analyze_worklife(period="month", include_suggestions=True)
                
                if analysis_result:
                    st.success("AI 분석이 완료되었습니다!")
                    
                    # 분석 결과 표시
                    if 'analysis' in analysis_result:
                        st.markdown("### 📊 분석 결과")
                        st.write(analysis_result['analysis'])
                    
                    if 'suggestions' in analysis_result:
                        st.markdown("### 💡 개선 제안")
                        for suggestion in analysis_result['suggestions']:
                            st.markdown(f"- {suggestion}")
                else:
                    st.error("AI 분석에 실패했습니다.")
    
    else:
        st.info("분석할 데이터가 부족합니다. 더 많은 데이터를 입력해주세요.")

def show_score_form(api_client):
    """워라밸 점수 입력 폼"""
    st.markdown("---")
    st.subheader("📝 새 주간 점수 입력")
    
    with st.form("score_form"):
        # 주 시작일 선택
        week_start = st.date_input(
            "주 시작일 (월요일)",
            value=date.today() - timedelta(days=date.today().weekday())
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            overall_score = st.slider(
                "전체 점수",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.1,
                help="전반적인 워라밸 만족도"
            )
            
            work_score = st.slider(
                "업무 점수",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.1,
                help="업무 관련 만족도"
            )
        
        with col2:
            life_score = st.slider(
                "생활 점수",
                min_value=0.0,
                max_value=10.0,
                value=7.0,
                step=0.1,
                help="개인 생활 만족도"
            )
            
            stress_level = st.slider(
                "스트레스 레벨",
                min_value=1,
                max_value=5,
                value=3,
                help="1: 매우 낮음, 5: 매우 높음"
            )
        
        satisfaction = st.slider(
            "전반적 만족도",
            min_value=1,
            max_value=5,
            value=4,
            help="1: 매우 불만족, 5: 매우 만족"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit = st.form_submit_button("저장", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("취소", use_container_width=True)
        
        if submit:
            if api_client.create_worklife_score(
                week_start=week_start.isoformat(),
                overall_score=overall_score,
                work_score=work_score,
                life_score=life_score,
                stress_level=stress_level,
                satisfaction=satisfaction
            ):
                st.success("워라밸 점수가 저장되었습니다!")
                st.session_state.show_score_form = False
                st.rerun()
            else:
                st.error("점수 저장에 실패했습니다.")
        
        if cancel:
            st.session_state.show_score_form = False
            st.rerun()

def show_habit_card(habit, api_client):
    """습관 카드 표시"""
    habit_id = habit.get('id')
    habit_type = habit.get('habit_type', '')
    completed = habit.get('completed', False)
    note = habit.get('note', '')
    date_str = habit.get('date', '')
    
    status_icon = "✅" if completed else "⭕"
    status_color = "#10B981" if completed else "#6B7280"
    
    with st.container():
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 8px; 
                    padding: 1rem; margin-bottom: 1rem; border-left: 4px solid {status_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #1F2937;">{status_icon} {habit_type}</h4>
                    {f'<p style="margin: 0.5rem 0; color: #6B7280; font-size: 0.9rem;">{note}</p>' if note else ''}
                    <small style="color: #6B7280;">📅 {date_str}</small>
                </div>
                <div>
        """, unsafe_allow_html=True)
        
        # 토글 버튼
        if completed:
            if st.button("⭕", key=f"uncomplete_{habit_id}", help="미완료로 변경"):
                if api_client.update_habit_log(habit_id, completed=False):
                    st.success("습관이 미완료로 변경되었습니다!")
                    st.rerun()
        else:
            if st.button("✅", key=f"complete_{habit_id}", help="완료로 변경"):
                if api_client.update_habit_log(habit_id, completed=True):
                    st.success("습관이 완료되었습니다!")
                    st.rerun()
        
        st.markdown("</div></div></div>", unsafe_allow_html=True)

def show_habit_form(api_client):
    """습관 로그 입력 폼"""
    st.markdown("---")
    st.subheader("🎯 새 습관 로그 추가")
    
    with st.form("habit_form"):
        habit_type = st.text_input(
            "습관 종류",
            placeholder="예: 운동, 독서, 명상"
        )
        
        completed = st.checkbox("완료 여부", value=True)
        
        note = st.text_area(
            "메모 (선택사항)",
            placeholder="습관에 대한 추가 정보나 느낌을 기록하세요"
        )
        
        habit_date = st.date_input(
            "날짜",
            value=date.today()
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit = st.form_submit_button("저장", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("취소", use_container_width=True)
        
        if submit and habit_type:
            if api_client.create_habit_log(
                habit_type=habit_type,
                completed=completed,
                note=note
            ):
                st.success("습관 로그가 저장되었습니다!")
                st.session_state.show_habit_form = False
                st.rerun()
            else:
                st.error("습관 로그 저장에 실패했습니다.")
        
        if cancel:
            st.session_state.show_habit_form = False
            st.rerun()

def get_score_change(scores, field):
    """점수 변화량 계산"""
    if len(scores) < 2:
        return 0
    
    current = scores[0].get(field, 0)
    previous = scores[1].get(field, 0)
    return current - previous

def calculate_consecutive_days(habits):
    """연속 달성일 계산"""
    if not habits:
        return 0
    
    # 날짜순 정렬
    sorted_habits = sorted(habits, key=lambda x: x.get('date', ''), reverse=True)
    
    consecutive = 0
    current_date = None
    
    for habit in sorted_habits:
        habit_date = habit.get('date')
        if habit_date != current_date:
            if habit.get('completed'):
                consecutive += 1
                current_date = habit_date
            else:
                break
        elif habit.get('completed'):
            continue
        else:
            break
    
    return consecutive
