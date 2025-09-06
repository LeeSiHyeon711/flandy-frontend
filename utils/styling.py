"""
스타일링 유틸리티
CSS 스타일과 테마 관련 함수들
"""

import streamlit as st


def apply_custom_css():
    """커스텀 CSS 적용"""
    st.markdown("""
    <style>
        /* 다크모드 지원을 위한 CSS 변수 */
        :root {
            --text-color: #666;
            --chart-bg-color: rgba(255,255,255,0.9);
            --chart-center-text: #333333;
        }
        
        /* 다크모드 감지 및 변수 재정의 */
        @media (prefers-color-scheme: dark) {
            :root {
                --text-color: #ccc;
                --chart-bg-color: rgba(30,30,30,0.9);
                --chart-center-text: #ffffff;
            }
        }
        
        /* Streamlit 다크모드 클래스 감지 */
        .stApp[data-theme="dark"] {
            --text-color: #ccc !important;
            --chart-bg-color: rgba(30,30,30,0.9) !important;
            --chart-center-text: #ffffff !important;
        }
        
        .worklife-score {
            font-size: 2rem;
            font-weight: bold;
            color: #4A90E2;
        }
        .stSidebar > div:first-child > div:first-child {
            padding-top: 1rem;
        }
        /* 사이드바 로고 이미지 여백 제거 */
        .stSidebar img {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
        }
        /* 사이드바 로고 컨테이너 여백 제거 */
        .stSidebar .stImage > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* 차트 배경 투명화 및 완벽한 원형 강제 */
        .js-plotly-plot {
            background: transparent !important;
        }
        /* 생활계획표 차트를 완벽한 원형으로 강제 */
        .js-plotly-plot .plotly {
            width: 600px !important;
            height: 600px !important;
            max-width: 600px !important;
            max-height: 600px !important;
        }
        /* 차트 컨테이너 중앙 정렬 */
        .stPlotlyChart {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        /* 다크모드에서 컨테이너 박스 제거 */
        .stMetric {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        /* 다크모드 호환을 위한 전역 스타일 제거 */
        .stApp {
            background: transparent !important;
        }
        /* 드래그 가능한 컨테이너 스타일 */
        .draggable-container {
            cursor: move;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            border-radius: 8px;
            padding: 10px;
            margin: 5px 0;
        }
        .draggable-container:hover {
            border-color: #4A90E2;
            background-color: rgba(74, 144, 226, 0.1);
        }
        .draggable-container.dragging {
            opacity: 0.5;
            transform: rotate(5deg);
        }
        /* 클릭하지 않은 대화방 버튼에 빨간색 점 표시 */
        .stButton > button[data-testid="baseButton-secondary"]:nth-of-type(2)::after,
        .stButton > button[data-testid="baseButton-secondary"]:nth-of-type(3)::after,
        .stButton > button[data-testid="baseButton-secondary"]:nth-of-type(4)::after {
            content: "";
            position: absolute;
            top: 8px;
            right: 8px;
            width: 8px;
            height: 8px;
            background-color: #ff4444;
            border-radius: 50%;
            z-index: 10;
        }
    </style>
    """, unsafe_allow_html=True)


def apply_sidebar_width_css():
    """사이드바 폭 고정 CSS 적용"""
    st.markdown("""
    <style>
    .css-1d391kg {
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    .css-1cypcdb {
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    </style>
    """, unsafe_allow_html=True)
