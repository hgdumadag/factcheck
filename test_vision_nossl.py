"""
Test Qwen Vision API with SSL verification disabled
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey patch requests to disable SSL verification
import requests
from functools import partialmethod
requests.Session.request = partialmethod(requests.Session.request, verify=False)

print("\n" + "=" * 60)
print("QWEN VISION API TEST (SSL verification disabled)")
print("=" * 60 + "\n")

# Check API key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    print("ERROR: DASHSCOPE_API_KEY not found")
    sys.exit(1)
print(f"API key: {api_key[:15]}...{api_key[-4:]}\n")

# Import dashscope
import dashscope
from dashscope import MultiModalConversation, Generation
from http import HTTPStatus

dashscope.api_key = api_key

# Test text API
print("Testing qwen-plus (text)...")
try:
    response = Generation.call(
        model="qwen-plus",
        messages=[{"role": "user", "content": "Say 'OK'"}]
    )

    if response.status_code == HTTPStatus.OK:
        print(f"  SUCCESS! Response: {response.output.choices[0].message.content}\n")
    else:
        print(f"  FAILED: {response.code} - {response.message}\n")
        sys.exit(1)
except Exception as e:
    print(f"  ERROR: {e}\n")
    sys.exit(1)

# Test vision API
print("Testing qwen-vl-plus (vision)...")
try:
    response = MultiModalConversation.call(
        model="qwen-vl-plus",
        messages=[{
            "role": "user",
            "content": [{"text": "Say 'Vision works'"}]
        }]
    )

    print(f"  Status: {response.status_code}")

    if response.status_code == HTTPStatus.OK:
        content = response.output.choices[0].message.content[0]['text']
        print(f"  SUCCESS! Response: {content}\n")
        print("=" * 60)
        print("YOUR API KEY SUPPORTS VISION MODELS!")
        print("=" * 60)
    else:
        print(f"  Code: {response.code}")
        print(f"  Message: {response.message}\n")

        if 'ModelServiceNotFound' in str(response.code) or 'model service not found' in str(response.message).lower():
            print("=" * 60)
            print("YOUR API KEY DOES NOT SUPPORT VISION MODELS")
            print("=" * 60)
            print("\nYour key works for text models (qwen-plus) but NOT")
            print("for vision models (qwen-vl-plus).")
            print("\nSOLUTIONS:")
            print("1. Enable vision models in Alibaba Cloud console")
            print("2. Use local OCR instead of vision API")
            print("=" * 60)
        else:
            print(f"Unknown error: {response.code}")

except Exception as e:
    print(f"  EXCEPTION: {e}\n")

print("\n")
