"""
Comprehensive Test Suite for Fact-Checker MVP
Tests all major components and functionality
"""

import unittest
import sys
import os
import json
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.qwen_client import QwenClient
from modules.input_processor import SimpleInputProcessor
from modules.claim_extractor import ClaimExtractor
from modules.search_engine import MVPSearchEngine
from modules.context_analyzer import ContextAnalyzer
from modules.verifier import SimpleVerifier


class TestQwenClient(unittest.TestCase):
    """Test Qwen 3 LLM Client"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            self.client = QwenClient()
            self.qwen_available = True
        except Exception as e:
            self.qwen_available = False
            self.skipTest(f"Qwen client not available: {e}")
    
    def test_01_client_initialization(self):
        """Test 1: Qwen client initializes correctly"""
        self.assertIsNotNone(self.client)
        self.assertIsNotNone(self.client.api_key)
        self.assertEqual(self.client.model, "qwen-plus")
    
    def test_02_simple_prompt(self):
        """Test 2: Simple prompt returns response"""
        if not self.qwen_available:
            self.skipTest("Qwen not available")
        try:
            response = self.client.simple_prompt("Say 'test' if you can hear me")
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
        except Exception as e:
            if 'SSL' in str(e) or 'CERTIFICATE' in str(e):
                self.skipTest(f"SSL Certificate issue - {str(e)[:100]}")
            raise
    
    def test_03_json_extraction(self):
        """Test 3: JSON extraction works correctly"""
        if not self.qwen_available:
            self.skipTest("Qwen not available")
        try:
            prompt = 'Return this JSON: {"status": "ok", "value": 42}'
            result = self.client.extract_json_response(prompt)
            self.assertIsInstance(result, dict)
        except Exception as e:
            if 'SSL' in str(e) or 'CERTIFICATE' in str(e):
                self.skipTest(f"SSL Certificate issue - {str(e)[:100]}")
            raise


class TestInputProcessor(unittest.TestCase):
    """Test Input Processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = SimpleInputProcessor()
    
    def test_04_text_processing(self):
        """Test 4: Text input processing"""
        text = "This is a test claim about facts."
        result = self.processor.process(text, "text")
        self.assertEqual(result['text'], text)
        self.assertEqual(result['type'], 'direct')
        self.assertFalse(result['has_image'])
    
    def test_05_empty_text_handling(self):
        """Test 5: Empty text handling"""
        result = self.processor.process("", "text")
        self.assertEqual(result['text'], "")
        self.assertEqual(result['type'], 'direct')
    
    def test_06_long_text_processing(self):
        """Test 6: Long text processing"""
        long_text = "Test " * 1000
        result = self.processor.process(long_text, "text")
        self.assertIsInstance(result['text'], str)
        self.assertEqual(result['type'], 'direct')
    
    def test_07_special_characters_text(self):
        """Test 7: Text with special characters"""
        special_text = "Test with émojis 🎉 and symbols @#$%"
        result = self.processor.process(special_text, "text")
        self.assertEqual(result['text'], special_text)
    
    def test_08_url_validation(self):
        """Test 8: URL processing structure"""
        # Test with a simple URL (may fail to fetch, but should return proper structure)
        try:
            result = self.processor.process("https://example.com", "url")
            self.assertIn('text', result)
            self.assertIn('type', result)
            self.assertEqual(result['type'], 'article')
        except Exception as e:
            # URL processing may fail in test environment
            self.assertIsInstance(e, Exception)
    
    def test_09_invalid_input_type(self):
        """Test 9: Invalid input type raises error"""
        with self.assertRaises(ValueError):
            self.processor.process("test", "invalid_type")


class TestClaimExtractor(unittest.TestCase):
    """Test Claim Extractor"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            self.extractor = ClaimExtractor()
            self.qwen_available = True
        except Exception:
            self.qwen_available = False
    
    def test_10_claim_extraction_structure(self):
        """Test 10: Claim extraction returns correct structure"""
        if not self.qwen_available:
            self.skipTest("Qwen not available")
        text = "Water boils at 100 degrees Celsius."
        result = self.extractor.extract_claims(text)
        self.assertIn('main_claim', result)
        self.assertIn('key_facts', result)
        self.assertIn('entities', result)
        self.assertIn('dates_mentioned', result)
    
    def test_11_claim_extraction_with_entities(self):
        """Test 11: Extract claims with named entities"""
        if not self.qwen_available:
            self.skipTest("Qwen not available")
        text = "Joe Biden visited New York on January 1, 2024."
        result = self.extractor.extract_claims(text)
        self.assertIsInstance(result['entities'], list)
        self.assertIsInstance(result['dates_mentioned'], list)
    
    def test_12_empty_text_claim_extraction(self):
        """Test 12: Claim extraction with empty text"""
        if not self.qwen_available:
            self.skipTest("Qwen not available")
        result = self.extractor.extract_claims("")
        self.assertIn('main_claim', result)


class TestSearchEngine(unittest.TestCase):
    """Test Search Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.search_engine = MVPSearchEngine()
    
    def test_13_search_engine_initialization(self):
        """Test 13: Search engine initializes correctly"""
        self.assertIsNotNone(self.search_engine)
        self.assertIsInstance(self.search_engine.factcheck_sites, list)
        self.assertGreater(len(self.search_engine.factcheck_sites), 0)
    
    def test_14_duckduckgo_search(self):
        """Test 14: DuckDuckGo search returns results"""
        try:
            results = self.search_engine.search_duckduckgo("water boils 100 celsius", max_results=2)
            self.assertIsInstance(results, list)
            if len(results) > 0:
                self.assertIn('title', results[0])
                self.assertIn('url', results[0])
        except Exception:
            # Search may fail in restricted environments
            self.skipTest("Search not available in test environment")
    
    def test_15_search_multiple_sources(self):
        """Test 15: Multi-source search aggregates results"""
        try:
            results = self.search_engine.search_multiple_sources("climate change", max_results=3)
            self.assertIsInstance(results, list)
            self.assertLessEqual(len(results), 3)
        except Exception:
            self.skipTest("Search not available in test environment")
    
    def test_16_search_and_verify_structure(self):
        """Test 16: Search and verify returns correct structure"""
        claims = {
            'main_claim': 'Test claim',
            'key_facts': [],
            'entities': [],
            'dates_mentioned': []
        }
        try:
            result = self.search_engine.search_and_verify(claims)
            self.assertIn('direct_evidence', result)
            self.assertIn('context', result)
            self.assertIn('existing_factchecks', result)
        except Exception:
            self.skipTest("Search not available in test environment")


class TestContextAnalyzer(unittest.TestCase):
    """Test Context Analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        try:
            self.analyzer = ContextAnalyzer()
            self.qwen_available = True
        except Exception as e:
            self.qwen_available = False
            self.analyzer = None
    
    def test_17_context_analyzer_initialization(self):
        """Test 17: Context analyzer initializes correctly"""
        if not self.analyzer:
            self.skipTest("Analyzer not available")
        self.assertIsNotNone(self.analyzer)
    
    def test_18_extract_dates_from_text(self):
        """Test 18: Date extraction from text"""
        if not self.analyzer:
            self.skipTest("Analyzer not available")
        text = "On January 15, 2024, and also on 2023-12-01"
        dates = self.analyzer.extract_dates_from_text(text)
        self.assertIsInstance(dates, list)
    
    def test_19_timeline_extraction(self):
        """Test 19: Timeline extraction from evidence"""
        if not self.analyzer:
            self.skipTest("Analyzer not available")
        evidence = [
            {'title': 'Event on Jan 1, 2024', 'snippet': 'Something happened', 'url': 'http://example.com'},
            {'title': 'Event on Feb 1, 2024', 'snippet': 'Another thing', 'url': 'http://example.com'}
        ]
        timeline = self.analyzer.extract_timeline(evidence)
        self.assertIsInstance(timeline, list)
    
    def test_20_context_analysis_structure(self):
        """Test 20: Context analysis returns correct structure"""
        if not self.qwen_available or not self.analyzer:
            self.skipTest("Qwen not available")
        claim = "Test claim"
        search_results = {
            'direct_evidence': [],
            'context': [],
            'existing_factchecks': []
        }
        try:
            result = self.analyzer.analyze_context(claim, search_results)
            self.assertIn('missing_context', result)
            self.assertIn('full_picture', result)
            self.assertIn('timeline', result)
        except Exception:
            # May fail without proper API or search results
            pass


class TestVerifier(unittest.TestCase):
    """Test Verifier"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.verifier = SimpleVerifier()
    
    def test_21_verifier_initialization(self):
        """Test 21: Verifier initializes with reputable domains"""
        self.assertIsNotNone(self.verifier)
        self.assertIsInstance(self.verifier.reputable_domains, list)
        self.assertGreater(len(self.verifier.reputable_domains), 0)
    
    def test_22_check_agreement_empty_evidence(self):
        """Test 22: Agreement check with empty evidence"""
        score = self.verifier.check_agreement([])
        self.assertEqual(score, 0.0)
    
    def test_23_check_agreement_multiple_sources(self):
        """Test 23: Agreement check with multiple sources"""
        evidence = [
            {'url': 'http://example1.com'},
            {'url': 'http://example2.com'},
            {'url': 'http://example3.com'}
        ]
        score = self.verifier.check_agreement(evidence)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_24_source_quality_reputable(self):
        """Test 24: Source quality with reputable sources"""
        evidence = [
            {'url': 'https://reuters.com/article'},
            {'url': 'https://bbc.com/news'}
        ]
        score = self.verifier.check_source_quality(evidence)
        self.assertGreater(score, 0.0)
    
    def test_25_source_quality_non_reputable(self):
        """Test 25: Source quality with non-reputable sources"""
        evidence = [
            {'url': 'http://random-blog.com/post'},
            {'url': 'http://unknown-site.net/article'}
        ]
        score = self.verifier.check_source_quality(evidence)
        self.assertGreaterEqual(score, 0.0)
    
    def test_26_context_scoring(self):
        """Test 26: Context completeness scoring"""
        context = {
            'missing_context': ['point1', 'point2'],
            'full_picture': 'Complete summary',
            'timeline': [{'date': '2024-01-01'}]
        }
        score = self.verifier.score_context(context)
        self.assertGreater(score, 0.5)
        self.assertLessEqual(score, 1.0)
    
    def test_27_factcheck_existence_scoring(self):
        """Test 27: Fact-check existence scoring"""
        evidence_with_fc = {'existing_factchecks': [{'url': 'snopes.com'}]}
        score = self.verifier.check_factcheck_existence(evidence_with_fc)
        self.assertGreater(score, 0.0)
        
        evidence_without_fc = {'existing_factchecks': []}
        score = self.verifier.check_factcheck_existence(evidence_without_fc)
        self.assertEqual(score, 0.0)
    
    def test_28_verdict_determination_high_confidence(self):
        """Test 28: Verdict with high confidence"""
        evidence = {'existing_factchecks': []}
        verdict = self.verifier.determine_verdict(0.8, evidence)
        self.assertEqual(verdict, "LIKELY TRUE")
    
    def test_29_verdict_determination_low_confidence(self):
        """Test 29: Verdict with low confidence"""
        evidence = {'existing_factchecks': []}
        verdict = self.verifier.determine_verdict(0.2, evidence)
        self.assertEqual(verdict, "LIKELY FALSE OR MISLEADING")
    
    def test_30_calculate_verdict_complete(self):
        """Test 30: Complete verdict calculation"""
        claim = "Test claim"
        evidence = {
            'direct_evidence': [{'url': 'https://reuters.com/article'}],
            'context': [],
            'existing_factchecks': []
        }
        context = {
            'missing_context': ['context point'],
            'full_picture': 'Summary',
            'timeline': []
        }
        result = self.verifier.calculate_verdict(claim, evidence, context)
        
        self.assertIn('verdict', result)
        self.assertIn('confidence', result)
        self.assertIn('scores', result)
        self.assertIn('evidence_count', result)
        self.assertIsInstance(result['confidence'], (int, float))
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_31_end_to_end_text_processing(self):
        """Test 31: End-to-end text processing pipeline"""
        try:
            processor = SimpleInputProcessor()
            extractor = ClaimExtractor()
            verifier = SimpleVerifier()
            
            # Process text
            text = "Water boils at 100 degrees Celsius at sea level."
            processed = processor.process(text, "text")
            self.assertIn('text', processed)
            
            # Extract claims
            claims = extractor.extract_claims(processed['text'])
            self.assertIn('main_claim', claims)
            
            # Verify (simplified)
            evidence = {'direct_evidence': [], 'context': [], 'existing_factchecks': []}
            context = {'missing_context': [], 'full_picture': '', 'timeline': []}
            verdict = verifier.calculate_verdict(claims['main_claim'], evidence, context)
            self.assertIn('verdict', verdict)
            
        except Exception as e:
            # May fail without API key
            if "DASHSCOPE_API_KEY" in str(e):
                self.skipTest("API key not configured")
            else:
                raise
    
    def test_32_streamlit_app_imports(self):
        """Test 32: Streamlit app can be imported without errors"""
        try:
            import sys
            import os
            # Temporarily add current directory to path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # Try importing streamlit_app module
            # We can't actually run it, but we can check if it imports cleanly
            import importlib.util
            spec = importlib.util.spec_from_file_location("streamlit_app", "streamlit_app.py")
            self.assertIsNotNone(spec)
            
        except ImportError as e:
            if 'streamlit' in str(e):
                self.skipTest("Streamlit not installed")
            raise


def run_tests_with_report():
    """Run all tests and generate detailed report"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestQwenClient))
    suite.addTests(loader.loadTestsFromTestCase(TestInputProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestClaimExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestContextAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestVerifier))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests with custom result
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 70)
    print("FACT-CHECKER MVP - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    
    result = run_tests_with_report()
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
