"""
데이터 처리 유틸리티
샘플 데이터 로드, 워라벨 점수 계산 등의 데이터 관련 함수들
"""

import pandas as pd
from datetime import datetime


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


def get_current_time():
    """현재 시간 반환"""
    return datetime.now().strftime("%H:%M")


def get_completed_tasks_count(df):
    """완료된 일정 개수 계산"""
    current_time = get_current_time()
    completed_tasks = len(df[df['time'] <= current_time])
    total_tasks = len(df)
    return completed_tasks, total_tasks
