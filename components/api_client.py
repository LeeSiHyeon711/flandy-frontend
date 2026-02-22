import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, date

class PlandyAPIClient:
    """Plandy 백엔드 API 클라이언트"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api"):
        self.base_url = base_url
        self.token = None
    
    def set_token(self, token: str):
        """인증 토큰 설정"""
        self.token = token
    
    def get_headers(self) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """API 요청 실행"""
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                st.error(f"지원하지 않는 HTTP 메서드: {method}")
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 401:
                st.error("인증이 필요합니다. 다시 로그인해주세요.")
                st.session_state.user_token = None
                st.session_state.user_info = None
                st.rerun()
            elif response.status_code == 422:
                errors = response.json().get('errors', {})
                for field, messages in errors.items():
                    st.error(f"{field}: {', '.join(messages)}")
            else:
                st.error(f"API 오류: {response.status_code} - {response.text}")
            
            return None
            
        except requests.exceptions.ConnectionError:
            st.error("서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.")
            return None
        except Exception as e:
            st.error(f"요청 중 오류가 발생했습니다: {str(e)}")
            return None
    
    # 인증 관련 메서드
    def login(self, email: str, password: str) -> bool:
        """로그인"""
        data = {"email": email, "password": password}
        response = self._make_request("POST", "/auth/login", data)
        
        if response and response.get("success"):
            self.token = response["data"]["token"]
            return True
        return False
    
    def register(self, email: str, password: str, name: str, password_confirmation: str = None) -> bool:
        """회원가입"""
        data = {
            "email": email, 
            "password": password, 
            "password_confirmation": password_confirmation or password,
            "name": name
        }
        response = self._make_request("POST", "/auth/register", data)
        
        if response and response.get("success"):
            self.token = response["data"]["token"]
            return True
        return False
    
    def get_user_info(self) -> Optional[Dict]:
        """현재 사용자 정보 조회"""
        response = self._make_request("GET", "/auth/me")
        return response["data"] if response and response.get("success") else None
    
    def logout(self) -> bool:
        """로그아웃"""
        response = self._make_request("POST", "/auth/logout")
        if response and response.get("success"):
            self.token = None
            return True
        return False
    
    # 태스크 관련 메서드
    def get_tasks(self, status: Optional[str] = None, priority: Optional[str] = None, 
                  date: Optional[str] = None) -> List[Dict]:
        """태스크 목록 조회"""
        params = []
        if status:
            params.append(f"status={status}")
        if priority:
            params.append(f"priority={priority}")
        if date:
            params.append(f"date={date}")
        
        endpoint = "/tasks"
        if params:
            endpoint += "?" + "&".join(params)
        
        response = self._make_request("GET", endpoint)
        return response["data"] if response and response.get("success") else []
    
    def create_task(self, title: str, description: str = "", priority: str = "medium",
                   deadline: Optional[str] = None, labels: List[str] = None,
                   story_points: Optional[int] = None, sprint_id: Optional[int] = None,
                   assignee_id: Optional[int] = None, team_id: Optional[int] = None) -> bool:
        """태스크 생성"""
        data = {
            "title": title,
            "description": description,
            "priority": priority,
            "labels": labels or []
        }
        if deadline:
            data["deadline"] = deadline
        if story_points is not None:
            data["story_points"] = story_points
        if sprint_id is not None:
            data["sprint_id"] = sprint_id
        if assignee_id is not None:
            data["assignee_id"] = assignee_id
        if team_id is not None:
            data["team_id"] = team_id

        response = self._make_request("POST", "/tasks", data)
        return response and response.get("success")
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """태스크 수정"""
        response = self._make_request("PUT", f"/tasks/{task_id}", kwargs)
        return response and response.get("success")
    
    def delete_task(self, task_id: int) -> bool:
        """태스크 삭제"""
        response = self._make_request("DELETE", f"/tasks/{task_id}")
        return response and response.get("success")
    
    # 스케줄 관련 메서드
    def get_schedule(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """스케줄 목록 조회"""
        params = []
        if start_date:
            params.append(f"start_date={start_date}")
        if end_date:
            params.append(f"end_date={end_date}")
        
        endpoint = "/schedule"
        if params:
            endpoint += "?" + "&".join(params)
        
        response = self._make_request("GET", endpoint)
        return response["data"] if response and response.get("success") else []
    
    def get_schedule_by_date(self, date: str) -> List[Dict]:
        """특정 날짜 스케줄 조회"""
        response = self._make_request("GET", f"/schedule/date/{date}")
        return response["data"] if response and response.get("success") else []
    
    def create_schedule(self, title: str = "", start_time: str = "", end_time: str = "",
                       description: str = "", task_id: Optional[int] = None,
                       starts_at: Optional[str] = None, ends_at: Optional[str] = None,
                       state: str = "scheduled", source: str = "user") -> bool:
        """스케줄 생성"""
        data = {
            "starts_at": starts_at or start_time,
            "ends_at": ends_at or end_time,
            "source": source,
            "state": state,
        }
        if task_id:
            data["task_id"] = task_id

        response = self._make_request("POST", "/schedule", data)
        return response and response.get("success")
    
    def update_schedule(self, schedule_id: int, **kwargs) -> bool:
        """스케줄 수정"""
        # 필드명 매핑 (프론트: start_time/end_time → 백엔드: starts_at/ends_at)
        if 'start_time' in kwargs:
            kwargs['starts_at'] = kwargs.pop('start_time')
        if 'end_time' in kwargs:
            kwargs['ends_at'] = kwargs.pop('end_time')
        # 백엔드 ScheduleBlock에 없는 필드 제거
        kwargs.pop('title', None)
        kwargs.pop('description', None)
        response = self._make_request("PUT", f"/schedule/{schedule_id}", kwargs)
        return response and response.get("success")
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """스케줄 삭제"""
        response = self._make_request("DELETE", f"/schedule/{schedule_id}")
        return response and response.get("success")
    
    # AI 관련 메서드
    def send_ai_message(self, message: str, context: Optional[Dict] = None, session_id: Optional[str] = None) -> Optional[Dict]:
        """AI 채팅 메시지 전송"""
        data = {"message": message}
        if context:
            data["context"] = context
        if session_id:
            data["session_id"] = session_id

        # user_id: session_state에서 조회
        data["user_id"] = st.session_state.get('user_info', {}).get('id')
        
        response = self._make_request("POST", "/ai/chat", data)
        return response if response and response.get("success") else None
    
    def send_ai_message_stream(self, message: str, context: Optional[Dict] = None, session_id: Optional[str] = None,
                               user_id=None, team_id=None):
        """AI 채팅 메시지 스트림 전송"""
        import requests
        import json

        data = {"message": message}
        if context:
            data["context"] = context
        if session_id:
            data["session_id"] = session_id

        # user_id: 파라미터 우선, 없으면 session_state에서 조회
        if user_id is not None:
            data["user_id"] = user_id
        else:
            data["user_id"] = st.session_state.get('user_info', {}).get('id')

        if team_id is not None:
            data["team_id"] = team_id
        
        url = f"{self.base_url}/ai/chat"
        headers = self.get_headers()
        
        try:
            response = requests.post(url, json=data, headers=headers, stream=True)
            
            if response.status_code == 200:
                current_event = ''
                ai_response_received = False

                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue

                    if line.startswith('id: '):
                        pass
                    elif line.startswith('event: '):
                        current_event = line[7:]
                    elif line.startswith('retry:'):
                        pass
                    elif line.startswith('data: ') or line.startswith('data:'):
                        json_data = line[6:] if line.startswith('data: ') else line[5:]
                        if json_data == '[DONE]':
                            break

                        try:
                            parsed_data = json.loads(json_data)
                        except json.JSONDecodeError:
                            continue

                        # ai_response 이벤트에서만 응답 yield (complete 이벤트의 중복 방지)
                        if current_event == 'ai_response' and 'ai_response' in parsed_data:
                            if not ai_response_received:
                                ai_response_received = True
                                yield {'ai_response': parsed_data['ai_response']}
                        elif current_event == 'complete' and not ai_response_received:
                            # ai_response 이벤트가 없었을 때만 complete에서 가져옴
                            if parsed_data.get('ai_response'):
                                yield {'ai_response': parsed_data['ai_response']}

                        # session_id 전달
                        if parsed_data.get('session_id'):
                            yield {'session_id': parsed_data['session_id']}
            else:
                st.error(f"스트림 요청 실패: {response.status_code}")
                return
                
        except requests.exceptions.ConnectionError:
            st.error("서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.")
        except Exception as e:
            st.error(f"요청 중 오류가 발생했습니다: {str(e)}")
    
    def request_schedule_optimization(self, date: str) -> Optional[Dict]:
        """일정 최적화 요청"""
        data = {"date": date}
        response = self._make_request("POST", "/ai/optimize-schedule", data)
        return response if response and response.get("success") else None

    def reschedule_request(self, task_id: int, reason: str) -> Optional[Dict]:
        """스케줄 재조정 요청"""
        data = {
            "task_id": task_id,
            "reason": reason
        }
        response = self._make_request("POST", "/ai/reschedule", data)
        return response["data"] if response and response.get("success") else None
    
    # 팀 관련 메서드
    def get_teams(self) -> List[Dict]:
        """팀 목록 조회"""
        response = self._make_request("GET", "/teams")
        return response["data"] if response and response.get("success") else []

    def create_team(self, name: str, description: str = "") -> Optional[Dict]:
        """팀 생성"""
        data = {"name": name, "description": description}
        response = self._make_request("POST", "/teams", data)
        return response["data"] if response and response.get("success") else None

    def get_team(self, team_id: int) -> Optional[Dict]:
        """팀 상세 조회"""
        response = self._make_request("GET", f"/teams/{team_id}")
        return response["data"] if response and response.get("success") else None

    def update_team(self, team_id: int, data: Dict) -> bool:
        """팀 정보 수정"""
        response = self._make_request("PUT", f"/teams/{team_id}", data)
        return response and response.get("success")

    def delete_team(self, team_id: int) -> bool:
        """팀 삭제"""
        response = self._make_request("DELETE", f"/teams/{team_id}")
        return response and response.get("success")

    def join_team(self, invite_code: str) -> Optional[Dict]:
        """초대 코드로 팀 참여"""
        data = {"invite_code": invite_code}
        response = self._make_request("POST", "/teams/join", data)
        return response["data"] if response and response.get("success") else None

    def leave_team(self, team_id: int) -> bool:
        """팀 탈퇴"""
        response = self._make_request("POST", f"/teams/{team_id}/leave")
        return response and response.get("success")

    def update_member_role(self, team_id: int, member_id: int, role: str) -> bool:
        """팀 멤버 역할 변경"""
        data = {"role": role}
        response = self._make_request("PUT", f"/teams/{team_id}/members/{member_id}", data)
        return response and response.get("success")

    def remove_member(self, team_id: int, member_id: int) -> bool:
        """팀 멤버 제거"""
        response = self._make_request("DELETE", f"/teams/{team_id}/members/{member_id}")
        return response and response.get("success")

    # 스프린트 관련 메서드
    def get_sprints(self, team_id: int) -> List[Dict]:
        """스프린트 목록 조회"""
        response = self._make_request("GET", f"/teams/{team_id}/sprints")
        return response["data"] if response and response.get("success") else []

    def create_sprint(self, team_id: int, data: Dict) -> Optional[Dict]:
        """스프린트 생성"""
        response = self._make_request("POST", f"/teams/{team_id}/sprints", data)
        return response["data"] if response and response.get("success") else None

    def get_sprint(self, sprint_id: int) -> Optional[Dict]:
        """스프린트 상세 조회"""
        response = self._make_request("GET", f"/sprints/{sprint_id}")
        return response["data"] if response and response.get("success") else None

    def update_sprint(self, sprint_id: int, data: Dict) -> bool:
        """스프린트 수정"""
        response = self._make_request("PUT", f"/sprints/{sprint_id}", data)
        return response and response.get("success")

    def delete_sprint(self, sprint_id: int) -> bool:
        """스프린트 삭제"""
        response = self._make_request("DELETE", f"/sprints/{sprint_id}")
        return response and response.get("success")

    def activate_sprint(self, sprint_id: int) -> bool:
        """스프린트 활성화"""
        response = self._make_request("POST", f"/sprints/{sprint_id}/activate")
        return response and response.get("success")

    def complete_sprint(self, sprint_id: int) -> bool:
        """스프린트 완료"""
        response = self._make_request("POST", f"/sprints/{sprint_id}/complete")
        return response and response.get("success")

    def get_sprint_dashboard(self, sprint_id: int) -> Optional[Dict]:
        """스프린트 대시보드 조회"""
        response = self._make_request("GET", f"/sprints/{sprint_id}/dashboard")
        return response["data"] if response and response.get("success") else None

    # 시스템 관련 메서드
    def health_check(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
