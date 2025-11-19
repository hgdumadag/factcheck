# Fact-Checker MVP

AI-powered fact-checking application with context awareness, powered by **Alibaba Qwen 3 LLM**.

## 🌟 Features

- **Multi-Input Support**: Text, URL, and Image (OCR) inputs
- **Context-Aware Verification**: Identifies missing context and provides the full picture
- **Multiple Source Search**: DuckDuckGo + optional Google Custom Search
- **Fact-Check Database**: Searches major fact-checking websites
- **Timeline Extraction**: Automatically builds event timelines
- **Confidence Scoring**: Detailed breakdown of verification metrics
- **Modern UI**: Clean, responsive React interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- Alibaba Cloud DashScope API Key ([Get one here](https://dashscope.console.aliyun.com/))

### Installation

#### Windows
```bash
setup.bat
```

#### macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
```

### Configuration

1. Edit `.env` file and add your API key:
```
DASHSCOPE_API_KEY=your_api_key_here
```

2. (Optional) For enhanced search, add Google Custom Search credentials:
```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_search_engine_id
```

3. (Optional) For image support, install Tesseract OCR:
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

### Running the Application

#### Option 1: Using Scripts (Windows)

Terminal 1:
```bash
start_backend.bat
```

Terminal 2:
```bash
start_frontend.bat
```

#### Option 2: Manual Start

Terminal 1 (Backend):
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 📖 Usage

1. **Choose Input Type**: Text, URL, or Image
2. **Submit Content**: Enter your text, paste a URL, or upload an image
3. **Review Results**:
   - Verdict and confidence score
   - Main claim extraction
   - **Missing context** (key differentiator!)
   - Timeline of events
   - Source citations
   - Detailed scoring breakdown

## 🏗️ Architecture

```
Backend (FastAPI + Alibaba Qwen 3)
├── Input Processor (text, URL, image)
├── Claim Extractor (LLM-powered)
├── Search Engine (multi-source)
├── Context Analyzer (identifies missing context)
└── Verifier (confidence scoring)

Frontend (React)
├── Input Interface (3 modes)
├── Verdict Display
├── Context Alert (innovation!)
├── Timeline View
└── Source Citations
```

## 🔑 Key Innovation

**Context Restoration**: Unlike basic fact-checkers, this MVP identifies what context is missing from claims and provides readers with the full picture, helping combat misleading information that's technically true but lacks important context.

## 📚 API Endpoints

- `GET /` - Health check
- `POST /api/factcheck/text` - Fact-check text
- `POST /api/factcheck/url` - Fact-check article URL
- `POST /api/factcheck/image` - Fact-check image (OCR)

## 🛠️ Tech Stack

**Backend**:
- FastAPI
- Alibaba Qwen 3 (via DashScope)
- BeautifulSoup4 & Newspaper3k
- Pytesseract (OCR)
- DuckDuckGo Search

**Frontend**:
- React 18
- Axios
- CSS3 (Gradient UI)

## 📝 Environment Variables

```env
DASHSCOPE_API_KEY=required      # Alibaba Qwen API key
GOOGLE_API_KEY=optional         # Google Custom Search
GOOGLE_CSE_ID=optional          # Google Search Engine ID
API_HOST=0.0.0.0               # Backend host
API_PORT=8000                   # Backend port
```

## 🎯 Future Enhancements

- Multi-language support
- Social media integration
- Browser extension
- Real-time fact-checking
- User feedback loop
- Claim database

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! This is an MVP - lots of room for improvement.

---

**Powered by Alibaba Qwen 3 LLM** 🚀
