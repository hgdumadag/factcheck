# Qwen Vision API Troubleshooting Guide

## Issue Summary

When trying to use images with Qwen API, you get an "Invalid API Key" error.

## Root Cause Analysis

After testing, we discovered **two separate issues**:

### 1. SSL Certificate Verification Error (Network Issue)
- **Symptom:** `SSL: CERTIFICATE_VERIFY_FAILED`
- **Cause:** Missing or outdated SSL certificates on your system
- **Impact:** Masks the real API error

### 2. Invalid API Key (Main Issue)
- **Symptom:** `InvalidApiKey - Invalid API-key provided`
- **Cause:** The API key `sk-add05c12b0284c12ba7ed628d88a46e5` is rejected by Qwen
- **Impact:** Cannot make ANY API calls (text or vision)

## Important Discovery

**Your code was NOT sending images to Qwen at all!**

The original implementation:
1. Uses Tesseract OCR locally to extract text from images
2. Sends the extracted text to Qwen (as text, not images)
3. Qwen never sees the actual images

To actually use Qwen's vision capabilities, you need:
- Use `qwen-vl-plus` or `qwen-vl-max` models (not `qwen-plus`)
- Use `MultiModalConversation` API (not `Generation`)
- Your API key must have access to vision models

## Solutions

### Solution 1: Fix the API Key (Required)

1. **Log into Alibaba Cloud Console:**
   ```
   https://dashscope.console.aliyun.com/
   ```

2. **Navigate to API-KEY Management**

3. **Verify your current key:**
   - Check if `sk-add05c12b0284c12ba7ed628d88a46e5` is listed
   - Check if it's marked as "Active"
   - Check expiration date

4. **Generate a NEW API key:**
   - Click "Create API Key"
   - Copy the new key immediately (you can't see it again!)
   - Replace in `.env` file:
     ```
     DASHSCOPE_API_KEY=sk-YOUR-NEW-KEY-HERE
     ```

5. **Test the new key:**
   ```bash
   venv\Scripts\python.exe test_vision_nossl.py
   ```

### Solution 2: Fix SSL Issues (Recommended for Production)

#### Option A: Proper SSL Certificate Fix (Best Practice)
```bash
# Update certifi package
pip install --upgrade certifi

# Update CA certificates on Windows
# Download and install: https://curl.se/docs/caextract.html
```

#### Option B: Disable SSL Verification (Development Only - NOT recommended)

Update `modules/qwen_client.py`:

```python
import requests
from functools import partialmethod

class QwenClient:
    def __init__(self):
        # Disable SSL verification (DEVELOPMENT ONLY!)
        requests.Session.request = partialmethod(
            requests.Session.request,
            verify=False
        )

        # ... rest of code
```

⚠️ **WARNING:** Never disable SSL in production!

### Solution 3: Enable Vision API Support

If your API key doesn't support vision models:

#### Option A: Use Vision Models (If Available)
Your API key needs to be enabled for vision models in the Alibaba Cloud console.

Files updated:
- ✅ `modules/qwen_vision_client.py` - NEW vision client
- ✅ `modules/input_processor.py` - Updated to use vision API

Usage:
```python
# Use vision API (default)
processor = SimpleInputProcessor(use_vision_api=True)

# Or use local OCR
processor = SimpleInputProcessor(use_vision_api=False)
```

#### Option B: Continue Using Local OCR
If vision models aren't available, stick with Tesseract:

```python
# In app.py
input_processor = SimpleInputProcessor(use_vision_api=False)
```

This will:
- Use Tesseract OCR to extract text from images locally
- Send extracted text to regular Qwen text models
- No vision model required

## Testing Steps

### Step 1: Test API Key (Text Model)
```bash
venv\Scripts\python.exe test_vision_nossl.py
```

Expected output if key is valid:
```
Testing qwen-plus (text)...
  SUCCESS! Response: OK
```

### Step 2: Test Vision Model Access
If Step 1 succeeds, the script automatically tests vision:

**If vision is available:**
```
Testing qwen-vl-plus (vision)...
  SUCCESS! Response: Vision works
YOUR API KEY SUPPORTS VISION MODELS!
```

**If vision is NOT available:**
```
Testing qwen-vl-plus (vision)...
  Code: ModelServiceNotFound
YOUR API KEY DOES NOT SUPPORT VISION MODELS
```

### Step 3: Test Your Application

With vision API enabled:
```bash
# Start backend
venv\Scripts\python.exe app.py

# Upload an image via the web interface
# It will use Qwen Vision to analyze it
```

## File Changes Summary

### New Files Created:
1. **`modules/qwen_vision_client.py`**
   - Handles Qwen Vision (VL) models
   - Supports local files and base64 images
   - Extracts claims from images using AI

2. **`test_vision_nossl.py`**
   - Quick diagnostic test
   - Tests both text and vision API access

3. **`test_vision_api.py`**
   - Comprehensive diagnostic test
   - Multiple test scenarios

### Modified Files:
1. **`modules/input_processor.py`**
   - Added `use_vision_api` parameter
   - Uses QwenVisionClient when enabled
   - Falls back to OCR if vision fails
   - Better error handling with specific error types

## Common Error Messages

### "Invalid API-key provided"
- **Cause:** API key is wrong, expired, or inactive
- **Fix:** Generate new key from Alibaba Cloud console

### "SSL: CERTIFICATE_VERIFY_FAILED"
- **Cause:** SSL certificate issues on your system
- **Fix:** Update certifi or disable SSL (dev only)

### "ModelServiceNotFound" (for qwen-vl-plus)
- **Cause:** API key doesn't have vision model access
- **Fix:** Enable in console OR use local OCR instead

### "Arrearage" or "Quota exceeded"
- **Cause:** Insufficient credits
- **Fix:** Add credits to Alibaba Cloud account

## Recommendations

### Immediate Actions:
1. ✅ Generate a new API key from Alibaba Cloud console
2. ✅ Update `.env` file with the new key
3. ✅ Run `test_vision_nossl.py` to verify
4. ✅ Fix SSL certificates (update certifi)

### For Production:
1. ❌ Never disable SSL verification
2. ✅ Use proper SSL certificate management
3. ✅ Store API keys in secure environment variables
4. ✅ Implement API key rotation
5. ✅ Add rate limiting and quota monitoring

### For Image Processing:
- **If vision models are available:** Use `use_vision_api=True` (more accurate)
- **If not available:** Use `use_vision_api=False` (requires Tesseract)
- **For production:** Implement fallback from vision to OCR

## Next Steps

1. **Fix API key** - This is blocking everything
2. **Test with new key** - Run diagnostic script
3. **Choose image processing method:**
   - Vision API (if available and budget allows)
   - Local OCR (free, requires Tesseract installation)
4. **Fix SSL issues** properly (don't just disable verification)

## Support Resources

- Alibaba Cloud DashScope Console: https://dashscope.console.aliyun.com/
- Qwen API Documentation: https://help.aliyun.com/zh/dashscope/
- API Key Management: https://dashscope.console.aliyun.com/apiKey

---

**Last Updated:** 2025-11-19
