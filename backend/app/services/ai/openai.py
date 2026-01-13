from typing import List, Dict, Any
import openai
from .base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 Vision Provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

    async def analyze_images(self, image_paths: List[str], prompt: str) -> Dict[str, Any]:
        """Analyze images using GPT-4 Vision"""
        try:
            # Prepare content
            content = []

            for image_path in image_paths:
                # Determine media type
                ext = image_path.lower().split(".")[-1]
                media_type_map = {
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    "gif": "image/gif",
                    "webp": "image/webp"
                }
                media_type = media_type_map.get(ext, "image/jpeg")

                # Encode image
                image_data = self._encode_image(image_path)

                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_data}"
                    }
                })

            # Add text prompt
            content.append({
                "type": "text",
                "text": prompt
            })

            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": content
                }],
                max_tokens=1024
            )

            # Parse response
            response_text = response.choices[0].message.content
            return self._parse_json_response(response_text)

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def test_connection(self) -> tuple[bool, str]:
        """Test OpenAI API connection"""
        try:
            # Make a simple API call to test connection
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": "Hi"
                }],
                max_tokens=5
            )
            return True, "Connection successful"
        except openai.AuthenticationError:
            return False, "Invalid API key"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
