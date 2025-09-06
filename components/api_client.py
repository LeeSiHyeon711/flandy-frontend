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
                   deadline: Optional[str] = None, labels: List[str] = None) -> bool:
        """태스크 생성"""
        data = {
            "title": title,
            "description": description,
            "priority": priority,
            "labels": labels or []
        }
        if deadline:
            data["deadline"] = deadline
        
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
    
    def create_schedule(self, title: str, start_time: str, end_time: str,
                       description: str = "", task_id: Optional[int] = None) -> bool:
        """스케줄 생성"""
        data = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "description": description
        }
        if task_id:
            data["task_id"] = task_id
        
        response = self._make_request("POST", "/schedule", data)
        return response and response.get("success")
    
    def update_schedule(self, schedule_id: int, **kwargs) -> bool:
        """스케줄 수정"""
        response = self._make_request("PUT", f"/schedule/{schedule_id}", kwargs)
        return response and response.get("success")
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """스케줄 삭제"""
        response = self._make_request("DELETE", f"/schedule/{schedule_id}")
        return response and response.get("success")
    
    # 워라밸 관련 메서드
    def get_worklife_scores(self) -> List[Dict]:
        """워라밸 점수 목록 조회"""
        response = self._make_request("GET", "/worklife/scores")
        return response["data"] if response and response.get("success") else []
    
    def get_worklife_score_by_week(self, week_start: str) -> Optional[Dict]:
        """특정 주 워라밸 점수 조회"""
        response = self._make_request("GET", f"/worklife/scores/week/{week_start}")
        return response["data"] if response and response.get("success") else None
    
    def create_worklife_score(self, week_start: str, overall_score: float,
                             work_score: float, life_score: float,
                             stress_level: int, satisfaction: int) -> bool:
        """워라밸 점수 생성"""
        data = {
            "week_start": week_start,
            "overall_score": overall_score,
            "work_score": work_score,
            "life_score": life_score,
            "stress_level": stress_level,
            "satisfaction": satisfaction
        }
        response = self._make_request("POST", "/worklife/scores", data)
        return response and response.get("success")
    
    def get_habit_logs(self, date: Optional[str] = None, habit_type: Optional[str] = None) -> List[Dict]:
        """습관 로그 조회"""
        params = []
        if date:
            params.append(f"date={date}")
        if habit_type:
            params.append(f"habit_type={habit_type}")
        
        endpoint = "/worklife/habits"
        if params:
            endpoint += "?" + "&".join(params)
        
        response = self._make_request("GET", endpoint)
        return response["data"] if response and response.get("success") else []
    
    def create_habit_log(self, habit_type: str, completed: bool, note: str = "") -> bool:
        """습관 로그 생성"""
        data = {
            "habit_type": habit_type,
            "completed": completed,
            "note": note
        }
        response = self._make_request("POST", "/worklife/habits", data)
        return response and response.get("success")
    
    def update_habit_log(self, habit_id: int, **kwargs) -> bool:
        """습관 로그 수정"""
        response = self._make_request("PUT", f"/worklife/habits/{habit_id}", kwargs)
        return response and response.get("success")
    
    # AI 관련 메서드
    def send_ai_message(self, message: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """AI 채팅 메시지 전송"""
        data = {"message": message}
        if context:
            data["context"] = context
        
        response = self._make_request("POST", "/ai/chat", data)
        return response["data"] if response and response.get("success") else None
    
    def analyze_worklife(self, period: str = "week", include_suggestions: bool = True) -> Optional[Dict]:
        """워라밸 분석 요청"""
        data = {
            "period": period,
            "include_suggestions": include_suggestions
        }
        response = self._make_request("POST", "/ai/analyze-worklife", data)
        return response["data"] if response and response.get("success") else None
    
    def reschedule_request(self, task_id: int, reason: str) -> Optional[Dict]:
        """스케줄 재조정 요청"""
        data = {
            "task_id": task_id,
            "reason": reason
        }
        response = self._make_request("POST", "/ai/reschedule", data)
        return response["data"] if response and response.get("success") else None
    
    # 시스템 관련 메서드
    def health_check(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
