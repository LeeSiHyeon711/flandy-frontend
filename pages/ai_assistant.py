import streamlit as st
import time
from datetime import datetime, date
from components.api_client import PlandyAPIClient


def show_ai_assistant():
    # 채팅 UI 전용 스타일
    st.markdown("""
    <style>
    /* 메인 콘텐츠 영역 최대 너비 해제 */
    .main .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    /* 채팅 메시지 전체 너비 사용 */
    .stChatMessage {
        max-width: 100% !important;
        width: 100% !important;
    }
    .stChatMessage > div {
        max-width: 100% !important;
    }
    /* 채팅 메시지 내 텍스트 영역 */
    .stChatMessage [data-testid="stMarkdownContainer"] {
        max-width: 100% !important;
    }
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        max-width: 100% !important;
        word-break: keep-all;
        overflow-wrap: break-word;
    }
    /* 입력 영역 전체 너비 */
    .stChatInput, .stForm {
        max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.header("AI 어시스턴트")

    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    if 'pending_prompt' not in st.session_state:
        st.session_state.pending_prompt = None
    if 'optimization_proposal' not in st.session_state:
        st.session_state.optimization_proposal = None
    if 'run_optimization' not in st.session_state:
        st.session_state.run_optimization = False

    # 채팅 메시지 영역
    for message in st.session_state.chat_history:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # pending prompt 처리
    pending = st.session_state.pending_prompt
    if pending:
        st.session_state.pending_prompt = None
        _stream_response(api_client, pending)

    # 일정 최적화 플로우 처리
    if st.session_state.run_optimization:
        st.session_state.run_optimization = False
        _run_optimization_flow(api_client)

    # 최적화 제안이 있으면 비교표 + 적용 버튼 표시
    if st.session_state.optimization_proposal:
        _show_optimization_proposal(api_client)

    # 입력 영역: 텍스트 + 전송 버튼을 한 줄에
    with st.form("chat_form", clear_on_submit=True, border=False):
        input_col, btn_col = st.columns([5, 1])
        with input_col:
            prompt = st.text_input("메시지 입력", placeholder="메시지를 입력하세요...", label_visibility="collapsed")
        with btn_col:
            submitted = st.form_submit_button("전송", use_container_width=True)

    if submitted and prompt:
        st.session_state.pending_prompt = prompt
        st.rerun()

    # 빠른 액션 버튼
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("태스크 추천", use_container_width=True):
            st.session_state.pending_prompt = "오늘 할 일을 추천해줘"
            st.rerun()
    with col2:
        if st.button("일정 최적화", use_container_width=True):
            st.session_state.run_optimization = True
            st.rerun()
    with col3:
        if st.button("스프린트 현황", use_container_width=True):
            st.session_state.pending_prompt = "현재 스프린트 진행 상황을 알려줘"
            st.rerun()
    with col4:
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.chat_history = []
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.pending_prompt = None
            st.session_state.optimization_proposal = None
            st.rerun()


def _extract_time(iso_string: str) -> str:
    """ISO 8601 문자열에서 HH:MM 형식의 시간을 추출"""
    try:
        # "2026-02-21T09:00:00+09:00" 등의 형식 처리
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return iso_string


def _run_optimization_flow(api_client):
    """일정 최적화 전용 플로우: 일정 조회 → 최적화 API 호출 → 비교표 렌더링"""
    # 사용자 메시지 표시
    user_msg = "일정 최적화를 요청합니다."
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_msg,
        'timestamp': datetime.now().isoformat()
    })
    with st.chat_message("user"):
        st.markdown(user_msg)

    with st.chat_message("assistant"):
        status = st.empty()
        user_info = st.session_state.get('user_info', {})
        user_name = user_info.get('name', '알 수 없음')
        status.markdown(f"**{user_name}**님의 오늘 일정을 조회하고 있습니다... :hourglass_flowing_sand:")

        today = date.today().isoformat()
        schedules = api_client.get_schedule_by_date(today)

        if not schedules:
            msg = "오늘 등록된 일정이 없어 최적화할 내용이 없습니다."
            status.markdown(msg)
            st.session_state.chat_history.append({
                'role': 'assistant', 'content': msg,
                'timestamp': datetime.now().isoformat()
            })
            return

        status.markdown(f"일정 {len(schedules)}개를 발견했습니다. AI가 최적 배치를 분석 중입니다... :hourglass_flowing_sand:")

        result = api_client.request_schedule_optimization(today)

        if not result:
            msg = "일정 최적화 요청에 실패했습니다. 잠시 후 다시 시도해주세요."
            status.markdown(msg)
            st.session_state.chat_history.append({
                'role': 'assistant', 'content': msg,
                'timestamp': datetime.now().isoformat()
            })
            return

        changes = result.get('changes', [])
        reasoning = result.get('reasoning', '')

        if not changes:
            msg = f"**분석 결과:** {reasoning}\n\n현재 일정이 이미 최적 상태입니다. 변경 사항이 없습니다."
            status.markdown(msg)
            st.session_state.chat_history.append({
                'role': 'assistant', 'content': msg,
                'timestamp': datetime.now().isoformat()
            })
            return

        # 비교표 구성
        comparison = f"**AI 분석:** {reasoning}\n\n"
        comparison += "| 작업 | 기존 시간 | 변경 시간 |\n|---|---|---|\n"
        for c in changes:
            orig_start = _extract_time(c.get('original_starts_at', ''))
            orig_end = _extract_time(c.get('original_ends_at', ''))
            new_start = _extract_time(c.get('new_starts_at', ''))
            new_end = _extract_time(c.get('new_ends_at', ''))
            comparison += f"| {c.get('task_title', '')} | {orig_start}~{orig_end} | {new_start}~{new_end} |\n"

        comparison += "\n이 변경사항을 적용할까요?"
        status.markdown(comparison)

        st.session_state.chat_history.append({
            'role': 'assistant', 'content': comparison,
            'timestamp': datetime.now().isoformat()
        })

        # 제안 데이터를 session state에 저장
        st.session_state.optimization_proposal = {
            'changes': changes,
            'reasoning': reasoning,
        }


def _show_optimization_proposal(api_client):
    """최적화 제안에 대한 예/아니오 버튼 표시"""
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("예, 적용합니다", use_container_width=True, type="primary"):
            _apply_optimization(api_client)
            st.rerun()
    with col_no:
        if st.button("아니오, 취소합니다", use_container_width=True):
            st.session_state.optimization_proposal = None
            cancel_msg = "일정 최적화를 취소했습니다."
            st.session_state.chat_history.append({
                'role': 'assistant', 'content': cancel_msg,
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()


def _apply_optimization(api_client):
    """최적화 제안을 DB에 반영"""
    proposal = st.session_state.optimization_proposal
    if not proposal:
        return

    changes = proposal['changes']
    success_count = 0
    fail_count = 0

    for change in changes:
        schedule_id = change.get('schedule_id')
        new_starts = change.get('new_starts_at')
        new_ends = change.get('new_ends_at')

        if schedule_id and new_starts and new_ends:
            result = api_client.update_schedule(
                schedule_id,
                starts_at=new_starts,
                ends_at=new_ends,
            )
            if result:
                success_count += 1
            else:
                fail_count += 1

    st.session_state.optimization_proposal = None

    if fail_count == 0:
        msg = f"일정 최적화가 완료되었습니다. {success_count}개의 일정이 변경되었습니다."
    else:
        msg = f"일정 최적화 결과: {success_count}개 성공, {fail_count}개 실패"

    st.session_state.chat_history.append({
        'role': 'assistant', 'content': msg,
        'timestamp': datetime.now().isoformat()
    })


def _stream_response(api_client, message):
    """메시지를 history에 추가하고 스트리밍 응답을 표시"""
    st.session_state.chat_history.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    with st.chat_message("user"):
        st.markdown(message)

    # 컨텍스트 수집
    team_id = st.session_state.get('selected_team_id')
    user_info = st.session_state.get('user_info', {})
    user_id = user_info.get('id')

    context = {}
    try:
        today = date.today().isoformat()
        tasks = api_client.get_tasks()
        today_schedule = api_client.get_schedule_by_date(today)
        context = {
            'total_tasks': len(tasks) if tasks else 0,
            'tasks': [
                {'title': t.get('title', ''), 'status': t.get('status', ''), 'priority': t.get('priority', '')}
                for t in (tasks or [])[:10]
            ],
            'today_schedule_count': len(today_schedule) if today_schedule else 0,
            'team_id': team_id,
        }
    except Exception:
        pass

    # AI 응답
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("생각하는 중... ▌")
        ai_response_content = ""

        try:
            for chunk in api_client.send_ai_message_stream(
                message, context=context, session_id=st.session_state.session_id,
                user_id=user_id, team_id=team_id
            ):
                if chunk and 'ai_response' in chunk:
                    ai_response_content = chunk['ai_response']
                if chunk and chunk.get('session_id'):
                    st.session_state.session_id = chunk['session_id']

            if ai_response_content:
                displayed = ""
                for char in ai_response_content:
                    displayed += char
                    response_placeholder.markdown(displayed + " ▌")
                    time.sleep(0.01)
                response_placeholder.markdown(ai_response_content)
            else:
                ai_response_content = "응답을 생성하지 못했습니다."
                response_placeholder.markdown(ai_response_content)
        except Exception as e:
            ai_response_content = f"오류가 발생했습니다: {str(e)}"
            response_placeholder.markdown(ai_response_content)

    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': ai_response_content,
        'timestamp': datetime.now().isoformat()
    })
