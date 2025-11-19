"""
Search Engine Module
Searches multiple sources for verification
"""

import requests
from typing import Dict, List
from duckduckgo_search import DDGS
import os


class MVPSearchEngine:
    """Search engine for fact verification"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        
        # Known fact-checking websites
        self.factcheck_sites = [
            "snopes.com",
            "factcheck.org",
            "politifact.com",
            "reuters.com/fact-check",
            "apnews.com/ap-fact-check",
            "fullfact.org"
        ]
    
    def search_and_verify(self, claims: Dict) -> Dict:
        """
        Search for evidence across multiple sources
        
        Args:
            claims: Extracted claims dict
            
        Returns:
            Dict with direct_evidence, context, and existing_factchecks
        """
        main_claim = claims.get('main_claim', '')
        
        # Search for main claim
        direct_evidence = self.search_multiple_sources(main_claim)
        
        # Search for context
        context_query = f"{main_claim} full story context background"
        context_results = self.search_multiple_sources(context_query)
        
        # Search for existing fact-checks
        factcheck_query = f"{main_claim} fact check debunk verify"
        factcheck_results = self.check_factcheck_sites(main_claim)
        
        return {
            'direct_evidence': direct_evidence[:5],
            'context': context_results[:5],
            'existing_factchecks': factcheck_results[:3]
        }
    
    def search_multiple_sources(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search multiple sources"""
        results = []
        
        # 1. DuckDuckGo search (free, no API key needed)
        ddg_results = self.search_duckduckgo(query, max_results=max_results)
        results.extend(ddg_results)
        
        # 2. Google Custom Search (if configured)
        if self.google_api_key and self.google_cse_id:
            google_results = self.search_google(query, max_results=3)
            results.extend(google_results)
        
        return results[:max_results]
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo"""
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=max_results))
                
                formatted_results = []
                for result in search_results:
                    formatted_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', ''),
                        'source': 'duckduckgo'
                    })
                
                return formatted_results
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def search_google(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search using Google Custom Search API"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            formatted_results = []
            
            for item in data.get('items', []):
                formatted_results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': 'google'
                })
            
            return formatted_results
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    def check_factcheck_sites(self, query: str) -> List[Dict]:
        """Search specifically on fact-checking websites"""
        results = []
        
        # Search DuckDuckGo restricted to fact-check sites
        for site in self.factcheck_sites[:3]:  # Limit to 3 sites for MVP
            site_query = f"site:{site} {query}"
            try:
                site_results = self.search_duckduckgo(site_query, max_results=2)
                for result in site_results:
                    result['factcheck_site'] = True
                    result['factcheck_source'] = site
                results.extend(site_results)
            except Exception as e:
                print(f"Error searching {site}: {e}")
                continue
        
        return results
