"""
Plandy 메인 애플리케이션
AI 일정·워라벨 관리 비서의 Streamlit 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import json
import os

# 페이지 설정
st.set_page_config(
    page_title="Plandy - AI 일정 관리 비서",
    page_icon="assets/plandy-logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 플랜디 테마 (다크모드 호환 + 드래그 기능)
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
    /* 차트 배경 투명화 */
    .js-plotly-plot {
        background: transparent !important;
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

def load_sample_data():
    """샘플 데이터 로드"""
    sample_schedule = [
        {"time": "09:00", "task": "아침 회의", "category": "업무", "duration": 60},
        {"time": "10:00", "task": "프로젝트 A 작업", "category": "업무", "duration": 120},
        {"time": "12:00", "task": "점심 식사", "category": "휴식", "duration": 60},
        {"time": "13:00", "task": "프로젝트 B 작업", "category": "업무", "duration": 90},
        {"time": "14:30", "task": "커피 브레이크", "category": "휴식", "duration": 15},
        {"time": "14:45", "task": "이메일 확인", "category": "업무", "duration": 30},
        {"time": "15:15", "task": "팀 미팅", "category": "업무", "duration": 45},
        {"time": "16:00", "task": "개인 업무", "category": "업무", "duration": 60},
        {"time": "17:00", "task": "하루 마무리", "category": "업무", "duration": 30},
    ]
    return pd.DataFrame(sample_schedule)

def create_schedule_chart(df):
    """일정 차트 생성 - 24시간 원형 생활계획표 (새로운 방식)"""
    # 플랜디 로고 색상 기반 통일된 색상 팔레트
    color_map = {
        "업무": "#4A90E2",      # 플랜디 메인 블루
        "휴식": "#6BCF7F",      # 플랜디 블루와 조화되는 그린
        "개인": "#FF8A65",      # 플랜디 블루와 조화되는 오렌지
        "운동": "#4FC3F7",      # 플랜디 블루 계열 라이트 블루
        "학습": "#81C784",      # 플랜디 블루와 조화되는 라이트 그린
        "기타": "#B0BEC5"       # 플랜디 블루와 조화되는 그레이
    }
    
    # 24시간을 24개 구간으로 나누기 (각 1시간)
    hours = list(range(24))
    
    # 각 시간대별 카테고리와 태스크 정보 저장
    hour_data = {}
    for hour in hours:
        hour_data[hour] = {
            'category': '기타',
            'task': '',
            'color': color_map['기타']
        }
    
    # 실제 일정 데이터를 시간대에 매핑
    for _, row in df.iterrows():
        start_time = datetime.strptime(row['time'], '%H:%M')
        end_time = start_time + timedelta(minutes=row['duration'])
        
        start_hour = start_time.hour
        end_hour = end_time.hour
        
        # 시작 시간부터 종료 시간까지의 모든 시간대에 일정 정보 저장
        for hour in range(start_hour, min(end_hour + 1, 24)):
            if hour in hour_data:
                hour_data[hour] = {
                    'category': row['category'],
                    'task': row['task'],
                    'color': color_map.get(row['category'], color_map['기타'])
                }
    
    # 새로운 방식: Pie 차트를 사용하여 원형 차트 생성
    fig = go.Figure()
    
    # 각 시간대별 데이터 준비
    values = [1] * 24  # 모든 섹터가 동일한 크기
    labels = [f"{hour:02d}" for hour in hours]
    colors = [hour_data[hour]['color'] for hour in hours]
    customdata = [[hour_data[hour]['category'], hour_data[hour]['task'] if hour_data[hour]['task'] else '없음'] for hour in hours]
    
    # Pie 차트 생성
    fig.add_trace(go.Pie(
        values=values,
        labels=labels,
        customdata=customdata,
        marker=dict(
            colors=colors,
            line=dict(color='white', width=2)
        ),
        textinfo='none',  # 숫자 표시 제거
        hovertemplate='<b>🕐 %{label}:00</b><br>' +
                     '<b>📋 카테고리:</b> %{customdata[0]}<br>' +
                     '<b>📝 일정:</b> %{customdata[1]}<br>' +
                     '<b>⏰ 시간대:</b> %{label}:00 ~ %{label}:59<extra></extra>',
        direction='clockwise',
        sort=False
    ))
    
    # 현재 시간 표시
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    
    # 레이아웃 설정 - 고정 크기로 완벽한 원형 유지
    fig.update_layout(
        showlegend=False,
        width=600,  # 고정 너비
        height=600,  # 고정 높이 (정사각형으로 설정)
        margin=dict(l=10, r=10, t=20, b=10),  # 여백 최소화
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=False  # 자동 크기 조정 비활성화
    )
    
    # 중앙에 현재 시간 표시 (원형)
    current_second = datetime.now().second
    current_time_str = f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}"
    
    # 다크모드 감지를 위한 JavaScript 함수
    dark_mode_script = """
    <script>
    function updateChartColors() {
        const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark' || 
                          window.matchMedia('(prefers-color-scheme: dark)').matches ||
                          document.body.classList.contains('dark');
        
        const chartElements = document.querySelectorAll('.js-plotly-plot');
        chartElements.forEach(chart => {
            const plotlyDiv = chart.querySelector('.plotly');
            if (plotlyDiv && plotlyDiv.data) {
                // 차트 중앙 원형 배경 색상 업데이트
                if (plotlyDiv.layout && plotlyDiv.layout.shapes) {
                    plotlyDiv.layout.shapes.forEach(shape => {
                        if (shape.type === 'circle') {
                            shape.fillcolor = isDarkMode ? 'rgba(30,30,30,0.9)' : 'rgba(255,255,255,0.9)';
                        }
                    });
                }
                
                // 차트 중앙 텍스트 색상 업데이트
                if (plotlyDiv.layout && plotlyDiv.layout.annotations) {
                    plotlyDiv.layout.annotations.forEach(annotation => {
                        if (annotation.text && annotation.text.includes('현재 시간')) {
                            annotation.font.color = isDarkMode ? '#ffffff' : '#333333';
                        }
                    });
                }
                
                // 차트 업데이트
                Plotly.redraw(plotlyDiv);
            }
        });
    }
    
    // 페이지 로드 시 실행
    document.addEventListener('DOMContentLoaded', updateChartColors);
    
    // 다크모드 변경 감지
    const observer = new MutationObserver(updateChartColors);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });
    
    // 미디어 쿼리 변경 감지
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateChartColors);
    </script>
    """
    
    # 완전한 원형 배경을 위한 원 추가
    fig.add_shape(
        type="circle",
        xref="paper", yref="paper",
        x0=0.35, y0=0.35, x1=0.65, y1=0.65,
        line=dict(color="#cccccc", width=2),
        fillcolor="rgba(255,255,255,0.9)"
    )
    
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text=f"<b>현재 시간</b><br>{current_time_str}",
        showarrow=False,
        font=dict(size=16, color='#333333'),
        align="center",
        valign="middle"
    )
    
    return fig, dark_mode_script

def calculate_worklife_score(df):
    """워라벨 점수 계산"""
    work_time = df[df['category'] == '업무']['duration'].sum()
    rest_time = df[df['category'] == '휴식']['duration'].sum()
    total_time = df['duration'].sum()
    
    if total_time == 0:
        return 0
    
    work_ratio = work_time / total_time
    rest_ratio = rest_time / total_time
    
    # 워라벨 점수 계산 (업무 60%, 휴식 40% 기준)
    ideal_work_ratio = 0.6
    ideal_rest_ratio = 0.4
    
    work_score = max(0, 100 - abs(work_ratio - ideal_work_ratio) * 200)
    rest_score = max(0, 100 - abs(rest_ratio - ideal_rest_ratio) * 200)
    
    return int((work_score + rest_score) / 2)

def main():
    """메인 애플리케이션"""
    
    # 사이드바 폭 고정 CSS
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
    
    # 사이드바
    with st.sidebar:
        # 플랜디 로고 (가운데 정렬, 고정 크기)
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            st.image("assets/plandy.png", width=180)

        st.markdown('<p style="text-align: center; color: var(--text-color, #666); font-size: 16px; margin: 5px 5px 15px 5px;">"계획은 유연하게, 하루는 완벽하게!"</p>', unsafe_allow_html=True)
        
        # 오늘의 현황을 드롭다운으로 변경
        with st.expander("📊 오늘의 현황", expanded=True):
            # 현재 시간 표시
            current_time = datetime.now().strftime("%H:%M")
            st.metric("현재 시간", current_time)
            
            # 워라벨 점수
            df = load_sample_data()
            worklife_score = calculate_worklife_score(df)
            
            # 워라벨 점수를 다크모드 호환으로 표시
            st.markdown("**워라벨 점수**")
            st.markdown(f"""
            <div style="text-align: center; margin: 0.5rem 0;">
                <div style="font-size: 2rem; font-weight: bold; color: #4A90E2; line-height: 1.2;">{worklife_score}/100</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 완료된 일정을 마지막에 표시
            completed_tasks = len(df[df['time'] <= current_time])
            total_tasks = len(df)
            progress = completed_tasks / total_tasks if total_tasks > 0 else 0
            st.progress(progress)
            st.caption(f"완료된 일정: {completed_tasks}/{total_tasks}")
        
        # 컨테이너 표시 설정 (드롭다운)
        with st.expander("🎛️ 컨테이너 표시 설정", expanded=False):
            # 각 컨테이너 토글
            show_chart = st.checkbox("📊 24시간 생활계획표", value=True, key="show_chart")
            show_table = st.checkbox("📋 상세 일정", value=True, key="show_table") 
            show_analysis = st.checkbox("📈 워라벨 분석", value=True, key="show_analysis")
        
        # 대화 목록
        st.header("💬 대화 목록")
        
        # 대화방 목록
        conversations = [
            {"name": "📅 일정 관리", "last_msg": "오늘 일정을 확인해주세요", "clicked": True},
            {"name": "⚖️ 워라벨 상담", "last_msg": "워라벨 점수를 개선해보세요", "clicked": False},
            {"name": "🎯 목표 설정", "last_msg": "이번 주 목표를 설정해보세요", "clicked": False},
            {"name": "📊 분석 리포트", "last_msg": "주간 리포트를 확인하세요", "clicked": False}
        ]
        
        for conv in conversations:
            button_text = f"{conv['name']}\n{conv['last_msg']}"
            
            if st.button(button_text, key=f"conv_{conv['name']}", use_container_width=True):
                st.session_state.current_page = "chat"
                st.session_state.selected_conversation = conv['name']
                st.rerun()
    
    # 페이지 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # 메인 컨텐츠 - 페이지별 표시
    if st.session_state.current_page == "dashboard":
        # 대시보드 페이지
        # 차트 생성 (토글에 따라 조건부로 사용)
        fig, dark_mode_script = create_schedule_chart(df)
        
        # 워라벨 점수 게이지 생성 (통일된 색상)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = worklife_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "워라벨 점수"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4A90E2"},  # 플랜디 메인 블루
                'steps': [
                    {'range': [0, 50], 'color': "#B0BEC5"},  # 통일된 그레이
                    {'range': [50, 80], 'color': "#FF8A65"},  # 통일된 오렌지
                    {'range': [80, 100], 'color': "#6BCF7F"}  # 통일된 그린
                ],
                'threshold': {
                    'line': {'color': "#4A90E2", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=250)  # 크기 복원
        
        # 카테고리별 시간 분석 (통일된 색상)
        category_time = df.groupby('category')['duration'].sum()
        fig_pie = px.pie(
            values=category_time.values,
            names=category_time.index,
            color_discrete_map={
                "업무": "#4A90E2",      # 플랜디 메인 블루
                "휴식": "#6BCF7F",      # 플랜디 블루와 조화되는 그린
                "개인": "#FF8A65",      # 플랜디 블루와 조화되는 오렌지
                "운동": "#4FC3F7",      # 플랜디 블루 계열 라이트 블루
                "학습": "#81C784",      # 플랜디 블루와 조화되는 라이트 그린
                "기타": "#B0BEC5"       # 플랜디 블루와 조화되는 그레이
            }
        )
        fig_pie.update_layout(height=250)  # 크기 복원
        
        # 활성화된 컨테이너 개수에 따른 레이아웃 결정
        active_containers = [show_chart, show_table, show_analysis]
        active_count = sum(active_containers)
        
        if active_count == 0:
            st.warning("표시할 컨테이너를 선택해주세요!")
        else:
            # 활성화된 컨테이너만 표시
            if active_count == 1:
                # 1개만 활성화된 경우 전체 너비 사용
                if show_chart:
                    st.markdown("#### 📊 24시간 생활계획표")
                
                    # 색깔 범례 (생활계획표 컨테이너 내부)
                    color_map = {
                        "업무": "#4A90E2",      # 플랜디 메인 블루
                        "휴식": "#6BCF7F",      # 플랜디 블루와 조화되는 그린
                        "개인": "#FF8A65",      # 플랜디 블루와 조화되는 오렌지
                        "운동": "#4FC3F7",      # 플랜디 블루 계열 라이트 블루
                        "학습": "#81C784",      # 플랜디 블루와 조화되는 라이트 그린
                        "기타": "#B0BEC5"       # 플랜디 블루와 조화되는 그레이
                    }
                    
                    legend_cols = st.columns(6)
                    for i, (category, color) in enumerate(color_map.items()):
                        with legend_cols[i]:
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                <div style="width: 15px; height: 15px; background-color: {color}; 
                                            border: 1px solid #ccc; border-radius: 3px; margin-right: 5px;"></div>
                                <span style="font-size: 11px;">{category}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 원형 차트를 중앙에 배치하고 고정 크기로 표시
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})
                        st.markdown(dark_mode_script, unsafe_allow_html=True)
                    st.markdown("""
                    <script>
                    setTimeout(function(){
                        window.location.reload();
                    }, 5000);
                    </script>
                    """, unsafe_allow_html=True)
                elif show_table:
                    st.markdown("#### 📋 상세 일정")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                elif show_analysis:
                    st.markdown("#### 📈 워라벨 분석")
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            elif active_count == 2:
                # 2개 활성화된 경우 1:1 비율
                cols = st.columns(2)
                col_idx = 0
                
                if show_chart:
                    with cols[col_idx]:
                        st.markdown("#### 📊 24시간 생활계획표")
                    
                        # 색깔 범례 (생활계획표 컨테이너 내부)
                        color_map = {
                            "업무": "#4A90E2",      # 플랜디 메인 블루
                            "휴식": "#6BCF7F",      # 플랜디 블루와 조화되는 그린
                            "개인": "#FF8A65",      # 플랜디 블루와 조화되는 오렌지
                            "운동": "#4FC3F7",      # 플랜디 블루 계열 라이트 블루
                            "학습": "#81C784",      # 플랜디 블루와 조화되는 라이트 그린
                            "기타": "#B0BEC5"       # 플랜디 블루와 조화되는 그레이
                        }
                        
                        legend_cols = st.columns(6)
                        for i, (category, color) in enumerate(color_map.items()):
                            with legend_cols[i]:
                                st.markdown(f"""
                                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                    <div style="width: 15px; height: 15px; background-color: {color}; 
                                                border: 1px solid #ccc; border-radius: 3px; margin-right: 5px;"></div>
                                    <span style="font-size: 11px;">{category}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})
                        st.markdown(dark_mode_script, unsafe_allow_html=True)
                        st.markdown("""
                        <script>
                        setTimeout(function(){
                            window.location.reload();
                        }, 5000);
                        </script>
                        """, unsafe_allow_html=True)
                    col_idx += 1
                
                if show_table:
                    with cols[col_idx]:
                        st.markdown("#### 📋 상세 일정")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    col_idx += 1
                
                if show_analysis:
                    with cols[col_idx]:
                        st.markdown("#### 📈 워라벨 분석")
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        st.plotly_chart(fig_pie, use_container_width=True)
            
            else:
                # 3개 모두 활성화된 경우 2:1.5:0.8 비율 (워라벨 분석 공간 축소)
                cols = st.columns([2, 1.5, 0.8])
                col_idx = 0
                
                if show_chart:
                    with cols[col_idx]:
                        st.markdown("#### 📊 24시간 생활계획표")
                        
                        # 색깔 범례 (생활계획표 컨테이너 내부)
                        color_map = {
                            "업무": "#4A90E2",      # 플랜디 메인 블루
                            "휴식": "#6BCF7F",      # 플랜디 블루와 조화되는 그린
                            "개인": "#FF8A65",      # 플랜디 블루와 조화되는 오렌지
                            "운동": "#4FC3F7",      # 플랜디 블루 계열 라이트 블루
                            "학습": "#81C784",      # 플랜디 블루와 조화되는 라이트 그린
                            "기타": "#B0BEC5"       # 플랜디 블루와 조화되는 그레이
                        }
                        
                        legend_cols = st.columns(6)
                        for i, (category, color) in enumerate(color_map.items()):
                            with legend_cols[i]:
                                st.markdown(f"""
                                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                    <div style="width: 15px; height: 15px; background-color: {color}; 
                                                border: 1px solid #ccc; border-radius: 3px; margin-right: 5px;"></div>
                                    <span style="font-size: 11px;">{category}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})
                        st.markdown(dark_mode_script, unsafe_allow_html=True)
                        st.markdown("""
                        <script>
                        setTimeout(function(){
                            window.location.reload();
                        }, 5000);
                        </script>
                        """, unsafe_allow_html=True)
                    col_idx += 1
                
                if show_table:
                    with cols[col_idx]:
                        st.markdown("#### 📋 상세 일정")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    col_idx += 1
                
                if show_analysis:
                    with cols[col_idx]:
                        st.markdown("#### 📈 워라벨 분석")
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        st.plotly_chart(fig_pie, use_container_width=True)
    
    elif st.session_state.current_page == "chat":
        # 채팅 페이지
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
                ai_response = f"안녕하세요! {st.session_state.selected_conversation}에 대해 도움을 드리겠습니다. 현재는 개발 중인 기능입니다."
                st.chat_message("assistant").write(ai_response)
        
        # 대시보드로 돌아가기 버튼
        if st.button("🏠 대시보드로 돌아가기"):
            st.session_state.current_page = "dashboard"
            st.rerun()


if __name__ == "__main__":
    main()
