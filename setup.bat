@echo off
echo ========================================
echo Fact-Checker MVP Setup
echo Powered by Alibaba Qwen 3
echo ========================================
echo.

echo Step 1: Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Step 2: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 3: Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created! Please add your DASHSCOPE_API_KEY
) else (
    echo .env already exists
)

echo.
echo Step 4: Setting up frontend...
cd frontend
call npm install
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your DASHSCOPE_API_KEY
echo    Get your API key from: https://dashscope.console.aliyun.com/
echo.
echo 2. Start the backend:
echo    python app.py
echo.
echo 3. In a new terminal, start the frontend:
echo    cd frontend
echo    npm start
echo.
echo Optional: Install Tesseract OCR for image support
echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo ========================================
pause
