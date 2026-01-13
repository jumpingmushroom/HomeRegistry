from typing import List, Dict, Any
import google.generativeai as genai
from PIL import Image
from .base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini AI Provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash for speed and cost-effectiveness
        # Can be changed to gemini-1.5-pro for better quality
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_images(self, image_paths: List[str], prompt: str) -> Dict[str, Any]:
        """Analyze images using Gemini Vision"""
        try:
            # Prepare image parts
            parts = []

            # Add text prompt first
            parts.append(prompt)

            # Add images
            for image_path in image_paths:
                # Open image with PIL
                img = Image.open(image_path)
                parts.append(img)

            # Generate content
            response = self.model.generate_content(parts)

            # Parse response
            response_text = response.text
            return self._parse_json_response(response_text)

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def test_connection(self) -> tuple[bool, str]:
        """Test Gemini API connection"""
        try:
            # Make a simple text-only API call to test connection
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hi")

            # If we got a response, connection is successful
            if response and response.text:
                return True, "Connection successful"
            else:
                return False, "No response from Gemini API"

        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                return False, "Invalid API key"
            elif "quota" in error_msg.lower():
                return False, "API quota exceeded"
            else:
                return False, f"Connection failed: {error_msg}"
