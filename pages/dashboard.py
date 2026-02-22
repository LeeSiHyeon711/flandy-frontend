import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from components.api_client import PlandyAPIClient
from components.auth import get_current_user
from components.charts import create_burndown_chart, create_task_status_chart, create_member_workload_chart
import plotly.express as px
import plotly.graph_objects as go


def show_dashboard():
    """스프린트 대시보드 페이지 표시"""
    st.header("스프린트 대시보드")

    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)

    # 팀 선택 확인
    team_id = st.session_state.get('selected_team_id')
    team_name = st.session_state.get('selected_team_name', '')

    if not team_id:
        st.markdown('<div class="flandy-card" style="border-radius: 12px; padding: 2rem; text-align: center; margin: 2rem 0;"><h3 style="margin-bottom: 1rem;">팀을 선택해주세요</h3><p>사이드바에서 팀을 선택하거나, \'팀 관리\' 메뉴에서 팀을 생성/참여하세요.</p></div>', unsafe_allow_html=True)
        return

    # 스프린트 목록 로드
    try:
        sprints = api_client.get_sprints(team_id)
    except Exception as e:
        st.error(f"스프린트 목록을 불러오는 중 오류가 발생했습니다: {e}")
        return

    if not sprints:
        st.info(f"'{team_name}' 팀에 등록된 스프린트가 없습니다. 스프린트를 생성해주세요.")
        _show_create_sprint_form(api_client, team_id)
        return

    # 스프린트 선택
    sprint_names = [f"{s.get('name', '이름 없음')} ({s.get('status', 'planning')})" for s in sprints]
    sprint_ids = [s.get('id') for s in sprints]

    # 활성 스프린트가 있으면 기본 선택
    default_idx = 0
    for i, s in enumerate(sprints):
        if s.get('status') == 'active':
            default_idx = i
            break

    col_sprint, col_action = st.columns([3, 1])

    with col_sprint:
        selected_sprint_idx = st.selectbox(
            "스프린트 선택",
            range(len(sprint_names)),
            format_func=lambda i: sprint_names[i],
            index=default_idx,
            key="sprint_selector"
        )

    selected_sprint_id = sprint_ids[selected_sprint_idx]
    selected_sprint = sprints[selected_sprint_idx]
    sprint_status = selected_sprint.get('status', 'planning')

    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        action_cols = st.columns(2)
        with action_cols[0]:
            if sprint_status == 'planning':
                if st.button("활성화", key="activate_sprint", use_container_width=True):
                    try:
                        if api_client.activate_sprint(selected_sprint_id):
                            st.success("스프린트가 활성화되었습니다!")
                            st.rerun()
                        else:
                            st.error("스프린트 활성화에 실패했습니다.")
                    except Exception as e:
                        st.error(f"스프린트 활성화 중 오류: {e}")
        with action_cols[1]:
            if sprint_status == 'active':
                if st.button("완료", key="complete_sprint", use_container_width=True):
                    try:
                        if api_client.complete_sprint(selected_sprint_id):
                            st.success("스프린트가 완료되었습니다!")
                            st.rerun()
                        else:
                            st.error("스프린트 완료 처리에 실패했습니다.")
                    except Exception as e:
                        st.error(f"스프린트 완료 중 오류: {e}")

    st.markdown("---")

    # 스프린트 대시보드 데이터 로드
    try:
        dashboard_data = api_client.get_sprint_dashboard(selected_sprint_id)
    except Exception as e:
        st.error(f"대시보드 데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return

    if not dashboard_data:
        st.info("대시보드 데이터를 불러올 수 없습니다.")
        return

    # 스프린트 기본 정보
    sprint_info = dashboard_data.get('sprint', selected_sprint)
    sprint_name = sprint_info.get('name', '이름 없음')
    start_date = sprint_info.get('start_date', '')
    end_date = sprint_info.get('end_date', '')

    st.markdown(f'<div class="flandy-card"><div style="display: flex; justify-content: space-between; align-items: center;"><div><h3 style="margin: 0;">{sprint_name}</h3><span style="color: var(--text-secondary); font-size: 0.85rem;">{start_date} ~ {end_date}</span></div><span style="color: #3B82F6; font-weight: bold; font-size: 0.9rem; background-color: var(--bg-primary); padding: 0.25rem 0.75rem; border-radius: 12px;">{sprint_status.upper()}</span></div></div>', unsafe_allow_html=True)

    # 스프린트 진행률
    total_points = dashboard_data.get('total_points', 0)
    completed_points = dashboard_data.get('completed_points', 0)
    progress = (completed_points / total_points * 100) if total_points > 0 else 0

    st.markdown(f'<div class="flandy-card"><div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;"><span style="color: var(--text-primary); font-weight: bold;">스프린트 진행률</span><span style="color: #3B82F6; font-weight: bold;">{completed_points}/{total_points} 포인트 ({progress:.0f}%)</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {progress}%;"></div></div></div>', unsafe_allow_html=True)

    # 상태별 메트릭 카드
    status_counts = dashboard_data.get('status_counts', {})
    pending_count = status_counts.get('pending', 0)
    in_progress_count = status_counts.get('in_progress', 0)
    completed_count = status_counts.get('completed', 0)
    cancelled_count = status_counts.get('cancelled', 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="flandy-metric" style="border-left: 4px solid #94A3B8;"><p class="label">대기</p><h2 class="value">{pending_count}</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="flandy-metric" style="border-left: 4px solid #3B82F6;"><p class="label">진행중</p><h2 class="value">{in_progress_count}</h2></div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="flandy-metric" style="border-left: 4px solid #22C55E;"><p class="label">완료</p><h2 class="value">{completed_count}</h2></div>', unsafe_allow_html=True)

    with col4:
        st.markdown(f'<div class="flandy-metric" style="border-left: 4px solid #EF4444;"><p class="label">취소</p><h2 class="value">{cancelled_count}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")

    # 차트 영역
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # 번다운 차트
        st.subheader("번다운 차트")
        burndown_data = dashboard_data.get('burndown', [])
        if burndown_data:
            fig = create_burndown_chart(burndown_data, sprint_name)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("번다운 데이터가 없습니다.")

    with chart_col2:
        # 태스크 상태 차트
        st.subheader("태스크 상태 분포")
        if status_counts:
            fig = create_task_status_chart(status_counts)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("태스크 상태 데이터가 없습니다.")

    st.markdown("---")

    # 멤버별 워크로드
    st.subheader("멤버별 워크로드")
    member_workload = dashboard_data.get('member_workload', [])
    if member_workload:
        fig = create_member_workload_chart(member_workload)
        st.plotly_chart(fig, use_container_width=True)

        # 멤버별 상세 정보
        for member in member_workload:
            member_name = member.get('name', '알 수 없음')
            member_tasks = member.get('total', 0)
            member_points = member.get('points', 0)
            member_completed = member.get('completed', 0)

            st.markdown(f'<div class="flandy-card" style="padding: 0.75rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;"><span style="color: var(--text-primary); font-weight: bold;">{member_name}</span><div style="display: flex; gap: 1.5rem; font-size: 0.85rem;"><span style="color: var(--text-secondary);">태스크: {member_tasks}개</span><span style="color: #3B82F6;">포인트: {member_points}pt</span><span style="color: #22C55E;">완료: {member_completed}개</span></div></div>', unsafe_allow_html=True)
    else:
        st.info("멤버 워크로드 데이터가 없습니다.")

    st.markdown("---")

    # 스프린트 생성 폼
    with st.expander("새 스프린트 생성", expanded=False):
        _show_create_sprint_form(api_client, team_id)


def _show_create_sprint_form(api_client, team_id):
    """스프린트 생성 폼"""
    with st.form("create_sprint_form"):
        sprint_name = st.text_input("스프린트 이름 *", placeholder="Sprint 1")
        sprint_goal = st.text_area("스프린트 목표", placeholder="이번 스프린트의 목표를 입력하세요")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=date.today())
        with col2:
            end_date = st.date_input("종료일", value=date.today() + timedelta(days=14))

        submitted = st.form_submit_button("스프린트 생성", use_container_width=True)

        if submitted:
            if not sprint_name:
                st.error("스프린트 이름을 입력해주세요.")
            else:
                data = {
                    "name": sprint_name,
                    "goal": sprint_goal,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                try:
                    result = api_client.create_sprint(team_id, data)
                    if result:
                        st.success(f"스프린트 '{sprint_name}'이(가) 생성되었습니다!")
                        st.rerun()
                    else:
                        st.error("스프린트 생성에 실패했습니다.")
                except Exception as e:
                    st.error(f"스프린트 생성 중 오류: {e}")
