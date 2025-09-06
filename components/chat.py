"""
채팅 컴포넌트
채팅 페이지와 관련 기능들을 담당
"""

import streamlit as st


def render_chat_page():
    """채팅 페이지 렌더링"""
    st.markdown(f"## 💬 {st.session_state.selected_conversation}")
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    # 채팅 입력
    user_input = st.chat_input("메시지를 입력하세요...")
    
    if user_input:
        with chat_container:
            # 사용자 메시지
            st.chat_message("user").write(user_input)
            
            # AI 응답 (임시)
            ai_response = get_ai_response(st.session_state.selected_conversation, user_input)
            st.chat_message("assistant").write(ai_response)
    
    # 대시보드로 돌아가기 버튼
    if st.button("🏠 대시보드로 돌아가기"):
        st.session_state.current_page = "dashboard"
        st.rerun()


def get_ai_response(conversation_type, user_input):
    """AI 응답 생성 (임시)"""
    responses = {
        "📅 일정 관리": "안녕하세요! 일정 관리에 대해 도움을 드리겠습니다. 현재는 개발 중인 기능입니다.",
        "⚖️ 워라벨 상담": "워라벨 개선을 위한 상담을 도와드리겠습니다. 현재는 개발 중인 기능입니다.",
        "🎯 목표 설정": "목표 설정에 대해 상담해드리겠습니다. 현재는 개발 중인 기능입니다.",
        "📊 분석 리포트": "분석 리포트에 대해 안내해드리겠습니다. 현재는 개발 중인 기능입니다."
    }
    
    return responses.get(conversation_type, "안녕하세요! 도움을 드리겠습니다. 현재는 개발 중인 기능입니다.")
