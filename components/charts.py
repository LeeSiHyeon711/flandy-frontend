"""
차트 컴포넌트
다양한 차트 생성 함수들을 담당
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from config.constants import THEME_DARK, THEME_LIGHT, CATEGORY_COLORS


def get_chart_colors():
    theme = st.session_state.get('theme', 'dark')
    palette = THEME_DARK if theme == 'dark' else THEME_LIGHT
    return {
        'font_color': palette['text_primary'],
        'grid_color': palette['border'],
        'muted_color': palette['text_secondary'],
        'accent_color': palette['accent'],
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
    }


def create_schedule_chart(df):
    """일정 차트 생성 - 수평 바 차트로 시간 블록 표시"""
    color_map = CATEGORY_COLORS

    # 각 시간대별 카테고리와 태스크 정보 저장
    hour_data = {}
    for hour in range(24):
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

        for hour in range(start_hour, min(end_hour + 1, 24)):
            if hour in hour_data:
                hour_data[hour] = {
                    'category': row['category'],
                    'task': row['task'],
                    'color': color_map.get(row['category'], color_map['기타'])
                }

    # 수평 바 차트 생성
    fig = go.Figure()

    # 카테고리별로 그룹화하여 바 추가
    categories_seen = {}
    for hour in range(24):
        cat = hour_data[hour]['category']
        color = hour_data[hour]['color']
        task = hour_data[hour]['task'] if hour_data[hour]['task'] else '없음'
        show_legend = cat not in categories_seen
        categories_seen[cat] = True

        fig.add_trace(go.Bar(
            y=['일정'],
            x=[1],
            orientation='h',
            name=cat if show_legend else None,
            showlegend=show_legend,
            marker=dict(color=color),
            hovertemplate=f'<b>{hour:02d}:00</b><br>'
                         f'카테고리: {cat}<br>'
                         f'일정: {task}<extra></extra>',
            legendgroup=cat,
        ))

    # 현재 시간 표시
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    current_time_str = f"{current_hour:02d}:{current_minute:02d}"

    colors = get_chart_colors()

    fig.update_layout(
        barmode='stack',
        showlegend=True,
        width=600,
        height=120,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor=colors['paper_bgcolor'],
        plot_bgcolor=colors['plot_bgcolor'],
        font=dict(color=colors['font_color']),
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.3,
            xanchor='center',
            x=0.5,
            font=dict(color=colors['muted_color'], size=11),
        ),
        title=dict(
            text=f'24시간 타임라인 (현재: {current_time_str})',
            font=dict(color=colors['font_color'], size=14),
        ),
    )

    return fig


def create_category_bar(df):
    """카테고리별 시간 분석 막대 차트 생성"""
    colors = get_chart_colors()

    category_time = df.groupby('category')['duration'].sum()

    fig_bar = go.Figure(data=[
        go.Bar(
            x=category_time.index,
            y=category_time.values,
            marker=dict(
                color=[CATEGORY_COLORS.get(cat, "#64748B") for cat in category_time.index]
            ),
            text=[f"{val}분" for val in category_time.values],
            textposition='auto',
            textfont=dict(color=colors['font_color']),
        )
    ])

    fig_bar.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="",
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor=colors['paper_bgcolor'],
        plot_bgcolor=colors['plot_bgcolor'],
        font=dict(color=colors['font_color']),
        xaxis=dict(gridcolor=colors['grid_color']),
        yaxis=dict(gridcolor=colors['grid_color']),
    )

    return fig_bar


def create_burndown_chart(burndown_data, sprint_name=""):
    """번다운 차트 생성 - 남은 스토리 포인트와 이상적 라인 표시"""
    if not burndown_data:
        return go.Figure()

    colors = get_chart_colors()

    dates = [item.get('date', '') for item in burndown_data]
    remaining = [item.get('remaining', 0) for item in burndown_data]
    ideal = [item.get('ideal', 0) for item in burndown_data]

    fig = go.Figure()

    # 이상적 라인 (점선)
    fig.add_trace(go.Scatter(
        x=dates,
        y=ideal,
        mode='lines',
        name='이상적',
        line=dict(color=colors['muted_color'], width=2, dash='dash'),
        hovertemplate='날짜: %{x}<br>이상적: %{y}pt<extra></extra>',
    ))

    # 실제 남은 포인트 라인
    fig.add_trace(go.Scatter(
        x=dates,
        y=remaining,
        mode='lines+markers',
        name='남은 포인트',
        line=dict(color=colors['accent_color'], width=3),
        marker=dict(size=6, color=colors['accent_color']),
        hovertemplate='날짜: %{x}<br>남은: %{y}pt<extra></extra>',
    ))

    fig.update_layout(
        title=dict(
            text=f'번다운 차트' + (f' - {sprint_name}' if sprint_name else ''),
            font=dict(color=colors['font_color'], size=14),
        ),
        xaxis=dict(
            title=dict(text='날짜', font=dict(color=colors['muted_color'])),
            gridcolor=colors['grid_color'],
            tickfont=dict(color=colors['muted_color']),
        ),
        yaxis=dict(
            title=dict(text='스토리 포인트', font=dict(color=colors['muted_color'])),
            gridcolor=colors['grid_color'],
            tickfont=dict(color=colors['muted_color']),
        ),
        height=350,
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor=colors['paper_bgcolor'],
        plot_bgcolor=colors['plot_bgcolor'],
        font=dict(color=colors['font_color']),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.2,
            xanchor='center',
            x=0.5,
            font=dict(color=colors['muted_color'], size=11),
        ),
        hovermode='x unified',
    )

    return fig


def create_task_status_chart(status_counts):
    """태스크 상태별 분포 수평 바 차트 생성"""
    from config.constants import STATUS_COLORS

    chart_colors = get_chart_colors()

    status_labels = {
        'pending': '대기',
        'in_progress': '진행중',
        'completed': '완료',
        'cancelled': '취소',
    }

    labels = []
    values = []
    bar_colors = []

    for key in ['pending', 'in_progress', 'completed', 'cancelled']:
        count = status_counts.get(key, 0)
        labels.append(status_labels.get(key, key))
        values.append(count)
        bar_colors.append(STATUS_COLORS.get(key, chart_colors['muted_color']))

    fig = go.Figure(data=[
        go.Bar(
            y=labels,
            x=values,
            orientation='h',
            marker=dict(color=bar_colors),
            text=[str(v) for v in values],
            textposition='auto',
            textfont=dict(color=chart_colors['font_color']),
            hovertemplate='%{y}: %{x}개<extra></extra>',
        )
    ])

    fig.update_layout(
        title=dict(
            text='상태별 태스크 수',
            font=dict(color=chart_colors['font_color'], size=14),
        ),
        xaxis=dict(
            title=dict(text='태스크 수', font=dict(color=chart_colors['muted_color'])),
            gridcolor=chart_colors['grid_color'],
            tickfont=dict(color=chart_colors['muted_color']),
        ),
        yaxis=dict(
            tickfont=dict(color=chart_colors['muted_color']),
            autorange='reversed',
        ),
        height=300,
        margin=dict(l=80, r=20, t=40, b=40),
        paper_bgcolor=chart_colors['paper_bgcolor'],
        plot_bgcolor=chart_colors['plot_bgcolor'],
        font=dict(color=chart_colors['font_color']),
        showlegend=False,
    )

    return fig


def create_member_workload_chart(member_workload):
    """멤버별 워크로드 수평 바 차트 생성"""
    if not member_workload:
        return go.Figure()

    colors = get_chart_colors()

    names = [m.get('name', '알 수 없음') for m in member_workload]
    task_counts = [m.get('total', m.get('task_count', 0)) for m in member_workload]

    fig = go.Figure(data=[
        go.Bar(
            y=names,
            x=task_counts,
            orientation='h',
            marker=dict(color=colors['accent_color']),
            text=[str(v) for v in task_counts],
            textposition='auto',
            textfont=dict(color=colors['font_color']),
            hovertemplate='%{y}: %{x}개 태스크<extra></extra>',
        )
    ])

    fig.update_layout(
        title=dict(
            text='멤버별 태스크 수',
            font=dict(color=colors['font_color'], size=14),
        ),
        xaxis=dict(
            title=dict(text='태스크 수', font=dict(color=colors['muted_color'])),
            gridcolor=colors['grid_color'],
            tickfont=dict(color=colors['muted_color']),
        ),
        yaxis=dict(
            tickfont=dict(color=colors['muted_color']),
            autorange='reversed',
        ),
        height=max(200, len(names) * 40 + 100),
        margin=dict(l=100, r=20, t=40, b=40),
        paper_bgcolor=colors['paper_bgcolor'],
        plot_bgcolor=colors['plot_bgcolor'],
        font=dict(color=colors['font_color']),
        showlegend=False,
    )

    return fig


def create_velocity_chart(sprints_data):
    """스프린트별 벨로시티 바 차트 생성 - 완료된 스토리 포인트"""
    if not sprints_data:
        return go.Figure()

    colors = get_chart_colors()

    names = [s.get('name', '이름 없음') for s in sprints_data]
    completed_points = [s.get('completed_points', 0) for s in sprints_data]

    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=completed_points,
            marker=dict(color=colors['accent_color']),
            text=[str(v) for v in completed_points],
            textposition='auto',
            textfont=dict(color=colors['font_color']),
            hovertemplate='%{x}: %{y}pt 완료<extra></extra>',
        )
    ])

    fig.update_layout(
        title=dict(
            text='스프린트 벨로시티',
            font=dict(color=colors['font_color'], size=14),
        ),
        xaxis=dict(
            title=dict(text='스프린트', font=dict(color=colors['muted_color'])),
            gridcolor=colors['grid_color'],
            tickfont=dict(color=colors['muted_color']),
        ),
        yaxis=dict(
            title=dict(text='완료 스토리 포인트', font=dict(color=colors['muted_color'])),
            gridcolor=colors['grid_color'],
            tickfont=dict(color=colors['muted_color']),
        ),
        height=350,
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor=colors['paper_bgcolor'],
        plot_bgcolor=colors['plot_bgcolor'],
        font=dict(color=colors['font_color']),
        showlegend=False,
    )

    return fig
