from typing import List, Dict, Any
import httpx
from .base import AIProvider


class OllamaProvider(AIProvider):
    """Ollama Local AI Provider"""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")

    async def analyze_images(self, image_paths: List[str], prompt: str) -> Dict[str, Any]:
        """Analyze images using Ollama (llava model)"""
        try:
            # Prepare images (Ollama expects base64 encoded images)
            images = [self._encode_image(path) for path in image_paths]

            # Make API call to Ollama
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": "llava",
                        "prompt": prompt,
                        "images": images,
                        "stream": False
                    }
                )
                response.raise_for_status()

                result = response.json()
                response_text = result.get("response", "")

                return self._parse_json_response(response_text)

        except httpx.HTTPError as e:
            raise Exception(f"Ollama API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")

    async def test_connection(self) -> tuple[bool, str]:
        """Test Ollama connection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Check if Ollama is running
                response = await client.get(f"{self.endpoint}/api/tags")
                response.raise_for_status()

                # Check if llava model is available
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]

                if any("llava" in name.lower() for name in model_names):
                    return True, "Connection successful (llava model available)"
                else:
                    return False, "Connection successful but llava model not found. Please run: ollama pull llava"

        except httpx.HTTPError:
            return False, "Cannot connect to Ollama. Make sure Ollama is running."
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
