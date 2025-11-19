"""
Input Processor Module
Handles text, URL, and image inputs
"""

import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
from newspaper import Article
from typing import Dict


class SimpleInputProcessor:
    """Process different input types: text, URL, image"""
    
    def __init__(self):
        # Configure pytesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def process(self, input_data, input_type: str) -> Dict:
        """
        Process input based on type
        
        Args:
            input_data: The input (text, URL, or file path)
            input_type: One of 'text', 'url', 'image'
            
        Returns:
            Dict with processed text and metadata
        """
        if input_type == "image":
            return self._process_image(input_data)
        elif input_type == "url":
            return self._process_url(input_data)
        elif input_type == "text":
            return self._process_text(input_data)
        else:
            raise ValueError(f"Unknown input type: {input_type}")
    
    def _process_text(self, text: str) -> Dict:
        """Process direct text input"""
        return {
            "text": text,
            "type": "direct",
            "has_image": False
        }
    
    def _process_image(self, image_path: str) -> Dict:
        """Extract text from image using OCR"""
        try:
            # Open image and extract text
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            
            return {
                "text": text.strip(),
                "type": "image",
                "has_image": True,
                "source": image_path
            }
        except Exception as e:
            # Fallback: return error message
            return {
                "text": f"[OCR Error: {str(e)}] Please ensure Tesseract is installed.",
                "type": "image",
                "has_image": True,
                "error": str(e)
            }
    
    def _process_url(self, url: str) -> Dict:
        """Scrape and extract article text from URL"""
        try:
            # Try newspaper3k first (better for articles)
            article = Article(url)
            article.download()
            article.parse()
            
            text = article.text
            title = article.title
            
            # Limit text length for MVP
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return {
                "text": text,
                "title": title,
                "type": "article",
                "source": url,
                "has_image": False
            }
        except Exception as e:
            # Fallback to simple BeautifulSoup scraping
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit text length
                if len(text) > 5000:
                    text = text[:5000] + "..."
                
                return {
                    "text": text,
                    "type": "article",
                    "source": url,
                    "has_image": False
                }
            except Exception as fallback_error:
                raise Exception(f"Failed to process URL: {str(fallback_error)}")
