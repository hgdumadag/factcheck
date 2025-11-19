@echo off
echo Starting Fact-Checker MVP Backend...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your DASHSCOPE_API_KEY
    pause
    exit /b 1
)

REM Start the backend
echo Backend starting on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python app.py
