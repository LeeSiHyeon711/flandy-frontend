@echo off
echo 🚀 Plandy Streamlit 프론트엔드 시작 중...
echo ================================================

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

REM 필요한 패키지 설치
echo 📦 필요한 패키지를 설치하는 중...
pip install -r requirements.txt

REM Streamlit 실행
echo 🌐 Streamlit 서버를 시작하는 중...
echo ================================================
echo 브라우저에서 http://127.0.0.1:8501 에 접속하세요.
echo ================================================

python run.py

pause
