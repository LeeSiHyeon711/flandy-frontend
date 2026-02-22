import streamlit as st
from components.api_client import PlandyAPIClient
from typing import Optional

def check_auth_status() -> bool:
    """인증 상태 확인"""
    if 'user_token' not in st.session_state or st.session_state.user_token is None:
        return False
    return True

def show_login_page():
    """서비스 소개 페이지 표시"""
    # Plandy 로고 표시 (base64 인코딩 사용)
    try:
        import base64
        import os
        
        logo_path = "assets/plandy-logo.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                logo_base64 = base64.b64encode(img_file.read()).decode()
            
            st.markdown(f'<div style="text-align: center; margin-bottom: 3rem;"><img src="data:image/png;base64,{logo_base64}" width="300" style="margin: 0 auto;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<h1 style="text-align: center; color: var(--text-primary); margin-bottom: 3rem;">Flandy</h1>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown('<h1 style="text-align: center; color: var(--text-primary); margin-bottom: 3rem;">Flandy</h1>', unsafe_allow_html=True)
    
    # 서비스 소개
    st.markdown('<div style="text-align: center; margin-bottom: 3rem;"><h2 style="color: var(--text-primary); margin-bottom: 1rem;">팀 스프린트 도우미</h2><p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.6;">Flandy는 인공지능을 활용하여 팀의 스프린트와 업무를 더 효율적으로 관리할 수 있도록 도와드립니다.</p></div>', unsafe_allow_html=True)
    
    # 주요 기능 소개
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="flandy-card" style="text-align: center; padding: 2rem; border-radius: 12px; margin: 1rem;"><h3 style="margin-bottom: 1rem;">태스크 관리</h3><p>할 일을 체계적으로 관리하고 우선순위를 설정하여 효율적으로 업무를 처리하세요.</p></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="flandy-card" style="text-align: center; padding: 2rem; border-radius: 12px; margin: 1rem;"><h3 style="margin-bottom: 1rem;">스케줄 관리</h3><p>일정을 체계적으로 관리하고 시간을 효율적으로 활용하여 균형잡힌 생활을 만들어보세요.</p></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="flandy-card" style="text-align: center; padding: 2rem; border-radius: 12px; margin: 1rem;"><h3 style="margin-bottom: 1rem;">AI 어시스턴트</h3><p>인공지능이 당신의 패턴을 분석하여 개인화된 생산성 팁과 일정 최적화 제안을 제공합니다.</p></div>', unsafe_allow_html=True)
    
    # 시작하기 안내
    st.markdown('<div class="flandy-card" style="text-align: center; margin: 3rem 0; padding: 2rem; border-radius: 12px;"><h3 style="margin-bottom: 1rem;">지금 시작하세요!</h3><p style="margin-bottom: 1.5rem;">왼쪽 사이드바에서 로그인하거나 회원가입하여 Flandy의 모든 기능을 경험해보세요.</p><p style="color: var(--text-primary); font-weight: bold;">데모 계정: demo@flandy.kr / demo1234</p></div>', unsafe_allow_html=True)

def logout():
    """로그아웃 처리"""
    if 'user_token' in st.session_state and st.session_state.user_token:
        api_client = PlandyAPIClient()
        api_client.set_token(st.session_state.user_token)
        api_client.logout()
    
    # 세션 상태 초기화
    st.session_state.user_token = None
    st.session_state.user_info = None
    st.session_state.chat_history = []
    st.session_state.session_id = None
    st.session_state.pending_prompt = None
    st.session_state.optimization_proposal = None
    st.session_state.run_optimization = False
    st.rerun()

def get_current_user() -> Optional[dict]:
    """현재 로그인한 사용자 정보 반환"""
    return st.session_state.get('user_info')

def get_api_client() -> PlandyAPIClient:
    """인증된 API 클라이언트 반환"""
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state and st.session_state.user_token:
        api_client.set_token(st.session_state.user_token)
    return api_client
