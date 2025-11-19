"""
Test Qwen Vision API with SSL fix
"""

import os
import sys
import ssl
from dotenv import load_dotenv

load_dotenv()

# Fix SSL certificate verification issue
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("\n" + "=" * 60)
print("QWEN VISION API TEST (with SSL fix)")
print("=" * 60 + "\n")

# Test 1: Check API key
print("Test 1: Checking API key...")
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    print("ERROR: DASHSCOPE_API_KEY not found in .env")
    sys.exit(1)
print(f"API key found: {api_key[:15]}...{api_key[-4:]}\n")

# Test 2: Import and configure dashscope
print("Test 2: Setting up dashscope...")
try:
    import dashscope
    from dashscope import MultiModalConversation, Generation
    from http import HTTPStatus

    # Set API key
    dashscope.api_key = api_key

    # Disable SSL verification (only for testing!)
    # IMPORTANT: In production, fix your SSL certificates instead
    import http.client
    http.client.HTTPSConnection._context = ssl._create_unverified_context()

    print("dashscope configured\n")
except ImportError as e:
    print(f"ERROR: {e}\n")
    sys.exit(1)

# Test 3: Try text API first
print("Test 3: Testing Qwen text API (qwen-plus)...")
try:
    response = Generation.call(
        model="qwen-plus",
        messages=[{"role": "user", "content": "Respond with just the word 'SUCCESS'"}]
    )

    if response.status_code == HTTPStatus.OK:
        print("SUCCESS: Text API works!")
        print(f"Response: {response.output.choices[0].message.content}\n")
    else:
        print(f"FAILED:")
        print(f"  Status: {response.status_code}")
        print(f"  Code: {response.code}")
        print(f"  Message: {response.message}\n")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}\n")
    sys.exit(1)

# Test 4: Try vision API
print("Test 4: Testing Qwen Vision API (qwen-vl-plus)...")
try:
    messages = [{
        "role": "user",
        "content": [{"text": "Respond with just the words 'VISION API WORKS'"}]
    }]

    response = MultiModalConversation.call(
        model="qwen-vl-plus",
        messages=messages
    )

    print(f"Status code: {response.status_code}")

    if response.status_code == HTTPStatus.OK:
        print("SUCCESS: Vision API works!\n")
        content = response.output.choices[0].message.content[0]['text']
        print(f"Response: {content}\n")
        print("=" * 60)
        print("RESULT: Your API key SUPPORTS vision models!")
        print("        You can use qwen-vl-plus for image processing")
        print("=" * 60)
    else:
        print(f"FAILED:")
        print(f"  Code: {response.code}")
        print(f"  Message: {response.message}")
        print(f"\n" + "=" * 60)
        print("DIAGNOSIS:")

        error_msg = str(response.message).lower()
        error_code = str(response.code)

        if 'invalidapikey' in error_code.lower() or 'invalid' in error_msg:
            print("  Your API key is INVALID or EXPIRED")
            print("  Solution: Check your Alibaba Cloud DashScope console")

        elif 'notfound' in error_code.lower() or 'not found' in error_msg or 'model service not found' in error_msg:
            print("  Your API key does NOT have access to vision models!")
            print("  ")
            print("  The 'qwen-vl-plus' model is not available with your key.")
            print("  ")
            print("  Solutions:")
            print("    1. Enable vision models in Alibaba Cloud DashScope console")
            print("    2. Get a new API key with vision model access")
            print("    3. Use local OCR (Tesseract) instead:")
            print("       - Set use_vision_api=False when creating InputProcessor")

        elif 'quota' in error_msg or 'arrearage' in error_code.lower():
            print("  QUOTA EXCEEDED or INSUFFICIENT CREDITS")
            print("  Solution: Add credits to your Alibaba Cloud account")

        else:
            print(f"  Unknown error: {response.code} - {response.message}")

        print("=" * 60)

except Exception as e:
    print(f"EXCEPTION: {e}\n")
    print(f"This usually means:")
    print("  - Network connection issue")
    print("  - API endpoint unavailable")
    print("=" * 60)

print("\n")
