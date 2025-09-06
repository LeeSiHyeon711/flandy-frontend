import streamlit as st
import sys
import os

# 현재 파일의 디렉토리 경로
current_dir = os.path.dirname(os.path.abspath(__file__))
# 프로젝트 루트 디렉토리 (src의 상위 디렉토리)
project_root = os.path.dirname(current_dir)

# 잘못된 경로들을 제거
paths_to_remove = []
for path in sys.path:
    if 'src/app.py' in path or path == current_dir:
        paths_to_remove.append(path)

for path in paths_to_remove:
    sys.path.remove(path)

# 프로젝트 루트를 Python 경로에 추가
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 현재 작업 디렉토리를 프로젝트 루트로 변경
os.chdir(project_root)

try:
    from components.sidebar import show_sidebar
    from pages.dashboard import show_dashboard
    from pages.tasks import show_tasks
    from pages.schedule import show_schedule
    from pages.worklife import show_worklife
    from pages.ai_assistant import show_ai_assistant
    from components.auth import check_auth_status
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.error(f"현재 작업 디렉토리: {os.getcwd()}")
    st.error(f"Python 경로: {sys.path[:3]}")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="Plandy - AI 생산성 관리",
    page_icon="assets/plandy-icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF2D20;
        text-align: center;
        margin-bottom: 2rem;
    }
    .task-card {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #F9FAFB;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF2D20;
    }
    .success-message {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid #A7F3D0;
    }
    .error-message {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid #FECACA;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 사이드바에서 페이지 선택
    selected_page = show_sidebar()
    
    # 인증 상태 확인
    if not check_auth_status():
        # 로그인되지 않은 상태: 서비스 소개 페이지 표시
        from components.auth import show_login_page
        show_login_page()
        return
    
    # 선택된 페이지에 따라 콘텐츠 표시
    if selected_page == "대시보드":
        show_dashboard()
    elif selected_page == "태스크 관리":
        show_tasks()
    elif selected_page == "스케줄 관리":
        show_schedule()
    elif selected_page == "워라밸 분석":
        show_worklife()
    elif selected_page == "AI 어시스턴트":
        show_ai_assistant()
    elif selected_page is None:
        pass

if __name__ == "__main__":
    main()