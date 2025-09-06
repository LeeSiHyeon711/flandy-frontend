"""
Plandy 메인 애플리케이션
AI 일정·워라벨 관리 비서의 Streamlit 대시보드
"""

import streamlit as st
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 컴포넌트 및 유틸리티 임포트
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.chat import render_chat_page
from utils.styling import apply_custom_css, apply_sidebar_width_css
from config.settings import setup_page_config, initialize_session_state

# 페이지 설정
setup_page_config()

# 커스텀 CSS 적용
apply_custom_css()


def main():
    """메인 애플리케이션"""
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바 폭 고정 CSS
    apply_sidebar_width_css()
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 메인 컨텐츠 - 페이지별 표시
    if st.session_state.current_page == "dashboard":
        render_dashboard()
    elif st.session_state.current_page == "chat":
        render_chat_page()


if __name__ == "__main__":
    main()
