"""
스타일링 유틸리티
CSS 변수 기반 다크/라이트 테마 시스템
"""

import streamlit as st
from config.constants import THEME_DARK, THEME_LIGHT


def apply_custom_css():
    """테마 기반 CSS 변수 + 공통 컴포넌트 스타일 주입"""
    theme = st.session_state.get('theme', 'dark')
    palette = THEME_DARK if theme == 'dark' else THEME_LIGHT

    vars_css = "\n".join(f"    --{k.replace('_', '-')}: {v};" for k, v in palette.items())

    st.markdown(f"""
    <style>
        :root {{
            {vars_css}
        }}

        .stApp {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
        }}

        /* ── 공통 카드 ── */
        .flandy-card {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }}
        .flandy-card h3, .flandy-card h4 {{
            color: var(--text-primary);
            margin: 0;
        }}
        .flandy-card p {{
            color: var(--text-secondary);
            margin: 0.5rem 0;
        }}

        /* ── 메트릭 카드 ── */
        .flandy-metric {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
        }}
        .flandy-metric .label {{
            color: var(--text-secondary);
            margin: 0;
            font-size: 0.85rem;
        }}
        .flandy-metric .value {{
            color: var(--text-primary);
            margin: 0.25rem 0;
        }}

        /* ── 채팅 버블 ── */
        .chat-user {{
            background-color: var(--accent);
            color: #FFFFFF;
            padding: 0.75rem 1rem;
            border-radius: 18px 18px 4px 18px;
            display: inline-block;
            max-width: 85%;
            word-wrap: break-word;
        }}
        .chat-ai {{
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border);
            padding: 0.75rem 1rem;
            border-radius: 18px 18px 18px 4px;
            display: inline-block;
            max-width: 85%;
            word-wrap: break-word;
        }}

        /* ── 진행률 바 ── */
        .progress-bar-bg {{
            background-color: var(--bg-primary);
            border-radius: 8px;
            height: 12px;
            overflow: hidden;
        }}
        .progress-bar-fill {{
            background-color: var(--accent);
            height: 100%;
            border-radius: 8px;
            transition: width 0.3s ease;
        }}

        /* ── 채팅 영역 너비 ── */
        .stChatMessage {{
            max-width: 100%;
        }}
        .stChatInput {{
            max-width: 100%;
        }}
        .stChatMessage p {{
            max-width: 100%;
        }}

        /* ── Streamlit 오버라이드 ── */
        .stSidebar > div:first-child > div:first-child {{
            padding-top: 1rem;
        }}
        .stSidebar img {{
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
        }}
        .js-plotly-plot {{
            background: transparent !important;
        }}
        .stPlotlyChart {{
            display: flex !important;
            justify-content: center !important;
        }}
        .stMetric {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)
