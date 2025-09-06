#!/usr/bin/env python3
"""
Plandy Streamlit 프론트엔드 실행 스크립트
"""

import subprocess
import sys
import os

def check_requirements():
    """필요한 패키지가 설치되어 있는지 확인"""
    try:
        import streamlit
        import requests
        import pandas
        import plotly
        print("✅ 모든 필요한 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령어로 패키지를 설치해주세요:")
        print("pip install -r requirements.txt")
        return False

def check_backend_connection():
    """백엔드 서버 연결 확인"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 백엔드 서버가 정상적으로 실행 중입니다.")
            return True
        else:
            print(f"❌ 백엔드 서버 응답 오류: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다.")
        print("백엔드 서버가 실행 중인지 확인해주세요:")
        print("cd ../plandy-backend && php artisan serve --host=127.0.0.1 --port=8000")
        return False
    except Exception as e:
        print(f"❌ 백엔드 서버 확인 중 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 Plandy Streamlit 프론트엔드 시작 중...")
    print("=" * 50)
    
    # 요구사항 확인
    if not check_requirements():
        sys.exit(1)
    
    # 백엔드 연결 확인
    print("\n🔍 백엔드 서버 연결 확인 중...")
    if not check_backend_connection():
        print("\n⚠️  백엔드 서버가 실행되지 않았지만 프론트엔드는 시작합니다.")
        print("   로그인 후 백엔드 서버를 시작해주세요.")
    
    print("\n🌐 Streamlit 서버 시작 중...")
    print("=" * 50)
    
    # Streamlit 실행
    try:
        # 프로젝트 루트 디렉토리로 이동
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        # Streamlit 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/app.py",
            "--server.port", "8501",
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Plandy 프론트엔드를 종료합니다.")
    except Exception as e:
        print(f"\n❌ Streamlit 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
