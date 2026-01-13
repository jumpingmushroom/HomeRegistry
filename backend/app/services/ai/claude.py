from typing import List, Dict, Any
import anthropic
from .base import AIProvider


class ClaudeProvider(AIProvider):
    """Anthropic Claude AI Provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)

    async def analyze_images(self, image_paths: List[str], prompt: str) -> Dict[str, Any]:
        """Analyze images using Claude Vision"""
        try:
            # Prepare image content
            content = []

            for image_path in image_paths:
                # Determine media type from file extension
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
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data,
                    },
                })

            # Add text prompt
            content.append({
                "type": "text",
                "text": prompt
            })

            # Make API call
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )

            # Parse response
            response_text = message.content[0].text
            return self._parse_json_response(response_text)

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    async def test_connection(self) -> tuple[bool, str]:
        """Test Claude API connection"""
        try:
            # Make a simple API call to test connection
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{
                    "role": "user",
                    "content": "Hi"
                }]
            )
            return True, "Connection successful"
        except anthropic.AuthenticationError:
            return False, "Invalid API key"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
