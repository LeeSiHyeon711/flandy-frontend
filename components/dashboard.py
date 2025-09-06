"""
대시보드 컴포넌트
메인 대시보드 페이지의 레이아웃과 컨테이너들을 담당
"""

import streamlit as st
from components.charts import create_schedule_chart, create_worklife_gauge, create_category_bar
from utils.data_utils import load_sample_data, calculate_worklife_score


def render_dashboard():
    """대시보드 페이지 렌더링"""
    # 섹션 간 간격 줄이기 CSS
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMarkdown {
        margin-bottom: 0.5rem !important;
    }
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 데이터 로드
    df = load_sample_data()
    worklife_score = calculate_worklife_score(df)
    
    # 차트 생성
    fig, dark_mode_script = create_schedule_chart(df)
    fig_gauge = create_worklife_gauge(worklife_score)
    fig_bar = create_category_bar(df)
    
    # 컨테이너 표시 설정 가져오기
    show_chart = st.session_state.get('show_chart', True)
    show_table = st.session_state.get('show_table', True)
    show_analysis = st.session_state.get('show_analysis', True)
    
    # 활성화된 컨테이너 개수에 따른 레이아웃 결정
    active_containers = [show_chart, show_table, show_analysis]
    active_count = sum(active_containers)
    
    if active_count == 0:
        st.warning("표시할 컨테이너를 선택해주세요!")
    else:
        render_dashboard_layout(show_chart, show_table, show_analysis, 
                              fig, dark_mode_script, fig_gauge, fig_bar, df)


def render_dashboard_layout(show_chart, show_table, show_analysis, 
                          fig, dark_mode_script, fig_gauge, fig_bar, df):
    """대시보드 레이아웃 렌더링"""
    if sum([show_chart, show_table, show_analysis]) == 1:
        render_single_container(show_chart, show_table, show_analysis, 
                              fig, dark_mode_script, fig_gauge, fig_bar, df)
    elif sum([show_chart, show_table, show_analysis]) == 2:
        render_double_container(show_chart, show_table, show_analysis, 
                              fig, dark_mode_script, fig_gauge, fig_bar, df)
    else:
        render_triple_container(show_chart, show_table, show_analysis, 
                              fig, dark_mode_script, fig_gauge, fig_bar, df)


def render_single_container(show_chart, show_table, show_analysis, 
                          fig, dark_mode_script, fig_gauge, fig_bar, df):
    """단일 컨테이너 렌더링"""
    if show_chart:
        render_schedule_chart(fig, dark_mode_script)
    elif show_table:
        render_schedule_table(df)
    elif show_analysis:
        render_worklife_analysis(fig_gauge, fig_bar)


def render_double_container(show_chart, show_table, show_analysis, 
                          fig, dark_mode_script, fig_gauge, fig_bar, df):
    """이중 컨테이너 렌더링"""
    if show_chart and show_table:
        # 차트와 테이블을 가로로 배치
        cols = st.columns(2)
        with cols[0]:
            render_schedule_chart(fig, dark_mode_script)
        with cols[1]:
            render_schedule_table(df)
        
        # 워라벨 분석이 있으면 아래에 배치
        if show_analysis:
            render_worklife_analysis(fig_gauge, fig_bar)
    elif show_chart and show_analysis:
        # 차트와 분석을 가로로 배치
        cols = st.columns(2)
        with cols[0]:
            render_schedule_chart(fig, dark_mode_script)
        with cols[1]:
            render_worklife_analysis(fig_gauge, fig_bar)
    elif show_table and show_analysis:
        # 테이블과 분석을 가로로 배치
        cols = st.columns(2)
        with cols[0]:
            render_schedule_table(df)
        with cols[1]:
            render_worklife_analysis(fig_gauge, fig_bar)


def render_triple_container(show_chart, show_table, show_analysis, 
                          fig, dark_mode_script, fig_gauge, fig_bar, df):
    """삼중 컨테이너 렌더링"""
    # 차트와 테이블+분석을 가로로 배치 (2:1 비율)
    cols = st.columns([2, 1])
    with cols[0]:
        render_schedule_chart(fig, dark_mode_script)
    with cols[1]:
        # 테이블과 분석을 세로로 배치
        render_schedule_table(df)
        render_worklife_analysis(fig_gauge, fig_bar)


def render_schedule_chart(fig, dark_mode_script):
    """일정 차트 렌더링"""
    st.markdown("#### 📊 24시간 생활계획표")
    
    # 차트와 범례를 같은 행에 배치 (차트 왼쪽, 범례 오른쪽)
    cols = st.columns([3, 1])
    
    with cols[0]:
        # 차트를 완전히 고정 크기로 표시 (컬럼 내에서도 고정)
        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})
        st.markdown(dark_mode_script, unsafe_allow_html=True)
    
    with cols[1]:
        # 색깔 범례를 오른쪽에 세로 정렬
        render_color_legend()
    
    # 자동 새로고침 스크립트
    st.markdown("""
    <script>
    setTimeout(function(){
        window.location.reload();
    }, 5000);
    </script>
    """, unsafe_allow_html=True)


def render_schedule_table(df):
    """일정 테이블 렌더링"""
    st.markdown("#### 📋 상세 일정")
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_worklife_analysis(fig_gauge, fig_bar):
    """워라벨 분석 렌더링"""
    st.markdown("#### 📈 워라벨 분석")
    
    # 차트 2개를 가로로 배치 (더 컴팩트하게)
    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    with cols[1]:
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})


def render_color_legend():
    """색깔 범례 렌더링"""
    color_map = {
        "업무": "#4A90E2",      # 플랜디 메인 블루
        "휴식": "#6BCF7F",      # 플랜디 블루와 조화되는 그린
        "개인": "#FF8A65",      # 플랜디 블루와 조화되는 오렌지
        "운동": "#4FC3F7",      # 플랜디 블루 계열 라이트 블루
        "학습": "#81C784",      # 플랜디 블루와 조화되는 라이트 그린
        "기타": "#B0BEC5"       # 플랜디 블루와 조화되는 그레이
    }
    
    # 세로 정렬을 위해 각 항목을 개별적으로 렌더링
    for category, color in color_map.items():
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 3px;">
            <div style="width: 15px; height: 15px; background-color: {color}; 
                        border: 1px solid #ccc; border-radius: 3px; margin-right: 8px;"></div>
            <span style="font-size: 12px;">{category}</span>
        </div>
        """, unsafe_allow_html=True)
