"""
Simple test for Qwen Vision API
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("\n" + "=" * 60)
print("QWEN VISION API TEST")
print("=" * 60 + "\n")

# Test 1: Check API key
print("Test 1: Checking API key...")
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    print("ERROR: DASHSCOPE_API_KEY not found in .env")
    sys.exit(1)
print(f"API key found: {api_key[:15]}...{api_key[-4:]}\n")

# Test 2: Import dashscope
print("Test 2: Importing dashscope...")
try:
    import dashscope
    from dashscope import MultiModalConversation
    from http import HTTPStatus
    print("dashscope imported successfully\n")
except ImportError as e:
    print(f"ERROR: {e}\n")
    sys.exit(1)

# Test 3: Try text API first
print("Test 3: Testing Qwen text API (qwen-plus)...")
try:
    from dashscope import Generation
    dashscope.api_key = api_key

    response = Generation.call(
        model="qwen-plus",
        messages=[{"role": "user", "content": "Say hello"}]
    )

    if response.status_code == HTTPStatus.OK:
        print("SUCCESS: Text API works!")
        print(f"Response: {response.output.choices[0].message.content[:50]}...\n")
    else:
        print(f"FAILED: Status {response.status_code}, Code: {response.code}, Message: {response.message}\n")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}\n")
    sys.exit(1)

# Test 4: Try vision API
print("Test 4: Testing Qwen Vision API (qwen-vl-plus)...")
try:
    messages = [{
        "role": "user",
        "content": [{"text": "Say 'Vision API works'"}]
    }]

    response = MultiModalConversation.call(
        model="qwen-vl-plus",
        messages=messages
    )

    print(f"Status code: {response.status_code}")

    if response.status_code == HTTPStatus.OK:
        print("SUCCESS: Vision API works!")
        content = response.output.choices[0].message.content[0]['text']
        print(f"Response: {content}\n")
        print("=" * 60)
        print("RESULT: Your API key supports vision models!")
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
            print("    3. Use local OCR (Tesseract) instead of vision API")

        elif 'quota' in error_msg or 'arrearage' in error_code.lower():
            print("  QUOTA EXCEEDED or INSUFFICIENT CREDITS")
            print("  Solution: Add credits to your Alibaba Cloud account")

        else:
            print(f"  Unknown error: {response.code} - {response.message}")

        print("=" * 60)

except Exception as e:
    print(f"EXCEPTION: {e}")
    print(f"\nThis usually means:")
    print("  - Network connection issue")
    print("  - Package compatibility issue")
    print("=" * 60)

print("\n")
