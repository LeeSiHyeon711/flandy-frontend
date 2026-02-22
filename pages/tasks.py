import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from components.api_client import PlandyAPIClient
from components.auth import get_current_user

def show_tasks():
    """태스크 관리 페이지 표시"""
    st.header("태스크 관리")

    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)

    # 팀/스프린트 정보
    team_id = st.session_state.get('selected_team_id')
    team_name = st.session_state.get('selected_team_name', '')

    # 스프린트 목록 및 멤버 목록 로드
    sprints = []
    members = []
    if team_id:
        try:
            sprints = api_client.get_sprints(team_id)
        except Exception:
            sprints = []
        try:
            team_data = api_client.get_team(team_id)
            if team_data:
                raw_members = team_data.get('members', [])
                # TeamMember 구조에서 user 정보 추출
                for m in raw_members:
                    user = m.get('user', {})
                    if user:
                        members.append({
                            'id': user.get('id', m.get('user_id')),
                            'name': user.get('name', '알 수 없음'),
                            'role': m.get('role', 'member'),
                        })
        except Exception:
            members = []

    # 필터 및 검색 - 상단 필터 행
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        # 스프린트 필터
        sprint_options = ["전체"]
        sprint_id_map = {}
        for s in sprints:
            label = f"{s.get('name', '이름 없음')} ({s.get('status', 'planning')})"
            sprint_options.append(label)
            sprint_id_map[label] = s.get('id')

        sprint_filter = st.selectbox(
            "스프린트 필터",
            sprint_options,
            key="sprint_filter"
        )

    with filter_col2:
        # 담당자 필터
        assignee_options = ["전체"]
        assignee_id_map = {}
        for m in members:
            label = m.get('name', '알 수 없음')
            assignee_options.append(label)
            assignee_id_map[label] = m.get('id')

        assignee_filter = st.selectbox(
            "담당자 필터",
            assignee_options,
            key="assignee_filter"
        )

    with filter_col3:
        search_term = st.text_input(
            "검색",
            placeholder="태스크 제목으로 검색...",
            key="search_term"
        )

    # 기존 필터 행
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "상태 필터",
            ["전체", "pending", "in_progress", "completed", "cancelled"],
            key="status_filter"
        )

    with col2:
        priority_filter = st.selectbox(
            "우선순위 필터",
            ["전체", "low", "medium", "high", "urgent"],
            key="priority_filter"
        )

    with col3:
        date_filter = st.date_input(
            "날짜 필터",
            value=None,
            key="date_filter"
        )

    # 필터 적용
    filters = {}
    if status_filter != "전체":
        filters['status'] = status_filter
    if priority_filter != "전체":
        filters['priority'] = priority_filter
    if date_filter:
        filters['date'] = date_filter.isoformat()

    # 태스크 데이터 로딩
    with st.spinner("태스크를 불러오는 중..."):
        tasks = api_client.get_tasks(**filters)

    # 스프린트 필터 적용 (클라이언트 사이드)
    if sprint_filter != "전체" and sprint_filter in sprint_id_map:
        selected_sprint_id = sprint_id_map[sprint_filter]
        tasks = [t for t in tasks if t.get('sprint_id') == selected_sprint_id]

    # 담당자 필터 적용 (클라이언트 사이드)
    if assignee_filter != "전체" and assignee_filter in assignee_id_map:
        selected_assignee_id = assignee_id_map[assignee_filter]
        tasks = [t for t in tasks if t.get('assignee_id') == selected_assignee_id]

    # 검색 필터 적용
    if search_term:
        tasks = [task for task in tasks if search_term.lower() in task.get('title', '').lower()]

    # 통계 정보
    col1, col2, col3, col4 = st.columns(4)

    total_tasks = len(tasks)
    pending_count = len([t for t in tasks if t.get('status') == 'pending'])
    in_progress_count = len([t for t in tasks if t.get('status') == 'in_progress'])
    completed_count = len([t for t in tasks if t.get('status') == 'completed'])

    with col1:
        st.metric("전체", total_tasks)
    with col2:
        st.metric("대기", pending_count)
    with col3:
        st.metric("진행중", in_progress_count)
    with col4:
        st.metric("완료", completed_count)

    st.markdown("---")

    # 새 태스크 추가 버튼
    if st.button("새 태스크 추가", use_container_width=True):
        st.session_state.show_task_form = not st.session_state.get('show_task_form', False)
        st.rerun()

    # 새 태스크 폼 (버튼 바로 아래)
    if st.session_state.get('show_task_form'):
        show_task_form(api_client, sprints, members)

    # 태스크 목록 표시
    if tasks:
        # 정렬 옵션
        col1, col2 = st.columns([3, 1])
        with col2:
            sort_by = st.selectbox(
                "정렬 기준",
                ["생성일", "마감일", "우선순위", "상태"],
                key="sort_tasks"
            )

        # 정렬 적용
        if sort_by == "마감일":
            tasks.sort(key=lambda x: x.get('deadline', ''), reverse=False)
        elif sort_by == "우선순위":
            priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
            tasks.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 2), reverse=True)
        elif sort_by == "상태":
            status_order = {'in_progress': 3, 'pending': 2, 'completed': 1, 'cancelled': 0}
            tasks.sort(key=lambda x: status_order.get(x.get('status', 'pending'), 2), reverse=True)
        else:  # 생성일
            tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # 태스크 카드들 표시
        for task in tasks:
            show_task_card(task, api_client, members)
    else:
        st.info("등록된 태스크가 없습니다.")

def show_task_card(task, api_client, members=None):
    """태스크 카드 표시"""
    task_id = task.get('id')
    title = task.get('title', '제목 없음')
    description = task.get('description', '') or ''
    status = task.get('status', 'pending') or 'pending'
    priority = task.get('priority', 'medium') or 'medium'
    deadline = task.get('deadline', '')
    story_points = task.get('story_points', None)
    assignee_id = task.get('assignee_id', None)

    # labels 안전 파싱 (JSON 문자열 또는 리스트 모두 처리)
    raw_labels = task.get('labels', [])
    if isinstance(raw_labels, str):
        try:
            import json
            raw_labels = json.loads(raw_labels)
        except (json.JSONDecodeError, TypeError):
            raw_labels = []
    if not isinstance(raw_labels, list):
        raw_labels = []
    labels = [str(l) for l in raw_labels if l]

    # 담당자 이름 찾기
    assignee_name = ""
    if assignee_id and members:
        assignee = next((m for m in members if m.get('id') == assignee_id), None)
        if assignee:
            assignee_name = assignee.get('name', '')
    elif task.get('assignee_name'):
        assignee_name = task.get('assignee_name', '')

    # 상태별 이모지와 색상
    status_info = {
        'pending': {'emoji': '', 'color': '#94A3B8'},
        'in_progress': {'emoji': '', 'color': '#3B82F6'},
        'completed': {'emoji': '', 'color': '#10B981'},
        'cancelled': {'emoji': '', 'color': '#EF4444'}
    }

    # 우선순위별 색상
    priority_info = {
        'low': {'color': '#10B981'},
        'medium': {'color': '#F59E0B'},
        'high': {'color': '#F97316'},
        'urgent': {'color': '#EF4444'}
    }

    status_color = status_info.get(status, {}).get('color', '#94A3B8')
    priority_color = priority_info.get(priority, {}).get('color', '#F59E0B')

    # 마감일 처리
    deadline_str = "마감일 없음"
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            deadline_str = deadline_dt.strftime('%Y-%m-%d %H:%M')

            now = datetime.now()
            if deadline_dt < now:
                deadline_str += " (지연)"
            elif (deadline_dt - now).days <= 1:
                deadline_str += " (임박)"
        except:
            deadline_str = deadline

    # 라벨 표시
    labels_str = ""
    if labels:
        labels_str = " ".join([f"#{label}" for label in labels])

    # 스토리 포인트 표시
    points_str = ""
    if story_points is not None:
        points_str = f'<span style="background-color: #3B82F6; color: #FFFFFF; padding: 0.1rem 0.4rem; border-radius: 10px; font-size: 0.75rem; font-weight: bold;">{story_points}pt</span>'

    # 담당자 표시
    assignee_str = ""
    if assignee_name:
        assignee_str = f'<span style="color: var(--text-secondary);">담당: {assignee_name}</span>'

    # 카드 표시
    desc_html = f'<p style="margin: 0.5rem 0 0.5rem 0; font-size: 0.9rem; color: var(--text-secondary);">{description}</p>' if description.strip() else ''
    labels_html = f'<span style="color: #8B5CF6;">{labels_str}</span>' if labels_str else ''

    card_html = (
        f'<div class="flandy-card" style="border-left: 4px solid {status_color}; margin-bottom: 0;">'
        f'<h4 style="margin: 0 0 0.25rem 0;">{title} {points_str}</h4>'
        f'{desc_html}'
        f'<div style="display: flex; gap: 1rem; font-size: 0.8rem; color: var(--text-secondary); flex-wrap: wrap; align-items: center;">'
        f'<span style="color: {priority_color}; font-weight: bold;">{priority.upper()}</span>'
        f'<span>{deadline_str}</span>'
        f'{assignee_str}'
        f'{labels_html}'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # 액션 버튼들 — 상태에 따라 보이는 버튼만 배치
    buttons = []
    buttons.append(("edit", "수정"))
    if status == 'pending':
        buttons.append(("start", "시작"))
    if status != 'completed':
        buttons.append(("complete", "완료"))
    buttons.append(("delete", "삭제"))

    btn_cols = st.columns(len(buttons))
    for i, (action, label) in enumerate(buttons):
        with btn_cols[i]:
            if action == "edit":
                if st.button(label, key=f"edit_{task_id}", use_container_width=True):
                    st.session_state.edit_task_id = task_id
                    st.session_state.show_task_form = True
                    st.rerun()
            elif action == "start":
                if st.button(label, key=f"start_{task_id}", use_container_width=True):
                    if api_client.update_task(task_id, status='in_progress'):
                        st.success("태스크를 시작했습니다!")
                        st.rerun()
                    else:
                        st.error("태스크 시작 처리에 실패했습니다.")
            elif action == "complete":
                if st.button(label, key=f"complete_{task_id}", use_container_width=True):
                    if api_client.update_task(task_id, status='completed'):
                        st.success("태스크가 완료되었습니다!")
                        st.rerun()
                    else:
                        st.error("태스크 완료 처리에 실패했습니다.")
            elif action == "delete":
                if st.button(label, key=f"delete_{task_id}", use_container_width=True):
                    if api_client.delete_task(task_id):
                        st.success("태스크가 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("태스크 삭제에 실패했습니다.")

    st.markdown("---")

def show_task_form(api_client, sprints=None, members=None):
    """태스크 생성/수정 폼"""
    st.markdown("---")

    # 수정 모드인지 확인
    is_edit = 'edit_task_id' in st.session_state
    task_id = st.session_state.get('edit_task_id')

    if is_edit:
        st.subheader("태스크 수정")
        # 기존 태스크 데이터 로드
        tasks = api_client.get_tasks()
        task_data = next((t for t in tasks if t.get('id') == task_id), {})
    else:
        st.subheader("새 태스크 추가")
        task_data = {}

    if sprints is None:
        sprints = []
    if members is None:
        members = []

    with st.form("task_form"):
        title = st.text_input(
            "태스크 제목 *",
            value=task_data.get('title', ''),
            placeholder="할 일을 입력하세요"
        )

        description = st.text_area(
            "설명",
            value=task_data.get('description', ''),
            placeholder="상세 설명을 입력하세요"
        )

        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox(
                "우선순위",
                ["low", "medium", "high", "urgent"],
                index=["low", "medium", "high", "urgent"].index(task_data.get('priority', 'medium'))
            )

        with col2:
            status = st.selectbox(
                "상태",
                ["pending", "in_progress", "completed", "cancelled"],
                index=["pending", "in_progress", "completed", "cancelled"].index(task_data.get('status', 'pending'))
            )

        col1, col2 = st.columns(2)
        with col1:
            deadline = st.date_input(
                "마감일",
                value=datetime.fromisoformat(task_data.get('deadline', '')).date() if task_data.get('deadline') else date.today() + timedelta(days=1)
            )
        with col2:
            story_points = st.number_input(
                "스토리 포인트",
                min_value=0,
                max_value=100,
                value=task_data.get('story_points', 0) or 0,
                step=1
            )

        # 스프린트 선택
        sprint_options = ["없음"]
        sprint_id_map = {}
        for s in sprints:
            label = f"{s.get('name', '이름 없음')} ({s.get('status', 'planning')})"
            sprint_options.append(label)
            sprint_id_map[label] = s.get('id')

        current_sprint_idx = 0
        if task_data.get('sprint_id'):
            for i, s in enumerate(sprints):
                if s.get('id') == task_data.get('sprint_id'):
                    current_sprint_idx = i + 1
                    break

        selected_sprint = st.selectbox(
            "스프린트",
            sprint_options,
            index=current_sprint_idx,
            key="task_sprint_select"
        )

        # 담당자 선택
        assignee_options = ["없음"]
        assignee_id_map = {}
        for m in members:
            label = m.get('name', '알 수 없음')
            assignee_options.append(label)
            assignee_id_map[label] = m.get('id')

        current_assignee_idx = 0
        if task_data.get('assignee_id'):
            for i, m in enumerate(members):
                if m.get('id') == task_data.get('assignee_id'):
                    current_assignee_idx = i + 1
                    break

        selected_assignee = st.selectbox(
            "담당자",
            assignee_options,
            index=current_assignee_idx,
            key="task_assignee_select"
        )

        # 라벨 안전 파싱
        raw_form_labels = task_data.get('labels', [])
        if isinstance(raw_form_labels, str):
            try:
                import json
                raw_form_labels = json.loads(raw_form_labels)
            except (json.JSONDecodeError, TypeError):
                raw_form_labels = []
        if not isinstance(raw_form_labels, list):
            raw_form_labels = []

        labels_input = st.text_input(
            "라벨 (쉼표로 구분)",
            value=", ".join(str(l) for l in raw_form_labels if l),
            placeholder="work, urgent, personal"
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            submit = st.form_submit_button("저장", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("취소", use_container_width=True)

        if submit and title:
            # 라벨 처리
            labels = [label.strip() for label in labels_input.split(',') if label.strip()]

            # 스프린트 ID 추출
            sprint_id = None
            if selected_sprint != "없음" and selected_sprint in sprint_id_map:
                sprint_id = sprint_id_map[selected_sprint]

            # 담당자 ID 추출
            assignee_id = None
            if selected_assignee != "없음" and selected_assignee in assignee_id_map:
                assignee_id = assignee_id_map[selected_assignee]

            # team_id
            team_id = st.session_state.get('selected_team_id')

            if is_edit:
                # 수정
                update_data = dict(
                    title=title,
                    description=description,
                    priority=priority,
                    status=status,
                    deadline=deadline.isoformat(),
                    labels=labels,
                    story_points=story_points if story_points > 0 else None,
                    sprint_id=sprint_id,
                    assignee_id=assignee_id,
                )
                if team_id:
                    update_data['team_id'] = team_id

                if api_client.update_task(task_id, **update_data):
                    st.success("태스크가 수정되었습니다!")
                    st.session_state.show_task_form = False
                    if 'edit_task_id' in st.session_state:
                        del st.session_state.edit_task_id
                    st.rerun()
                else:
                    st.error("태스크 수정에 실패했습니다.")
            else:
                # 생성
                if api_client.create_task(
                    title=title,
                    description=description,
                    priority=priority,
                    deadline=deadline.isoformat(),
                    labels=labels,
                    story_points=story_points if story_points > 0 else None,
                    sprint_id=sprint_id,
                    assignee_id=assignee_id,
                    team_id=team_id,
                ):
                    st.success("태스크가 추가되었습니다!")
                    st.session_state.show_task_form = False
                    st.rerun()
                else:
                    st.error("태스크 추가에 실패했습니다.")

        if cancel:
            st.session_state.show_task_form = False
            if 'edit_task_id' in st.session_state:
                del st.session_state.edit_task_id
            st.rerun()
