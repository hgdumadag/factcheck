# Fact-Checker MVP - Complete Setup Guide

## Step-by-Step Installation

### 1. Get Your Alibaba Qwen API Key

1. Go to [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it in step 3)

### 2. Run Setup

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create Python virtual environment
- Install all Python dependencies
- Create `.env` file from template
- Install frontend dependencies

### 3. Configure Environment

Edit `.env` file and add your API key:
```
DASHSCOPE_API_KEY=sk-your-actual-api-key-here
```

### 4. (Optional) Install Tesseract for Image Support

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location
3. If needed, update path in `modules/input_processor.py`:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 5. Start the Application

**Option A: Using Scripts (Windows)**

Terminal 1:
```bash
start_backend.bat
```

Terminal 2:
```bash
start_frontend.bat
```

**Option B: Manual Start**

Terminal 1 (Backend):
```bash
# Windows
venv\Scripts\activate
python app.py

# macOS/Linux
source venv/bin/activate
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

### 6. Test the Application

1. Backend should be running at: http://localhost:8000
2. Frontend should open at: http://localhost:3000
3. Run the test script:
   ```bash
   python test_example.py
   ```

## Troubleshooting

### "Module not found" errors
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Then reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json  # or delete manually
npm install
npm start
```

### API Key errors
- Make sure `.env` file exists in the root directory
- Check that `DASHSCOPE_API_KEY` is set correctly
- Verify your API key is active on DashScope console

### OCR not working
- Install Tesseract OCR (see step 4)
- Check Tesseract path in `modules/input_processor.py`
- Test with: `tesseract --version`

### Port already in use
If port 8000 or 3000 is taken:

Backend (edit `.env`):
```
API_PORT=8001
```

Frontend (edit `frontend/package.json`):
Change proxy to match new backend port

## Using the Application

### 1. Text Input
- Click "📝 Text" button
- Enter or paste text to fact-check
- Click "Check Facts"

### 2. URL Input
- Click "🔗 URL" button
- Paste article URL
- Click "Check Facts"

### 3. Image Input
- Click "📷 Image" button
- Upload an image with text
- Click "Check Facts"

### Understanding Results

**Verdict Card:**
- Shows overall assessment
- Confidence percentage
- Color-coded (green=true, red=false, yellow=needs context)

**Context Card (Key Feature!):**
- Shows missing context
- Provides full picture
- Helps understand complete story

**Timeline:**
- Shows chronological events
- Helps understand sequence

**Sources:**
- Lists evidence found
- Links to original sources
- Highlights fact-check sites

**Detailed Scores:**
- Source agreement
- Source quality
- Context completeness
- Fact-check coverage

## Advanced Configuration

### Enable Google Custom Search (Optional)

1. Get Google API Key: https://console.cloud.google.com/
2. Create Custom Search Engine: https://cse.google.com/
3. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_search_engine_id
   ```

### Customize Qwen Model

Edit `modules/qwen_client.py`:
```python
self.model = "qwen-plus"  # or "qwen-turbo" for faster/cheaper
```

## Next Steps

1. Test with various claims
2. Try different input types
3. Customize for your use case
4. Deploy to production (see deployment guide)

## Support

- Check README.md for overview
- Review code comments for details
- Test with `test_example.py`

---

Happy Fact-Checking! 🔍
