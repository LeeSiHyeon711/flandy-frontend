import streamlit as st
import base64
import os
from components.auth import logout, get_current_user


def get_image_base64(image_path):
    """이미지를 base64로 인코딩"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""
    except Exception:
        return ""


def show_sidebar():
    """사이드바 표시 및 페이지 선택"""

    # 로고
    logo_b64 = get_image_base64("assets/plandy-logo.png")
    if logo_b64:
        st.sidebar.markdown(
            f'<div style="text-align:center;margin-bottom:1rem;">'
            f'<img src="data:image/png;base64,{logo_b64}" width="120"></div>',
            unsafe_allow_html=True,
        )

    # # 테마 토글 (비활성)
    # if 'theme' not in st.session_state:
    #     st.session_state.theme = 'dark'
    # theme_icon = "☀️" if st.session_state.theme == 'dark' else "🌙"
    # theme_label = "라이트 모드" if st.session_state.theme == 'dark' else "다크 모드"
    # if st.sidebar.button(f"{theme_icon} {theme_label}", key="theme_toggle", use_container_width=True):
    #     st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    #     st.rerun()

    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    user = get_current_user()

    if user:
        if st.sidebar.button("로그아웃", key="top_logout", use_container_width=True):
            logout()
        return _show_logged_in_sidebar(user)
    else:
        return _show_login_sidebar()


def _show_logged_in_sidebar(user):
    """로그인된 사용자 사이드바"""
    st.sidebar.markdown(f"### 안녕하세요, {user.get('name', '사용자')}님!")
    st.sidebar.markdown(f"📧 {user.get('email', '')}")

    # 팀 선택
    from components.api_client import PlandyAPIClient
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)

    try:
        teams = api_client.get_teams()
    except Exception:
        teams = []

    if teams:
        team_names = [t.get('name', '알 수 없음') for t in teams]
        team_ids = [t.get('id') for t in teams]

        default_index = 0
        if 'selected_team_id' in st.session_state and st.session_state.selected_team_id in team_ids:
            default_index = team_ids.index(st.session_state.selected_team_id)

        selected_team_idx = st.sidebar.selectbox(
            "팀 선택",
            range(len(team_names)),
            format_func=lambda i: team_names[i],
            index=default_index,
            key="team_selector",
        )
        st.session_state.selected_team_id = team_ids[selected_team_idx]
        st.session_state.selected_team_name = team_names[selected_team_idx]
    else:
        st.sidebar.info("소속된 팀이 없습니다. '팀 관리'에서 팀을 생성하거나 참여하세요.")
        st.session_state.selected_team_id = None
        st.session_state.selected_team_name = None

    # 현재 선택된 페이지
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "스프린트 대시보드"

    menu_items = [
        ("📊", "스프린트 대시보드"),
        ("📋", "태스크 관리"),
        ("📅", "스케줄 관리"),
        ("👥", "팀 관리"),
        ("🤖", "AI 어시스턴트"),
    ]

    for icon, page_name in menu_items:
        is_active = st.session_state.selected_page == page_name
        if is_active:
            st.sidebar.markdown(
                f'<div style="background-color: #3B82F6; color: #FFFFFF; padding: 0.5rem 0.75rem; border-radius: 8px; margin-bottom: 0.25rem; font-weight: bold; text-align: center;">{icon} {page_name}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.sidebar.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
                st.session_state.selected_page = page_name
                st.rerun()

    selected_page = st.session_state.selected_page

    # 서버 상태
    try:
        import requests
        resp = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
        if resp.status_code == 200:
            st.sidebar.success("🟢 서버 연결됨")
        else:
            st.sidebar.error("🔴 서버 오류")
    except Exception:
        st.sidebar.error("🔴 서버 연결 실패")

    return selected_page


def _show_login_sidebar():
    """로그인/회원가입 사이드바"""
    st.sidebar.markdown("### 로그인")

    with st.sidebar.form("sidebar_login_form"):
        email = st.text_input("이메일", placeholder="demo@flandy.kr")
        password = st.text_input("비밀번호", type="password", placeholder="demo1234")
        login_submitted = st.form_submit_button("로그인", use_container_width=True)

    if login_submitted:
        if email and password:
            from components.api_client import PlandyAPIClient
            api_client = PlandyAPIClient()
            if api_client.login(email, password):
                st.session_state.user_token = api_client.token
                user_info = api_client.get_user_info()
                if user_info:
                    st.session_state.user_info = user_info
                    st.sidebar.success(f"환영합니다, {user_info.get('name', '사용자')}님!")
                    st.rerun()
            else:
                st.sidebar.error("로그인에 실패했습니다.")
        else:
            st.sidebar.error("이메일과 비밀번호를 입력해주세요.")

    if st.sidebar.button("데모 로그인", use_container_width=True):
        from components.api_client import PlandyAPIClient
        api_client = PlandyAPIClient()
        if api_client.login("demo@flandy.kr", "demo1234"):
            st.session_state.user_token = api_client.token
            user_info = api_client.get_user_info()
            if user_info:
                st.session_state.user_info = user_info
                st.sidebar.success("데모 계정으로 로그인되었습니다!")
                st.rerun()
        else:
            st.sidebar.error("데모 계정 로그인에 실패했습니다.")

    # 회원가입
    st.sidebar.markdown("### 회원가입")
    with st.sidebar.form("sidebar_register_form"):
        name = st.text_input("이름", placeholder="홍길동")
        email_reg = st.text_input("이메일", placeholder="user@example.com")
        password_reg = st.text_input("비밀번호", type="password")
        password_confirm = st.text_input("비밀번호 확인", type="password")
        register_submitted = st.form_submit_button("회원가입", use_container_width=True)

    if register_submitted:
        if not all([name, email_reg, password_reg, password_confirm]):
            st.sidebar.error("모든 필드를 입력해주세요.")
        elif password_reg != password_confirm:
            st.sidebar.error("비밀번호가 일치하지 않습니다.")
        elif len(password_reg) < 6:
            st.sidebar.error("비밀번호는 6자 이상이어야 합니다.")
        else:
            from components.api_client import PlandyAPIClient
            api_client = PlandyAPIClient()
            if api_client.register(email_reg, password_reg, name, password_confirm):
                st.session_state.user_token = api_client.token
                user_info = api_client.get_user_info()
                if user_info:
                    st.session_state.user_info = user_info
                    st.sidebar.success("회원가입이 완료되었습니다!")
                    st.rerun()
            else:
                st.sidebar.error("회원가입에 실패했습니다.")

    return None
