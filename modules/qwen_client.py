"""
Alibaba Qwen 3 LLM Client
Handles all interactions with Qwen API via DashScope
"""

import os
import json
from typing import Dict, List, Optional
import dashscope
from dashscope import Generation
import urllib3

# Disable SSL warnings for development/testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class QwenClient:
    """Client for Alibaba Qwen 3 LLM"""
    
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not found in environment variables")
        
        dashscope.api_key = self.api_key
        self.model = "qwen-plus"  # Using Qwen-Plus for better performance
        
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Send a chat completion request to Qwen
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            
        Returns:
            Response text from Qwen
        """
        try:
            # Configure session to ignore SSL verification for testing
            import os
            os.environ['CURL_CA_BUNDLE'] = ''
            
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format='message',
                temperature=temperature
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                raise Exception(f"Qwen API error: {response.message}")
                
        except Exception as e:
            # Handle SSL errors gracefully
            error_msg = str(e)
            if 'SSL' in error_msg or 'CERTIFICATE' in error_msg:
                raise Exception(f"SSL Certificate Error - Please check network or disable SSL verification: {error_msg}")
            raise Exception(f"Failed to call Qwen API: {str(e)}")
    
    def extract_json_response(self, prompt: str, temperature: float = 0.3) -> dict:
        """
        Get a JSON response from Qwen
        
        Args:
            prompt: The prompt requesting JSON output
            temperature: Lower temperature for more consistent JSON
            
        Returns:
            Parsed JSON dict
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that always responds with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response_text = self.chat(messages, temperature)
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {response_text}")
    
    def simple_prompt(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Simple prompt with optional system message
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            
        Returns:
            Response text
        """
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return self.chat(messages)
