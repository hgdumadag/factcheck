"""
Test script to verify the fact-checker setup
Run this after setting up to test the system
"""

import requests
import json

# Test the backend is running
def test_health():
    try:
        response = requests.get("http://localhost:8000/")
        print("✓ Backend is running!")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Backend not running: {e}")
        return False

# Test fact-checking with sample text
def test_factcheck():
    try:
        sample_text = "Water boils at 100 degrees Celsius at sea level."
        
        response = requests.post(
            "http://localhost:8000/api/factcheck/text",
            json={"text": sample_text},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Fact-check test successful!")
            print(f"  Main Claim: {result['main_claim']}")
            print(f"  Verdict: {result['verdict']}")
            print(f"  Confidence: {result['confidence']}")
            return True
        else:
            print(f"\n✗ Fact-check failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ Fact-check test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Fact-Checker MVP Test Suite")
    print("=" * 50)
    print("\nTesting backend health...")
    
    if test_health():
        print("\nTesting fact-check functionality...")
        test_factcheck()
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)
