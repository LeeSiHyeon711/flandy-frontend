"""
사이드바 컴포넌트
사용자 현황, 대화 목록, 설정 등을 담당
"""

import streamlit as st
from datetime import datetime
from utils.data_utils import load_sample_data, calculate_worklife_score


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        # 사이드바 전체 스타일링 (한 번만 적용)
        st.markdown("""
        <style>
        /* 사이드바 전체 리셋 */
        .sidebar * {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* 사이드바 컨테이너 간격 강제 고정 */
        .sidebar .element-container {
            margin-bottom: 20px !important;
            margin-top: 0 !important;
            padding: 0 !important;
        }
        
        /* 사이드바 첫 번째 요소 */
        .sidebar .element-container:first-child {
            margin-top: 0 !important;
        }
        
        /* 사이드바 마지막 요소 */
        .sidebar .element-container:last-child {
            margin-bottom: 0 !important;
        }
        
        /* 대화방 버튼 스타일링 */
        div[data-testid="stButton"] > button {
            text-align: left !important;
            padding: 12px 16px !important;
            height: auto !important;
            min-height: 70px !important;
            border-radius: 8px !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            margin: 0 !important;
        }
        
        /* 대화방 버튼 컨테이너 간격 강제 고정 */
        div[data-testid="stButton"] {
            margin-bottom: 8px !important;
            margin-top: 0 !important;
        }
        
        /* 선택된 대화방 버튼 */
        div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
            color: white !important;
        }
        
        /* 일반 대화방 버튼 - Streamlit 기본 스타일 강제 덮어쓰기 */
        .sidebar div[data-testid="stButton"] > button[kind="secondary"],
        .sidebar div[data-testid="stButton"] button[kind="secondary"],
        .sidebar button[kind="secondary"],
        .sidebar .stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 0px solid transparent !important;
            border-width: 0px !important;
            border-style: none !important;
            border-color: transparent !important;
            color: #e0e0e0 !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        .sidebar div[data-testid="stButton"] > button[kind="secondary"]:hover,
        .sidebar div[data-testid="stButton"] button[kind="secondary"]:hover,
        .sidebar button[kind="secondary"]:hover,
        .sidebar .stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 0px solid transparent !important;
            border-width: 0px !important;
            border-style: none !important;
            border-color: transparent !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* 컬럼 간격 강제 고정 */
        .stColumns > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* 마크다운 헤더 간격 강제 고정 */
        .sidebar h3 {
            margin-bottom: 12px !important;
            margin-top: 0 !important;
        }
        
        /* 이미지 간격 강제 고정 */
        .sidebar img {
            margin-bottom: 8px !important;
            margin-top: 0 !important;
        }
        
        /* expander 간격 강제 고정 */
        .sidebar .streamlit-expander {
            margin-bottom: 20px !important;
            margin-top: 0 !important;
        }
        
        /* 모든 텍스트 요소 간격 리셋 */
        .sidebar p, .sidebar div, .sidebar span {
            margin: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 플랜디 로고 (가운데 정렬, 고정 크기)
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            st.image("assets/plandy.png", width=180)

        st.markdown('<p style="text-align: center; font-size: 16px; margin: 5px 5px 15px 5px;">"계획은 유연하게, 하루는 완벽하게!"</p>', unsafe_allow_html=True)
        
        # 오늘의 현황
        render_today_status()
        
        # 컨테이너 표시 설정
        render_container_settings()
        
        # 대화 목록
        render_conversation_list()


def render_today_status():
    """오늘의 현황 섹션"""
    with st.expander("📊 오늘의 현황", expanded=True):
        # 현재 시간 표시
        current_time = datetime.now().strftime("%H:%M")
        st.metric("현재 시간", current_time)
        
        # 워라벨 점수
        df = load_sample_data()
        worklife_score = calculate_worklife_score(df)
        
        # 워라벨 점수를 다크모드 호환으로 표시
        st.markdown("**워라벨 점수**")
        st.markdown(f"""
        <div style="text-align: center; margin: 0.5rem 0;">
            <div style="font-size: 2rem; font-weight: bold; color: #4A90E2; line-height: 1.2;">{worklife_score}/100</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 완료된 일정을 마지막에 표시
        completed_tasks = len(df[df['time'] <= current_time])
        total_tasks = len(df)
        progress = completed_tasks / total_tasks if total_tasks > 0 else 0
        st.progress(progress)
        st.caption(f"완료된 일정: {completed_tasks}/{total_tasks}")


def render_container_settings():
    """컨테이너 표시 설정"""
    with st.expander("🎛️ 컨테이너 표시 설정", expanded=False):
        # 각 컨테이너 토글 - 세션 상태에서 초기값 가져오기
        show_chart = st.checkbox(
            "📊 24시간 생활계획표", 
            value=st.session_state.get('show_chart', True), 
            key="show_chart"
        )
        show_table = st.checkbox(
            "📋 상세 일정", 
            value=st.session_state.get('show_table', True), 
            key="show_table"
        ) 
        show_analysis = st.checkbox(
            "📈 워라벨 분석", 
            value=st.session_state.get('show_analysis', True), 
            key="show_analysis"
        )


def render_conversation_list():
    """대화 목록 렌더링 - ChatGPT 스타일"""
    # 대화 목록 헤더와 + 버튼
    col1, col2 = st.columns([4, 0.5])
    with col1:
        st.markdown("### 💬 대화 목록")
    with col2:
        if st.button("✚", key="new_chat_btn", help="새 대화방 만들기"):
            st.session_state.current_page = "chat"
            st.session_state.selected_conversation = "새 대화방"
            st.rerun()
    
    # 대화방 목록
    conversations = [
        {"name": "일정 관리", "last_msg": "오늘 일정을 확인해주세요"},
        {"name": "워라벨 상담", "last_msg": "워라벨 점수를 개선해보세요"},
        {"name": "목표 설정", "last_msg": "이번 주 목표를 설정해보세요"},
        {"name": "분석 리포트", "last_msg": "주간 리포트를 확인하세요"}
    ]
    
    # 현재 선택된 대화방 (채팅 페이지일 때만 활성화)
    current_page = st.session_state.get('current_page', 'dashboard')
    selected_conv = st.session_state.get('selected_conversation', None)
    
    # 채팅 페이지가 아니면 선택된 대화방 없음
    if current_page != 'chat':
        selected_conv = None
    
    # ChatGPT 스타일의 대화방 버튼들
    for i, conv in enumerate(conversations):
        is_selected = conv['name'] == selected_conv
        
        # 보기 좋은 버튼 텍스트 (시간 제거)
        button_text = f"[{conv['name']}] {conv['last_msg']}"
        
        # 버튼 클릭 이벤트
        if st.button(button_text, key=f"conv_btn_{i}", type="primary" if is_selected else "secondary", use_container_width=True):
            st.session_state.current_page = "chat"
            st.session_state.selected_conversation = conv['name']
            st.rerun()
