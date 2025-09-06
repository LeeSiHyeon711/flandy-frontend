import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from components.api_client import PlandyAPIClient
from components.auth import get_current_user

def show_tasks():
    """태스크 관리 페이지 표시"""
    st.header("📋 태스크 관리")
    
    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)
    
    # 필터 및 검색
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    with col4:
        search_term = st.text_input(
            "검색",
            placeholder="태스크 제목으로 검색...",
            key="search_term"
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
    if st.button("➕ 새 태스크 추가", use_container_width=True):
        st.session_state.show_task_form = True
    
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
            show_task_card(task, api_client)
    else:
        st.info("등록된 태스크가 없습니다.")
    
    # 새 태스크 폼
    if st.session_state.get('show_task_form'):
        show_task_form(api_client)

def show_task_card(task, api_client):
    """태스크 카드 표시"""
    task_id = task.get('id')
    title = task.get('title', '제목 없음')
    description = task.get('description', '')
    status = task.get('status', 'pending')
    priority = task.get('priority', 'medium')
    deadline = task.get('deadline', '')
    labels = task.get('labels', [])
    
    # 상태별 이모지와 색상
    status_info = {
        'pending': {'emoji': '⏳', 'color': '#6B7280'},
        'in_progress': {'emoji': '🔄', 'color': '#3B82F6'},
        'completed': {'emoji': '✅', 'color': '#10B981'},
        'cancelled': {'emoji': '❌', 'color': '#EF4444'}
    }
    
    # 우선순위별 색상
    priority_info = {
        'low': {'emoji': '🟢', 'color': '#10B981'},
        'medium': {'emoji': '🟡', 'color': '#F59E0B'},
        'high': {'emoji': '🟠', 'color': '#F97316'},
        'urgent': {'emoji': '🔴', 'color': '#EF4444'}
    }
    
    status_emoji = status_info.get(status, {}).get('emoji', '📝')
    priority_emoji = priority_info.get(priority, {}).get('emoji', '⚪')
    
    # 마감일 처리
    deadline_str = "마감일 없음"
    if deadline:
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            deadline_str = deadline_dt.strftime('%Y-%m-%d %H:%M')
            
            # 마감일 임박 체크
            now = datetime.now()
            if deadline_dt < now:
                deadline_str += " ⚠️ 지연"
            elif (deadline_dt - now).days <= 1:
                deadline_str += " 🔥 임박"
        except:
            deadline_str = deadline
    
    # 라벨 표시
    labels_str = ""
    if labels:
        labels_str = " ".join([f"🏷️ {label}" for label in labels])
    
    # 카드 표시
    with st.container():
        st.markdown(f"""
        <div class="task-card" style="border-left: 4px solid {status_info.get(status, {}).get('color', '#6B7280')}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h4 style="margin: 0; color: #1F2937;">{status_emoji} {title}</h4>
                    <p style="margin: 0.5rem 0; color: #6B7280; font-size: 0.9rem;">{description}</p>
                    <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: #6B7280;">
                        <span>{priority_emoji} {priority.upper()}</span>
                        <span>📅 {deadline_str}</span>
                        {f'<span>{labels_str}</span>' if labels_str else ''}
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem;">
        """, unsafe_allow_html=True)
        
        # 액션 버튼들
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("✏️", key=f"edit_{task_id}", help="수정"):
                st.session_state.edit_task_id = task_id
                st.session_state.show_task_form = True
                st.rerun()
        
        with col2:
            if status != 'completed':
                if st.button("✅", key=f"complete_{task_id}", help="완료"):
                    if api_client.update_task(task_id, status='completed'):
                        st.success("태스크가 완료되었습니다!")
                        st.rerun()
                    else:
                        st.error("태스크 완료 처리에 실패했습니다.")
        
        with col3:
            if status == 'pending':
                if st.button("🔄", key=f"start_{task_id}", help="시작"):
                    if api_client.update_task(task_id, status='in_progress'):
                        st.success("태스크를 시작했습니다!")
                        st.rerun()
                    else:
                        st.error("태스크 시작 처리에 실패했습니다.")
        
        with col4:
            if st.button("🗑️", key=f"delete_{task_id}", help="삭제"):
                if api_client.delete_task(task_id):
                    st.success("태스크가 삭제되었습니다!")
                    st.rerun()
                else:
                    st.error("태스크 삭제에 실패했습니다.")
        
        st.markdown("</div></div></div>", unsafe_allow_html=True)
        st.markdown("---")

def show_task_form(api_client):
    """태스크 생성/수정 폼"""
    st.markdown("---")
    
    # 수정 모드인지 확인
    is_edit = 'edit_task_id' in st.session_state
    task_id = st.session_state.get('edit_task_id')
    
    if is_edit:
        st.subheader("✏️ 태스크 수정")
        # 기존 태스크 데이터 로드
        tasks = api_client.get_tasks()
        task_data = next((t for t in tasks if t.get('id') == task_id), {})
    else:
        st.subheader("➕ 새 태스크 추가")
        task_data = {}
    
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
        
        deadline = st.date_input(
            "마감일",
            value=datetime.fromisoformat(task_data.get('deadline', '')).date() if task_data.get('deadline') else date.today() + timedelta(days=1)
        )
        
        labels_input = st.text_input(
            "라벨 (쉼표로 구분)",
            value=", ".join(task_data.get('labels', [])),
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
            
            if is_edit:
                # 수정
                if api_client.update_task(
                    task_id,
                    title=title,
                    description=description,
                    priority=priority,
                    status=status,
                    deadline=deadline.isoformat(),
                    labels=labels
                ):
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
                    labels=labels
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
