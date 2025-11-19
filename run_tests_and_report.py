"""
Test Runner with HTML Report Generation
Runs all tests and creates a comprehensive HTML report
"""

import unittest
import sys
import os
from datetime import datetime
from io import StringIO
import json

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class HTMLTestResult(unittest.TextTestResult):
    """Custom test result that captures detailed information"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def startTest(self, test):
        super().startTest(test)
        self.start_time = datetime.now()
    
    def stopTest(self, test):
        super().stopTest(test)
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0.0
        
        # Determine status
        status = "PASS"
        message = ""
        error_type = ""
        
        # Check if test failed
        for failure in self.failures:
            if failure[0] == test:
                status = "FAIL"
                message = failure[1]
                error_type = "Assertion Error"
                break
        
        # Check if test had error
        for error in self.errors:
            if error[0] == test:
                status = "ERROR"
                message = error[1]
                error_type = "Exception"
                break
        
        # Check if test was skipped
        for skipped in self.skipped:
            if skipped[0] == test:
                status = "SKIP"
                message = skipped[1]
                error_type = "Skipped"
                break
        
        self.test_results.append({
            'name': str(test),
            'doc': test.shortDescription() or str(test),
            'status': status,
            'duration': duration,
            'message': message,
            'error_type': error_type
        })


def generate_html_report(result, output_file='test_report.html'):
    """Generate comprehensive HTML report"""
    
    # Calculate statistics
    total_tests = result.testsRun
    passed = total_tests - len(result.failures) - len(result.errors) - len(result.skipped)
    failed = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    # Get test results
    test_results = result.test_results if hasattr(result, 'test_results') else []
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fact-Checker MVP - Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .timestamp {{
            margin-top: 15px;
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card.total .stat-value {{ color: #667eea; }}
        .stat-card.passed .stat-value {{ color: #4caf50; }}
        .stat-card.failed .stat-value {{ color: #f44336; }}
        .stat-card.errors .stat-value {{ color: #ff9800; }}
        .stat-card.skipped .stat-value {{ color: #9e9e9e; }}
        
        .success-rate {{
            grid-column: 1 / -1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
        }}
        
        .success-rate-value {{
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .progress-bar {{
            background: rgba(255,255,255,0.3);
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 20px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: white;
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #667eea;
        }}
        
        .tests-section {{
            padding: 40px;
        }}
        
        .section-title {{
            font-size: 1.8rem;
            margin-bottom: 25px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .filter-btn:hover {{
            background: #667eea;
            color: white;
        }}
        
        .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .test-list {{
            display: grid;
            gap: 15px;
        }}
        
        .test-item {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
        }}
        
        .test-item:hover {{
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateX(5px);
        }}
        
        .test-item.pass {{
            border-left: 5px solid #4caf50;
        }}
        
        .test-item.fail {{
            border-left: 5px solid #f44336;
        }}
        
        .test-item.error {{
            border-left: 5px solid #ff9800;
        }}
        
        .test-item.skip {{
            border-left: 5px solid #9e9e9e;
            opacity: 0.7;
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }}
        
        .test-name {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            flex: 1;
        }}
        
        .test-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .test-status.pass {{
            background: #4caf50;
            color: white;
        }}
        
        .test-status.fail {{
            background: #f44336;
            color: white;
        }}
        
        .test-status.error {{
            background: #ff9800;
            color: white;
        }}
        
        .test-status.skip {{
            background: #9e9e9e;
            color: white;
        }}
        
        .test-description {{
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 10px;
        }}
        
        .test-duration {{
            font-size: 0.85rem;
            color: #999;
        }}
        
        .test-message {{
            margin-top: 15px;
            padding: 15px;
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .test-message.error {{
            background: #f8d7da;
            border-left-color: #f44336;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
        }}
        
        .footer p {{
            margin: 5px 0;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .stat-value {{
                font-size: 2rem;
            }}
            
            .success-rate-value {{
                font-size: 3rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Fact-Checker MVP Test Report</h1>
            <p>Comprehensive Test Suite Results</p>
            <div class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="summary">
            <div class="stat-card total">
                <div class="stat-value">{total_tests}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            
            <div class="stat-card passed">
                <div class="stat-value">{passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            
            <div class="stat-card failed">
                <div class="stat-value">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            
            <div class="stat-card errors">
                <div class="stat-value">{errors}</div>
                <div class="stat-label">Errors</div>
            </div>
            
            <div class="stat-card skipped">
                <div class="stat-value">{skipped}</div>
                <div class="stat-label">Skipped</div>
            </div>
            
            <div class="success-rate">
                <div class="success-rate-value">{success_rate:.1f}%</div>
                <div>Success Rate</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate}%">
                        {success_rate:.1f}%
                    </div>
                </div>
            </div>
        </div>
        
        <div class="tests-section">
            <h2 class="section-title">Test Results Details</h2>
            
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterTests('all')">All Tests</button>
                <button class="filter-btn" onclick="filterTests('pass')">Passed ({passed})</button>
                <button class="filter-btn" onclick="filterTests('fail')">Failed ({failed})</button>
                <button class="filter-btn" onclick="filterTests('error')">Errors ({errors})</button>
                <button class="filter-btn" onclick="filterTests('skip')">Skipped ({skipped})</button>
            </div>
            
            <div class="test-list" id="testList">
"""
    
    # Add test items
    for i, test in enumerate(test_results, 1):
        status_class = test['status'].lower()
        message_html = ""
        
        if test['message']:
            message_class = 'error' if test['status'] == 'ERROR' else ''
            # Escape and limit message length
            safe_message = str(test['message'])[:1000]
            message_html = f'<div class="test-message {message_class}">{safe_message}</div>'
        
        html_content += f"""
                <div class="test-item {status_class}" data-status="{status_class}">
                    <div class="test-header">
                        <div class="test-name">{test['doc']}</div>
                        <div class="test-status {status_class}">{test['status']}</div>
                    </div>
                    <div class="test-description">{test['name']}</div>
                    <div class="test-duration">⏱️ Duration: {test['duration']:.3f}s</div>
                    {message_html}
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Fact-Checker MVP</strong> - Powered by Alibaba Qwen 3</p>
            <p>Test Suite Version 1.0</p>
        </div>
    </div>
    
    <script>
        function filterTests(status) {
            const items = document.querySelectorAll('.test-item');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Update button states
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter tests
            items.forEach(item => {
                if (status === 'all' || item.dataset.status === status) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML Report generated: {output_file}")
    return output_file


def run_all_tests():
    """Run all tests and generate HTML report"""
    
    print("=" * 80)
    print("FACT-CHECKER MVP - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    # Import test suite
    from test_suite import (
        TestQwenClient, TestInputProcessor, TestClaimExtractor,
        TestSearchEngine, TestContextAnalyzer, TestVerifier, TestIntegration
    )
    
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
    
    # Run tests with custom result collector
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=HTMLTestResult)
    result = runner.run(suite)
    
    # Print test output
    print(stream.getvalue())
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)) / result.testsRun) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print("=" * 80)
    
    # Generate HTML report
    report_file = generate_html_report(result)
    
    return result, report_file


if __name__ == '__main__':
    result, report_file = run_all_tests()
    
    print()
    print("🎉 Testing complete!")
    print(f"📄 View full report: {os.path.abspath(report_file)}")
