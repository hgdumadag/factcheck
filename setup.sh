#!/bin/bash

echo "========================================"
echo "Fact-Checker MVP Setup"
echo "Powered by Alibaba Qwen 3"
echo "========================================"
echo ""

echo "Step 1: Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 2: Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 3: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created! Please add your DASHSCOPE_API_KEY"
else
    echo ".env already exists"
fi

echo ""
echo "Step 4: Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your DASHSCOPE_API_KEY"
echo "   Get your API key from: https://dashscope.console.aliyun.com/"
echo ""
echo "2. Start the backend:"
echo "   python app.py"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "Optional: Install Tesseract OCR for image support"
echo "   macOS: brew install tesseract"
echo "   Linux: sudo apt-get install tesseract-ocr"
echo "========================================"
