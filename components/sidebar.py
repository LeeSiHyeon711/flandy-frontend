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
        else:
            # 이미지가 없으면 빈 문자열 반환
            return ""
    except Exception as e:
        st.error(f"이미지 로드 오류: {e}")
        return ""

def show_sidebar():
    """사이드바 표시 및 페이지 선택"""
    
    # Plandy 로고 표시 (사이드바 상단 중앙정렬)
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <img src="data:image/png;base64,{}" width="120" style="margin: 0 auto;">
    </div>
    """.format(get_image_base64("assets/plandy-logo.png")), unsafe_allow_html=True)
    
    # 사용자 정보 표시 또는 로그인 폼
    user = get_current_user()
    if user:
        # 로그인된 상태: 사용자 정보, 메뉴, 로그아웃, 서버 상태 표시
        st.sidebar.markdown(f"### 안녕하세요, {user.get('name', '사용자')}님!")
        st.sidebar.markdown(f"📧 {user.get('email', '')}")
        st.sidebar.markdown("---")
        
        # 메뉴 항목들
        menu_items = [
            "대시보드",
            "태스크 관리", 
            "스케줄 관리",
            "워라밸 분석",
            "AI 어시스턴트"
        ]
        
        selected_page = st.sidebar.selectbox("메뉴 선택", menu_items, key="page_selector")
        
        st.sidebar.markdown("---")
        
        # 로그아웃 버튼
        if st.sidebar.button("로그아웃", use_container_width=True):
            logout()
        
        st.sidebar.markdown("---")
        
        # 서버 상태 표시
        st.sidebar.markdown("### 서버 상태")
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000/api/health", timeout=2)
            if response.status_code == 200:
                st.sidebar.success("🟢 서버 연결됨")
            else:
                st.sidebar.error("🔴 서버 오류")
        except:
            st.sidebar.error("🔴 서버 연결 실패")
        
        return selected_page
    else:
        # 로그인되지 않은 상태: 로그인/회원가입 폼만 표시
        st.sidebar.markdown("### 로그인")
        
        with st.sidebar.form("sidebar_login_form"):
            email = st.text_input("이메일", placeholder="kim@plandy.kr")
            password = st.text_input("비밀번호", type="password", placeholder="password123")
            
            login_submitted = st.form_submit_button("로그인", use_container_width=True)
            demo_login = st.form_submit_button("데모 로그인", use_container_width=True)
        
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
        
        if demo_login:
            from components.api_client import PlandyAPIClient
            api_client = PlandyAPIClient()
            if api_client.login("kim@plandy.kr", "password123"):
                st.session_state.user_token = api_client.token
                user_info = api_client.get_user_info()
                if user_info:
                    st.session_state.user_info = user_info
                    st.sidebar.success(f"데모 계정으로 로그인되었습니다!")
                    st.rerun()
            else:
                st.sidebar.error("데모 계정 로그인에 실패했습니다.")
        
        st.sidebar.markdown("---")
        
        # 회원가입 섹션을 접을 수 있게 만들기
        with st.sidebar.expander("회원가입", expanded=False):
            with st.form("sidebar_register_form"):
                name = st.text_input("이름", placeholder="홍길동")
                email_reg = st.text_input("이메일", placeholder="user@example.com")
                password_reg = st.text_input("비밀번호", type="password")
                password_confirm = st.text_input("비밀번호 확인", type="password")
                
                register_submitted = st.form_submit_button("회원가입", use_container_width=True)
            
            if register_submitted:
                if not all([name, email_reg, password_reg, password_confirm]):
                    st.error("모든 필드를 입력해주세요.")
                elif password_reg != password_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif len(password_reg) < 6:
                    st.error("비밀번호는 6자 이상이어야 합니다.")
                else:
                    from components.api_client import PlandyAPIClient
                    api_client = PlandyAPIClient()
                    if api_client.register(email_reg, password_reg, name, password_confirm):
                        st.session_state.user_token = api_client.token
                        user_info = api_client.get_user_info()
                        if user_info:
                            st.session_state.user_info = user_info
                            st.success(f"회원가입이 완료되었습니다!")
                            st.rerun()
                    else:
                        st.error("회원가입에 실패했습니다.")
        
        return None  # 로그인되지 않은 상태에서는 페이지 선택 없음