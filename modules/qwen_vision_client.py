"""
Alibaba Qwen Vision (VL) Client
Handles image + text multimodal inputs using Qwen-VL models
"""

import os
import json
import base64
from typing import Dict, List, Optional, Union
import dashscope
from dashscope import MultiModalConversation
from http import HTTPStatus


class QwenVisionClient:
    """Client for Alibaba Qwen Vision (VL) models"""

    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not found in environment variables")

        dashscope.api_key = self.api_key

        # Use qwen-vl-plus for vision tasks (supports images)
        # Options: qwen-vl-plus, qwen-vl-max
        self.model = "qwen-vl-plus"

    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image file to base64 string

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded string
        """
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image_with_text(
        self,
        image_path: str,
        prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Analyze an image with a text prompt using Qwen-VL

        Args:
            image_path: Path to the image file
            prompt: Text prompt/question about the image
            temperature: Sampling temperature (0-1)

        Returns:
            Response text from Qwen-VL
        """
        try:
            # Method 1: Using local file path (recommended for local files)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": f"file://{os.path.abspath(image_path)}"},
                        {"text": prompt}
                    ]
                }
            ]

            response = MultiModalConversation.call(
                model=self.model,
                messages=messages,
                temperature=temperature
            )

            if response.status_code == HTTPStatus.OK:
                return response.output.choices[0].message.content[0]['text']
            else:
                # Provide detailed error information
                error_msg = f"Qwen-VL API error: {response.code} - {response.message}"
                raise Exception(error_msg)

        except Exception as e:
            error_str = str(e)

            # Check for common errors
            if 'InvalidApiKey' in error_str or 'invalid api-key' in error_str.lower():
                raise Exception(
                    f"Invalid API Key. Please verify:\n"
                    f"1. API key is correct in .env file\n"
                    f"2. API key has access to Qwen-VL models\n"
                    f"3. You have sufficient credits\n"
                    f"Original error: {error_str}"
                )
            elif 'model not found' in error_str.lower():
                raise Exception(
                    f"Model '{self.model}' not available. "
                    f"Your API key may not have access to vision models. "
                    f"Original error: {error_str}"
                )
            elif 'quota' in error_str.lower() or 'insufficient' in error_str.lower():
                raise Exception(f"API quota exceeded or insufficient credits: {error_str}")
            else:
                raise Exception(f"Failed to call Qwen-VL API: {error_str}")

    def analyze_image_with_base64(
        self,
        image_base64: str,
        prompt: str,
        temperature: float = 0.7
    ) -> str:
        """
        Analyze an image using base64 encoded data

        Args:
            image_base64: Base64 encoded image data
            prompt: Text prompt/question about the image
            temperature: Sampling temperature (0-1)

        Returns:
            Response text from Qwen-VL
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image;base64,{image_base64}"},
                        {"text": prompt}
                    ]
                }
            ]

            response = MultiModalConversation.call(
                model=self.model,
                messages=messages,
                temperature=temperature
            )

            if response.status_code == HTTPStatus.OK:
                return response.output.choices[0].message.content[0]['text']
            else:
                error_msg = f"Qwen-VL API error: {response.code} - {response.message}"
                raise Exception(error_msg)

        except Exception as e:
            raise Exception(f"Failed to call Qwen-VL API: {str(e)}")

    def extract_claims_from_image(self, image_path: str) -> Dict:
        """
        Extract factual claims from an image containing text

        Args:
            image_path: Path to image file

        Returns:
            Dict with extracted claims structure
        """
        prompt = """
Analyze this image and extract any factual claims or text visible in it.
Return as JSON with the following structure:

{
    "visible_text": "all text you can see in the image",
    "main_claim": "primary claim being made",
    "key_facts": [
        {"claim": "specific fact 1", "checkable": true},
        {"claim": "specific fact 2", "checkable": false}
    ],
    "entities": ["person1", "organization1", "location1"],
    "dates_mentioned": ["date1", "date2"],
    "image_description": "brief description of what the image shows"
}

Important:
- Extract ALL visible text accurately
- Identify verifiable factual claims
- Note any named entities (people, organizations, places)
- Extract any dates or time references
- Describe the image content briefly
"""

        try:
            response_text = self.analyze_image_with_text(image_path, prompt, temperature=0.3)

            # Try to parse JSON response
            try:
                # Remove markdown code blocks if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                result = json.loads(response_text)

                # Ensure required fields exist
                if 'main_claim' not in result:
                    result['main_claim'] = result.get('visible_text', '')[:200]
                if 'key_facts' not in result:
                    result['key_facts'] = []
                if 'entities' not in result:
                    result['entities'] = []
                if 'dates_mentioned' not in result:
                    result['dates_mentioned'] = []
                if 'visible_text' not in result:
                    result['visible_text'] = result.get('main_claim', '')

                return result

            except json.JSONDecodeError:
                # Fallback: use response as visible text
                return {
                    "visible_text": response_text,
                    "main_claim": response_text[:200],
                    "key_facts": [{"claim": response_text[:200], "checkable": True}],
                    "entities": [],
                    "dates_mentioned": [],
                    "image_description": "Could not parse structured response"
                }

        except Exception as e:
            raise Exception(f"Failed to extract claims from image: {str(e)}")

    def simple_image_query(self, image_path: str, question: str) -> str:
        """
        Ask a simple question about an image

        Args:
            image_path: Path to image file
            question: Question to ask about the image

        Returns:
            Answer text
        """
        return self.analyze_image_with_text(image_path, question)
