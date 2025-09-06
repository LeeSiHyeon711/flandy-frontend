"""
차트 컴포넌트
다양한 차트 생성 함수들을 담당
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta


def create_schedule_chart(df):
    """일정 차트 생성 - 24시간 원형 생활계획표"""
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
    
    # Pie 차트를 사용하여 원형 차트 생성
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
        sort=False,
        scalegroup='one'  # 비율 조정 비활성화
    ))
    
    # 현재 시간 표시
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    current_second = datetime.now().second
    current_time_str = f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}"
    
    # 레이아웃 설정 - 고정 크기로 완벽한 원형 유지
    fig.update_layout(
        showlegend=False,
        width=600,  # 고정 너비
        height=600,  # 고정 높이 (정확한 정사각형)
        margin=dict(l=10, r=10, t=20, b=10),  # 최소 여백
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=False,  # 자동 크기 조정 비활성화
        uniformtext_minsize=12,
        uniformtext_mode='hide'
    )
    
    # 완전한 원형 배경을 위한 원 추가 (정확한 원형)
    fig.add_shape(
        type="circle",
        xref="paper", yref="paper",
        x0=0.4, y0=0.4, x1=0.6, y1=0.6,
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
    
    # 다크모드 감지를 위한 JavaScript 함수
    dark_mode_script = get_dark_mode_script()
    
    return fig, dark_mode_script


def create_worklife_gauge(worklife_score):
    """워라벨 점수 게이지 생성"""
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = worklife_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': ""},
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
    fig_gauge.update_layout(height=300)
    
    return fig_gauge


def create_category_bar(df):
    """카테고리별 시간 분석 막대 차트 생성"""
    category_time = df.groupby('category')['duration'].sum()
    
    fig_bar = go.Figure(data=[
        go.Bar(
            x=category_time.index,
            y=category_time.values,
            marker=dict(
                color=[
                    "#4A90E2" if cat == "업무" else
                    "#6BCF7F" if cat == "휴식" else
                    "#FF8A65" if cat == "개인" else
                    "#4FC3F7" if cat == "운동" else
                    "#81C784" if cat == "학습" else
                    "#B0BEC5"
                    for cat in category_time.index
                ]
            ),
            text=[f"{val}분" for val in category_time.values],
            textposition='auto',
        )
    ])
    
    fig_bar.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="",
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig_bar


def get_dark_mode_script():
    """다크모드 감지 JavaScript 스크립트"""
    return """
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
