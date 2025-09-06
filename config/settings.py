"""
앱 설정
Streamlit 앱의 기본 설정들
"""

import streamlit as st

# 페이지 설정
PAGE_CONFIG = {
    "page_title": "Plandy - AI 일정 관리 비서",
    "page_icon": "assets/plandy-logo.png",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 기본 세션 상태
DEFAULT_SESSION_STATE = {
    "current_page": "dashboard",
    "show_chart": True,
    "show_table": True,
    "show_analysis": True
}

def initialize_session_state():
    """세션 상태 초기화"""
    for key, value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value

def setup_page_config():
    """페이지 설정 적용"""
    st.set_page_config(**PAGE_CONFIG)