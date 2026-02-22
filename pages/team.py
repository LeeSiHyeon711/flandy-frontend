import streamlit as st
from components.api_client import PlandyAPIClient
from components.auth import get_current_user


def show_team():
    """팀 관리 페이지 표시"""
    st.header("팀 관리")

    # API 클라이언트 초기화
    api_client = PlandyAPIClient()
    if 'user_token' in st.session_state:
        api_client.set_token(st.session_state.user_token)

    # 탭 구성: 내 팀 목록 / 팀 생성 / 팀 참여
    tab1, tab2, tab3 = st.tabs(["내 팀 목록", "팀 생성", "팀 참여"])

    # --- 내 팀 목록 ---
    with tab1:
        _show_my_teams(api_client)

    # --- 팀 생성 ---
    with tab2:
        _show_create_team_form(api_client)

    # --- 팀 참여 ---
    with tab3:
        _show_join_team_form(api_client)


def _show_my_teams(api_client):
    """내 팀 목록 표시"""
    try:
        teams = api_client.get_teams()
    except Exception as e:
        st.error(f"팀 목록을 불러오는 중 오류가 발생했습니다: {e}")
        return

    if not teams:
        st.info("소속된 팀이 없습니다. '팀 생성' 또는 '팀 참여' 탭에서 시작하세요.")
        return

    for team in teams:
        team_id = team.get('id')
        team_name = team.get('name', '알 수 없음')
        team_desc = team.get('description', '')
        invite_code = team.get('invite_code', '')
        members = team.get('members', [])
        my_role = team.get('my_role', 'member')

        with st.expander(f"{team_name}", expanded=False):
            # 팀 정보 카드
            st.markdown(f'<div class="flandy-card"><h4 style="margin: 0 0 0.5rem 0;">{team_name}</h4><p style="margin: 0 0 0.5rem 0;">{team_desc if team_desc else "설명 없음"}</p><div style="display: flex; gap: 1rem; font-size: 0.85rem;"><span style="color: #3B82F6;">내 역할: {my_role}</span><span style="color: var(--text-secondary);">멤버: {len(members)}명</span></div></div>', unsafe_allow_html=True)

            # 초대 코드
            if invite_code:
                st.markdown(f'<div class="flandy-card" style="padding: 0.75rem;"><span style="color: var(--text-secondary); font-size: 0.85rem;">초대 코드:</span> <code style="color: #3B82F6; background-color: var(--bg-primary); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 1rem;">{invite_code}</code></div>', unsafe_allow_html=True)

            # 멤버 목록
            if members:
                st.markdown("**멤버 목록**")
                for member in members:
                    user = member.get('user', {}) or {}
                    member_id = member.get('user_id') or user.get('id') or member.get('id')
                    member_name = user.get('name') or member.get('name', '알 수 없음')
                    member_email = user.get('email') or member.get('email', '')
                    member_role = member.get('role', 'member')

                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.markdown(f'<div style="color: var(--text-primary); padding: 0.25rem 0;">{member_name} <span style="color: var(--text-secondary); font-size: 0.8rem;">({member_email})</span></div>', unsafe_allow_html=True)

                    with col2:
                        # 역할 변경 (owner/admin만 가능)
                        if my_role in ['owner', 'admin'] and member_role != 'owner':
                            role_options = ['member', 'admin']
                            current_idx = role_options.index(member_role) if member_role in role_options else 0
                            new_role = st.selectbox(
                                "역할",
                                role_options,
                                index=current_idx,
                                key=f"role_{team_id}_{member_id}",
                                label_visibility="collapsed"
                            )
                            if new_role != member_role:
                                if st.button("변경", key=f"change_role_{team_id}_{member_id}"):
                                    try:
                                        if api_client.update_member_role(team_id, member_id, new_role):
                                            st.success(f"{member_name}의 역할이 변경되었습니다.")
                                            st.rerun()
                                        else:
                                            st.error("역할 변경에 실패했습니다.")
                                    except Exception as e:
                                        st.error(f"역할 변경 중 오류: {e}")
                        else:
                            st.markdown(f'<span style="color: var(--text-secondary); font-size: 0.85rem;">{member_role}</span>', unsafe_allow_html=True)

                    with col3:
                        # 멤버 제거 (owner/admin만 가능, 자기 자신과 owner는 제거 불가)
                        if my_role in ['owner', 'admin'] and member_role != 'owner':
                            if st.button("제거", key=f"remove_{team_id}_{member_id}"):
                                try:
                                    if api_client.remove_member(team_id, member_id):
                                        st.success(f"{member_name}이(가) 팀에서 제거되었습니다.")
                                        st.rerun()
                                    else:
                                        st.error("멤버 제거에 실패했습니다.")
                                except Exception as e:
                                    st.error(f"멤버 제거 중 오류: {e}")

            st.markdown("---")

            # 팀 액션 버튼
            action_col1, action_col2 = st.columns(2)

            with action_col1:
                # 팀 탈퇴
                if my_role != 'owner':
                    if st.button("팀 탈퇴", key=f"leave_{team_id}", use_container_width=True):
                        try:
                            if api_client.leave_team(team_id):
                                st.success("팀에서 탈퇴했습니다.")
                                # 선택된 팀이 탈퇴한 팀이면 초기화
                                if st.session_state.get('selected_team_id') == team_id:
                                    st.session_state.selected_team_id = None
                                    st.session_state.selected_team_name = None
                                st.rerun()
                            else:
                                st.error("팀 탈퇴에 실패했습니다.")
                        except Exception as e:
                            st.error(f"팀 탈퇴 중 오류: {e}")

            with action_col2:
                # 팀 삭제 (owner만 가능)
                if my_role == 'owner':
                    if st.button("팀 삭제", key=f"delete_team_{team_id}", use_container_width=True, type="primary"):
                        try:
                            if api_client.delete_team(team_id):
                                st.success("팀이 삭제되었습니다.")
                                if st.session_state.get('selected_team_id') == team_id:
                                    st.session_state.selected_team_id = None
                                    st.session_state.selected_team_name = None
                                st.rerun()
                            else:
                                st.error("팀 삭제에 실패했습니다.")
                        except Exception as e:
                            st.error(f"팀 삭제 중 오류: {e}")


def _show_create_team_form(api_client):
    """팀 생성 폼"""
    st.subheader("새 팀 만들기")

    with st.form("create_team_form"):
        team_name = st.text_input("팀 이름 *", placeholder="팀 이름을 입력하세요")
        team_desc = st.text_area("팀 설명", placeholder="팀에 대한 설명을 입력하세요")

        submitted = st.form_submit_button("팀 생성", use_container_width=True)

        if submitted:
            if not team_name:
                st.error("팀 이름을 입력해주세요.")
            else:
                try:
                    result = api_client.create_team(team_name, team_desc)
                    if result:
                        st.success(f"'{team_name}' 팀이 생성되었습니다!")
                        # 새로 만든 팀을 선택
                        st.session_state.selected_team_id = result.get('id')
                        st.session_state.selected_team_name = result.get('name', team_name)
                        st.rerun()
                    else:
                        st.error("팀 생성에 실패했습니다.")
                except Exception as e:
                    st.error(f"팀 생성 중 오류가 발생했습니다: {e}")


def _show_join_team_form(api_client):
    """팀 참여 폼"""
    st.subheader("초대 코드로 팀 참여")

    with st.form("join_team_form"):
        invite_code = st.text_input("초대 코드 *", placeholder="초대 코드를 입력하세요")

        submitted = st.form_submit_button("팀 참여", use_container_width=True)

        if submitted:
            if not invite_code:
                st.error("초대 코드를 입력해주세요.")
            else:
                try:
                    result = api_client.join_team(invite_code)
                    if result:
                        st.success("팀에 성공적으로 참여했습니다!")
                        st.session_state.selected_team_id = result.get('id')
                        st.session_state.selected_team_name = result.get('name', '')
                        st.rerun()
                    else:
                        st.error("팀 참여에 실패했습니다. 초대 코드를 확인해주세요.")
                except Exception as e:
                    st.error(f"팀 참여 중 오류가 발생했습니다: {e}")
