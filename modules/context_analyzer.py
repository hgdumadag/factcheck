"""
Context Analyzer Module
Identifies missing context and provides full picture
KEY MVP DIFFERENTIATOR
"""

from modules.qwen_client import QwenClient
from typing import Dict, List
import dateparser
import re


class ContextAnalyzer:
    """Analyze and restore missing context"""
    
    def __init__(self):
        self.qwen = QwenClient()
    
    def analyze_context(self, claim: str, search_results: Dict) -> Dict:
        """
        Analyze what context is missing from the claim
        
        Args:
            claim: The main claim to analyze
            search_results: Search results from multiple sources
            
        Returns:
            Dict with missing_context, full_picture, and timeline
        """
        # Extract all evidence snippets
        all_evidence = []
        all_evidence.extend(search_results.get('direct_evidence', []))
        all_evidence.extend(search_results.get('context', []))
        all_evidence.extend(search_results.get('existing_factchecks', []))
        
        # Build evidence text
        evidence_text = "\n\n".join([
            f"Source: {ev.get('title', 'Unknown')}\n{ev.get('snippet', '')}"
            for ev in all_evidence[:5]
        ])
        
        # Extract timeline
        timeline = self.extract_timeline(all_evidence)
        
        # Use Qwen to identify missing context
        missing_context = self.identify_missing_context(claim, evidence_text)
        
        # Generate full picture
        full_picture = self.generate_full_picture(claim, evidence_text, missing_context)
        
        return {
            'missing_context': missing_context,
            'full_picture': full_picture,
            'timeline': timeline,
            'evidence_count': len(all_evidence)
        }
    
    def identify_missing_context(self, claim: str, evidence: str) -> List[str]:
        """Identify what context is missing"""
        prompt = f"""
Original claim: {claim}

Evidence found:
{evidence}

What important context is missing from the original claim? What should readers know to understand the full story?

Provide 3-5 bullet points of missing context. Be specific and factual.
Format as a simple list, one point per line, starting with a dash (-)
"""
        
        try:
            response = self.qwen.simple_prompt(prompt)
            
            # Parse bullet points
            lines = response.strip().split('\n')
            context_points = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    point = line[1:].strip()
                    if point:
                        context_points.append(point)
                elif line and len(context_points) < 5:
                    # Include numbered points or regular lines
                    clean_line = re.sub(r'^\d+\.?\s*', '', line)
                    if clean_line:
                        context_points.append(clean_line)
            
            return context_points[:5]
            
        except Exception as e:
            return [f"Unable to analyze context: {str(e)}"]
    
    def generate_full_picture(self, claim: str, evidence: str, missing_context: List[str]) -> str:
        """Generate a comprehensive summary"""
        prompt = f"""
Based on the original claim and evidence found, provide a brief, balanced summary of the full story.

Original claim: {claim}

Evidence: {evidence}

Missing context identified:
{chr(10).join(f"- {point}" for point in missing_context)}

Write a 2-3 sentence summary that gives readers the complete picture.
Be objective and factual.
"""
        
        try:
            response = self.qwen.simple_prompt(prompt)
            return response.strip()
        except Exception as e:
            return f"Unable to generate full picture: {str(e)}"
    
    def extract_timeline(self, evidence: List[Dict]) -> List[Dict]:
        """Extract timeline events from evidence"""
        timeline = []
        
        for item in evidence:
            text = f"{item.get('title', '')} {item.get('snippet', '')}"
            
            # Find dates in text
            dates = self.extract_dates_from_text(text)
            
            for date_str, date_obj in dates:
                timeline.append({
                    'date': date_str,
                    'date_normalized': date_obj.strftime('%Y-%m-%d') if date_obj else date_str,
                    'event': item.get('title', '')[:100],
                    'source': item.get('url', '')
                })
        
        # Sort by date (most recent first)
        timeline.sort(key=lambda x: x.get('date_normalized', ''), reverse=True)
        
        return timeline[:10]
    
    def extract_dates_from_text(self, text: str) -> List[tuple]:
        """Extract dates from text"""
        dates = []
        
        # Common date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD-MM-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? \d{4}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                try:
                    date_obj = dateparser.parse(date_str)
                    if date_obj:
                        dates.append((date_str, date_obj))
                except:
                    continue
        
        return dates
