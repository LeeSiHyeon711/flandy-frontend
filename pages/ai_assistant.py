import streamlit as st
from datetime import datetime, date
from components.api_client import PlandyAPIClient
import json

def show_ai_assistant():
    """AI 어시스턴트 페이지 표시"""
    st.header("🤖 AI 어시스턴트")
    
    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)
    
    # 채팅 히스토리 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # AI 어시스턴트 소개
    st.markdown("""
    <div style="background-color: #F0F9FF; border: 1px solid #0EA5E9; border-radius: 8px; padding: 1rem; margin-bottom: 2rem;">
        <h4 style="color: #0C4A6E; margin: 0;">🤖 Plandy AI 어시스턴트</h4>
        <p style="color: #075985; margin: 0.5rem 0;">AI가 당신의 생산성과 워라밸을 개선하는 데 도움을 드립니다!</p>
        <ul style="color: #075985; margin: 0;">
            <li>📋 태스크 우선순위 추천</li>
            <li>📅 일정 최적화 제안</li>
            <li>⚖️ 워라밸 분석 및 개선 방안</li>
            <li>💡 개인화된 생산성 팁</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 빠른 액션 버튼들
    st.subheader("⚡ 빠른 액션")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 태스크 추천", use_container_width=True):
            send_quick_message(api_client, "오늘 할 일을 추천해줘")
    
    with col2:
        if st.button("📅 일정 최적화", use_container_width=True):
            send_quick_message(api_client, "내 일정을 최적화해줘")
    
    with col3:
        if st.button("⚖️ 워라밸 분석", use_container_width=True):
            send_quick_message(api_client, "내 워라밸을 분석해줘")
    
    with col4:
        if st.button("💡 생산성 팁", use_container_width=True):
            send_quick_message(api_client, "생산성을 높이는 팁을 알려줘")
    
    st.markdown("---")
    
    # 채팅 인터페이스
    st.subheader("💬 AI와 대화하기")
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="text-align: right; margin: 1rem 0;">
                    <div style="background-color: #3B82F6; color: white; padding: 0.75rem; 
                                border-radius: 18px 18px 4px 18px; display: inline-block; max-width: 70%;">
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: left; margin: 1rem 0;">
                    <div style="background-color: #F3F4F6; color: #1F2937; padding: 0.75rem; 
                                border-radius: 18px 18px 18px 4px; display: inline-block; max-width: 70%;">
                        <strong>🤖 AI:</strong><br>
                        {message['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 메시지 입력
    st.markdown("---")
    
    with st.form("chat_form"):
        user_message = st.text_area(
            "메시지를 입력하세요",
            placeholder="예: 오늘 할 일을 추천해줘, 내 일정을 최적화해줘, 워라밸을 개선하는 방법을 알려줘",
            height=100
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            send_button = st.form_submit_button("📤 전송", use_container_width=True)
        with col2:
            clear_button = st.form_submit_button("🗑️ 대화 초기화", use_container_width=True)
        with col3:
            context_button = st.form_submit_button("📊 컨텍스트 포함", use_container_width=True)
        
        if send_button and user_message:
            send_message(api_client, user_message)
        
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
        
        if context_button and user_message:
            send_message_with_context(api_client, user_message)
    
    # 컨텍스트 정보 표시
    st.markdown("---")
    st.subheader("📊 현재 컨텍스트")
    
    with st.spinner("컨텍스트 정보를 불러오는 중..."):
        # 현재 데이터 수집
        today = date.today().isoformat()
        tasks = api_client.get_tasks()
        today_tasks = api_client.get_tasks(date=today)
        today_schedule = api_client.get_schedule_by_date(today)
        worklife_scores = api_client.get_worklife_scores()
        today_habits = api_client.get_habit_logs(date=today)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 태스크 현황**")
        st.write(f"- 전체 태스크: {len(tasks)}개")
        st.write(f"- 오늘 태스크: {len(today_tasks)}개")
        pending_tasks = len([t for t in today_tasks if t.get('status') == 'pending'])
        in_progress_tasks = len([t for t in today_tasks if t.get('status') == 'in_progress'])
        completed_tasks = len([t for t in today_tasks if t.get('status') == 'completed'])
        st.write(f"- 대기: {pending_tasks}개, 진행중: {in_progress_tasks}개, 완료: {completed_tasks}개")
        
        st.markdown("**📅 일정 현황**")
        st.write(f"- 오늘 일정: {len(today_schedule)}개")
    
    with col2:
        st.markdown("**⚖️ 워라밸 현황**")
        if worklife_scores:
            latest_score = worklife_scores[0]
            st.write(f"- 전체 점수: {latest_score.get('overall_score', 0):.1f}/10")
            st.write(f"- 업무 점수: {latest_score.get('work_score', 0):.1f}/10")
            st.write(f"- 생활 점수: {latest_score.get('life_score', 0):.1f}/10")
            st.write(f"- 스트레스 레벨: {latest_score.get('stress_level', 0)}/5")
        else:
            st.write("- 워라밸 점수 데이터 없음")
        
        st.markdown("**🎯 습관 현황**")
        st.write(f"- 오늘 습관: {len(today_habits)}개")
        completed_habits = len([h for h in today_habits if h.get('completed')])
        st.write(f"- 완료: {completed_habits}개")

def send_quick_message(api_client, message):
    """빠른 메시지 전송"""
    send_message(api_client, message)

def send_message(api_client, message):
    """일반 메시지 전송"""
    # 사용자 메시지를 히스토리에 추가
    st.session_state.chat_history.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # AI 응답 요청
    with st.spinner("AI가 응답을 생성하는 중..."):
        response = api_client.send_ai_message(message)
    
    if response:
        # AI 응답을 히스토리에 추가
        ai_response = response.get('response', '죄송합니다. 응답을 생성할 수 없습니다.')
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 제안사항이 있으면 표시
        suggestions = response.get('suggestions', [])
        if suggestions:
            suggestion_text = "\n\n**💡 제안사항:**\n"
            for suggestion in suggestions:
                suggestion_text += f"- {suggestion.get('content', '')}\n"
            
            st.session_state.chat_history[-1]['content'] += suggestion_text
        
        st.rerun()
    else:
        st.error("AI 응답을 받을 수 없습니다. 다시 시도해주세요.")

def send_message_with_context(api_client, message):
    """컨텍스트를 포함한 메시지 전송"""
    # 현재 컨텍스트 수집
    today = date.today().isoformat()
    tasks = api_client.get_tasks()
    today_tasks = api_client.get_tasks(date=today)
    today_schedule = api_client.get_schedule_by_date(today)
    worklife_scores = api_client.get_worklife_scores()
    today_habits = api_client.get_habit_logs(date=today)
    
    # 컨텍스트 정보 구성
    context = {
        'current_tasks': len(tasks),
        'today_tasks': len(today_tasks),
        'pending_tasks': len([t for t in today_tasks if t.get('status') == 'pending']),
        'in_progress_tasks': len([t for t in today_tasks if t.get('status') == 'in_progress']),
        'completed_tasks': len([t for t in today_tasks if t.get('status') == 'completed']),
        'today_schedule_count': len(today_schedule),
        'worklife_score': worklife_scores[0].get('overall_score', 0) if worklife_scores else 0,
        'stress_level': worklife_scores[0].get('stress_level', 0) if worklife_scores else 0,
        'today_habits': len(today_habits),
        'completed_habits': len([h for h in today_habits if h.get('completed')])
    }
    
    # 사용자 메시지를 히스토리에 추가
    st.session_state.chat_history.append({
        'role': 'user',
        'content': f"{message} (컨텍스트 포함)",
        'timestamp': datetime.now().isoformat()
    })
    
    # AI 응답 요청 (컨텍스트 포함)
    with st.spinner("AI가 컨텍스트를 분석하여 응답을 생성하는 중..."):
        response = api_client.send_ai_message(message, context)
    
    if response:
        # AI 응답을 히스토리에 추가
        ai_response = response.get('response', '죄송합니다. 응답을 생성할 수 없습니다.')
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 제안사항이 있으면 표시
        suggestions = response.get('suggestions', [])
        if suggestions:
            suggestion_text = "\n\n**💡 제안사항:**\n"
            for suggestion in suggestions:
                suggestion_text += f"- {suggestion.get('content', '')}\n"
            
            st.session_state.chat_history[-1]['content'] += suggestion_text
        
        st.rerun()
    else:
        st.error("AI 응답을 받을 수 없습니다. 다시 시도해주세요.")
