"""
Claim Extractor Module
Uses Alibaba Qwen 3 to extract factual claims from text
"""

from modules.qwen_client import QwenClient
from typing import Dict, List


class ClaimExtractor:
    """Extract verifiable claims from text using Qwen 3"""
    
    def __init__(self):
        self.qwen = QwenClient()
    
    def extract_claims(self, text: str) -> Dict:
        """
        Extract main claims and key facts from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with main_claim, key_facts, entities, and dates
        """
        prompt = f"""
Extract the main factual claims from this text that can be verified.
Return as JSON with the following structure:

{{
    "main_claim": "primary claim being made",
    "key_facts": [
        {{"claim": "specific fact 1", "checkable": true}},
        {{"claim": "specific fact 2", "checkable": false}}
    ],
    "entities": ["person1", "organization1", "location1"],
    "dates_mentioned": ["date1", "date2"]
}}

Text to analyze:
{text}

Important:
- Extract only verifiable factual claims
- Mark checkable as true only if the claim can be fact-checked
- Include all named entities (people, organizations, places)
- Extract any dates or time references
- Keep the main_claim concise and clear
"""
        
        try:
            result = self.qwen.extract_json_response(prompt)
            
            # Ensure required fields exist
            if 'main_claim' not in result:
                result['main_claim'] = text[:200] if len(text) > 200 else text
            if 'key_facts' not in result:
                result['key_facts'] = []
            if 'entities' not in result:
                result['entities'] = []
            if 'dates_mentioned' not in result:
                result['dates_mentioned'] = []
            
            return result
            
        except Exception as e:
            # Fallback: return basic structure
            return {
                "main_claim": text[:200] if len(text) > 200 else text,
                "key_facts": [{"claim": text[:200], "checkable": True}],
                "entities": [],
                "dates_mentioned": [],
                "error": str(e)
            }
