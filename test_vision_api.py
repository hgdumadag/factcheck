"""
Test script to verify Qwen Vision API configuration
This will help diagnose API key and model access issues
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key_exists():
    """Test if API key is set"""
    print("=" * 60)
    print("TEST 1: Checking API Key Configuration")
    print("=" * 60)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ FAIL: DASHSCOPE_API_KEY not found in .env file")
        return False

    if api_key == "your_api_key_here":
        print("❌ FAIL: API key is still the default placeholder")
        return False

    print(f"[OK] API key found: {api_key[:10]}...{api_key[-4:]}")
    return True


def test_dashscope_import():
    """Test if dashscope package is installed"""
    print("\n" + "=" * 60)
    print("TEST 2: Checking DashScope Package")
    print("=" * 60)

    try:
        import dashscope
        print(f"✓ dashscope package installed (version: {dashscope.__version__})")
        return True
    except ImportError as e:
        print(f"❌ FAIL: dashscope not installed: {e}")
        print("Run: pip install dashscope")
        return False


def test_qwen_text_api():
    """Test basic Qwen text API (qwen-plus)"""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Qwen Text API (qwen-plus)")
    print("=" * 60)

    try:
        from modules.qwen_client import QwenClient

        client = QwenClient()
        response = client.simple_prompt("Say 'API key is valid' if you can read this.")

        print(f"✓ Text API works!")
        print(f"  Response: {response[:100]}...")
        return True

    except Exception as e:
        print(f"❌ FAIL: Text API error: {e}")
        return False


def test_qwen_vision_api_simple():
    """Test Qwen Vision API with a simple prompt (no image)"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Qwen Vision API Access (qwen-vl-plus)")
    print("=" * 60)

    try:
        import dashscope
        from dashscope import MultiModalConversation
        from http import HTTPStatus

        api_key = os.getenv("DASHSCOPE_API_KEY")
        dashscope.api_key = api_key

        # Try to call the vision model with text only
        messages = [
            {
                "role": "user",
                "content": [
                    {"text": "Say 'Vision API works' if you can read this."}
                ]
            }
        ]

        response = MultiModalConversation.call(
            model="qwen-vl-plus",
            messages=messages
        )

        if response.status_code == HTTPStatus.OK:
            print("✓ Vision API access confirmed!")
            print(f"  Model: qwen-vl-plus")
            try:
                content = response.output.choices[0].message.content[0]['text']
                print(f"  Response: {content[:100]}...")
            except:
                print(f"  Response: {response.output}")
            return True
        else:
            print(f"❌ FAIL: Vision API returned status code: {response.status_code}")
            print(f"  Error code: {response.code}")
            print(f"  Error message: {response.message}")

            # Provide specific guidance
            if 'InvalidApiKey' in str(response.code):
                print("\n💡 SOLUTION: Your API key is invalid or expired")
                print("   - Verify the key in .env file is correct")
                print("   - Check your Alibaba Cloud console")

            elif 'ModelNotFound' in str(response.code) or 'model service not found' in str(response.message).lower():
                print("\n💡 SOLUTION: Your API key doesn't have access to qwen-vl-plus")
                print("   - Your key may only support text models (qwen-plus, qwen-turbo)")
                print("   - Vision models require a different subscription/plan")
                print("   - Check your Alibaba Cloud DashScope console")
                print("   - You may need to enable vision models in your account")

            elif 'Arrearage' in str(response.code) or 'quota' in str(response.message).lower():
                print("\n💡 SOLUTION: Insufficient balance or quota exceeded")
                print("   - Add credits to your Alibaba Cloud account")
                print("   - Check your usage quota limits")

            return False

    except Exception as e:
        print(f"❌ FAIL: Exception when calling Vision API: {e}")
        print(f"\n💡 This might indicate:")
        print("   - Network connectivity issues")
        print("   - Package version mismatch")
        print("   - API endpoint changes")
        return False


def test_vision_client():
    """Test the custom QwenVisionClient"""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Custom Vision Client")
    print("=" * 60)

    try:
        from modules.qwen_vision_client import QwenVisionClient

        client = QwenVisionClient()
        print(f"✓ QwenVisionClient initialized successfully")
        print(f"  Model: {client.model}")
        return True

    except Exception as e:
        print(f"❌ FAIL: Could not initialize QwenVisionClient: {e}")
        return False


def test_available_models():
    """Check which models are available with your API key"""
    print("\n" + "=" * 60)
    print("TEST 6: Checking Available Models")
    print("=" * 60)

    import dashscope
    from dashscope import Generation, MultiModalConversation
    from http import HTTPStatus

    api_key = os.getenv("DASHSCOPE_API_KEY")
    dashscope.api_key = api_key

    # Test different models
    models_to_test = [
        ("qwen-plus", "text", Generation),
        ("qwen-turbo", "text", Generation),
        ("qwen-max", "text", Generation),
        ("qwen-vl-plus", "vision", MultiModalConversation),
        ("qwen-vl-max", "vision", MultiModalConversation),
    ]

    available_models = []

    for model_name, model_type, api_class in models_to_test:
        try:
            if model_type == "text":
                response = api_class.call(
                    model=model_name,
                    messages=[{"role": "user", "content": "test"}]
                )
            else:  # vision
                response = api_class.call(
                    model=model_name,
                    messages=[{
                        "role": "user",
                        "content": [{"text": "test"}]
                    }]
                )

            if response.status_code == HTTPStatus.OK:
                print(f"  ✓ {model_name:20} - Available")
                available_models.append(model_name)
            else:
                print(f"  ✗ {model_name:20} - Not available ({response.code})")

        except Exception as e:
            print(f"  ✗ {model_name:20} - Error: {str(e)[:50]}")

    return len(available_models) > 0


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print(" " * 10 + "QWEN VISION API DIAGNOSTIC TESTS")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("API Key Configuration", test_api_key_exists()))
    results.append(("DashScope Package", test_dashscope_import()))
    results.append(("Qwen Text API", test_qwen_text_api()))
    results.append(("Qwen Vision API", test_qwen_vision_api_simple()))
    results.append(("Vision Client", test_vision_client()))
    results.append(("Available Models", test_available_models()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    if passed == total:
        print("🎉 All tests passed! Your Qwen Vision API is properly configured.")
        print("\nYou can now use image processing with:")
        print("  - Qwen Vision API (more accurate, requires API credits)")
        print("  - Or fallback to local OCR (Tesseract)")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")

        if not results[3][1]:  # Vision API test failed
            print("\n📌 IMPORTANT: Vision API Not Available")
            print("   Your API key likely doesn't support qwen-vl-plus model.")
            print("\n   OPTIONS:")
            print("   1. Enable vision models in your Alibaba Cloud DashScope account")
            print("   2. Use a different API key with vision access")
            print("   3. Use local OCR (Tesseract) instead:")
            print("      - Install Tesseract: https://github.com/tesseract-ocr/tesseract")
            print("      - Set use_vision_api=False in input_processor")

    print("\n" + "=" * 60)
    print()


if __name__ == "__main__":
    main()
