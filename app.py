"""
Fact-Checking MVP - Main FastAPI Application
Uses Alibaba Qwen 3 LLM for intelligent fact verification
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

from modules.input_processor import SimpleInputProcessor
from modules.claim_extractor import ClaimExtractor
from modules.search_engine import MVPSearchEngine
from modules.context_analyzer import ContextAnalyzer
from modules.verifier import SimpleVerifier

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Fact-Checking MVP with Context",
    description="AI-powered fact-checker using Alibaba Qwen 3",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
input_processor = SimpleInputProcessor()
claim_extractor = ClaimExtractor()
search_engine = MVPSearchEngine()
context_analyzer = ContextAnalyzer()
verifier = SimpleVerifier()

# Pydantic models
class TextInput(BaseModel):
    text: str
    
class URLInput(BaseModel):
    url: str

class FactCheckResponse(BaseModel):
    verdict: str
    confidence: float
    main_claim: str
    key_facts: List[dict]
    context: dict
    evidence: dict
    timeline: List[dict]
    scores: dict


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Fact-Checking MVP",
        "llm": "Alibaba Qwen 3"
    }


@app.post("/api/factcheck/text", response_model=FactCheckResponse)
async def factcheck_text(input_data: TextInput):
    """
    Fact-check text input
    """
    try:
        # Process input
        processed = input_processor.process(input_data.text, "text")
        
        # Extract claims
        claims = claim_extractor.extract_claims(processed['text'])
        
        # Search and verify
        evidence = search_engine.search_and_verify(claims)
        
        # Analyze context
        context = context_analyzer.analyze_context(claims['main_claim'], evidence)
        
        # Calculate verdict
        verdict_data = verifier.calculate_verdict(claims['main_claim'], evidence, context)
        
        return {
            "verdict": verdict_data['verdict'],
            "confidence": verdict_data['confidence'],
            "main_claim": claims['main_claim'],
            "key_facts": claims['key_facts'],
            "context": context,
            "evidence": evidence,
            "timeline": context.get('timeline', []),
            "scores": verdict_data['scores']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/factcheck/url", response_model=FactCheckResponse)
async def factcheck_url(input_data: URLInput):
    """
    Fact-check article from URL
    """
    try:
        # Process URL
        processed = input_processor.process(input_data.url, "url")
        
        # Extract claims
        claims = claim_extractor.extract_claims(processed['text'])
        
        # Search and verify
        evidence = search_engine.search_and_verify(claims)
        
        # Analyze context
        context = context_analyzer.analyze_context(claims['main_claim'], evidence)
        
        # Calculate verdict
        verdict_data = verifier.calculate_verdict(claims['main_claim'], evidence, context)
        
        return {
            "verdict": verdict_data['verdict'],
            "confidence": verdict_data['confidence'],
            "main_claim": claims['main_claim'],
            "key_facts": claims['key_facts'],
            "context": context,
            "evidence": evidence,
            "timeline": context.get('timeline', []),
            "scores": verdict_data['scores']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/factcheck/image", response_model=FactCheckResponse)
async def factcheck_image(file: UploadFile = File(...)):
    """
    Fact-check image with text (OCR)
    """
    try:
        # Save uploaded file temporarily
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process image
        processed = input_processor.process(file_path, "image")
        
        # Clean up
        os.remove(file_path)
        
        # Extract claims
        claims = claim_extractor.extract_claims(processed['text'])
        
        # Search and verify
        evidence = search_engine.search_and_verify(claims)
        
        # Analyze context
        context = context_analyzer.analyze_context(claims['main_claim'], evidence)
        
        # Calculate verdict
        verdict_data = verifier.calculate_verdict(claims['main_claim'], evidence, context)
        
        return {
            "verdict": verdict_data['verdict'],
            "confidence": verdict_data['confidence'],
            "main_claim": claims['main_claim'],
            "key_facts": claims['key_facts'],
            "context": context,
            "evidence": evidence,
            "timeline": context.get('timeline', []),
            "scores": verdict_data['scores']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
