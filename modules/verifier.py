"""
Verifier Module
Calculates confidence scores and verdict
"""

from typing import Dict, List


class SimpleVerifier:
    """Calculate verification verdict and confidence"""
    
    def __init__(self):
        self.reputable_domains = [
            'reuters.com', 'apnews.com', 'bbc.com', 'nytimes.com',
            'washingtonpost.com', 'theguardian.com', 'npr.org',
            'factcheck.org', 'snopes.com', 'politifact.com',
            'fullfact.org', 'who.int', 'cdc.gov', 'gov.uk'
        ]
    
    def calculate_verdict(self, claim: str, evidence: Dict, context: Dict) -> Dict:
        """
        Calculate verdict and confidence score
        
        Args:
            claim: Main claim being verified
            evidence: Search results
            context: Context analysis
            
        Returns:
            Dict with verdict, confidence, and detailed scores
        """
        # Combine all evidence
        all_evidence = []
        all_evidence.extend(evidence.get('direct_evidence', []))
        all_evidence.extend(evidence.get('context', []))
        all_evidence.extend(evidence.get('existing_factchecks', []))
        
        # Calculate individual scores
        scores = {
            'source_agreement': self.check_agreement(all_evidence),
            'reputable_sources': self.check_source_quality(all_evidence),
            'context_completeness': self.score_context(context),
            'fact_check_exists': self.check_factcheck_existence(evidence)
        }
        
        # Weighted average
        weights = {
            'source_agreement': 0.35,
            'reputable_sources': 0.30,
            'context_completeness': 0.20,
            'fact_check_exists': 0.15
        }
        
        confidence = sum(scores[k] * weights[k] for k in scores)
        
        # Determine verdict
        verdict = self.determine_verdict(confidence, evidence)
        
        return {
            'verdict': verdict,
            'confidence': round(confidence, 2),
            'scores': {k: round(v, 2) for k, v in scores.items()},
            'evidence_count': len(all_evidence)
        }
    
    def check_agreement(self, evidence: List[Dict]) -> float:
        """Check if sources agree (simplified for MVP)"""
        if not evidence:
            return 0.0
        
        # If we have multiple sources, assume moderate agreement
        # In production, this would use NLP to check if sources contradict
        if len(evidence) >= 3:
            return 0.7
        elif len(evidence) == 2:
            return 0.5
        else:
            return 0.3
    
    def check_source_quality(self, evidence: List[Dict]) -> float:
        """Check quality of sources"""
        if not evidence:
            return 0.0
        
        reputable_count = 0
        
        for item in evidence:
            url = item.get('url', '').lower()
            for domain in self.reputable_domains:
                if domain in url:
                    reputable_count += 1
                    break
        
        # Score based on percentage of reputable sources
        if len(evidence) == 0:
            return 0.0
        
        score = reputable_count / len(evidence)
        return min(score * 1.2, 1.0)  # Boost score slightly
    
    def score_context(self, context: Dict) -> float:
        """Score context completeness"""
        score = 0.5  # Base score
        
        # Bonus for having missing context identified
        if context.get('missing_context') and len(context['missing_context']) > 0:
            score += 0.2
        
        # Bonus for having full picture
        if context.get('full_picture'):
            score += 0.2
        
        # Bonus for timeline
        if context.get('timeline') and len(context['timeline']) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def check_factcheck_existence(self, evidence: Dict) -> float:
        """Check if fact-check already exists"""
        factchecks = evidence.get('existing_factchecks', [])
        
        if not factchecks:
            return 0.0
        
        # Higher score for multiple fact-checks
        if len(factchecks) >= 2:
            return 1.0
        else:
            return 0.7
    
    def determine_verdict(self, confidence: float, evidence: Dict) -> str:
        """Determine final verdict"""
        factchecks = evidence.get('existing_factchecks', [])
        
        # If fact-checks exist, they heavily influence verdict
        if factchecks:
            # In production, analyze fact-check content
            # For MVP, high confidence if fact-checks found
            if confidence > 0.6:
                return "VERIFIED BY FACT-CHECKERS"
            else:
                return "FACT-CHECKED - NEEDS CONTEXT"
        
        # Otherwise use confidence score
        if confidence > 0.7:
            return "LIKELY TRUE"
        elif confidence > 0.5:
            return "NEEDS MORE CONTEXT"
        elif confidence > 0.3:
            return "QUESTIONABLE"
        else:
            return "LIKELY FALSE OR MISLEADING"
