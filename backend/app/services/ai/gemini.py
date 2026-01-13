from typing import List, Dict, Any, Optional
import google.generativeai as genai
from PIL import Image
from .base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini AI Provider"""

    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Use provided model or default to gemini-pro-vision
        self.model_name = model_name or 'gemini-pro-vision'
        self.model = genai.GenerativeModel(self.model_name)

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
            response = self.model.generate_content("Hi")

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

    @staticmethod
    def list_available_models(api_key: str) -> List[Dict[str, Any]]:
        """List all available Gemini models that support vision/multimodal"""
        try:
            genai.configure(api_key=api_key)
            models = []

            for model in genai.list_models():
                # Check if model supports generateContent (needed for our use case)
                if 'generateContent' in model.supported_generation_methods:
                    # Check if model supports vision (has vision in name or supports image input)
                    supports_vision = (
                        'vision' in model.name.lower() or
                        'pro' in model.name.lower() or
                        'flash' in model.name.lower()
                    )

                    models.append({
                        'name': model.name,
                        'display_name': model.display_name,
                        'description': model.description if hasattr(model, 'description') else None,
                        'supports_vision': supports_vision
                    })

            # Filter to only models that support vision
            vision_models = [m for m in models if m['supports_vision']]
            return vision_models if vision_models else models  # Fallback to all if none marked as vision

        except Exception as e:
            raise Exception(f"Failed to list models: {str(e)}")
