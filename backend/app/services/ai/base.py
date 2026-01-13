from abc import ABC, abstractmethod
from typing import List, Dict, Any
import base64
import json


class AIProvider(ABC):
    """Base class for AI providers"""

    @abstractmethod
    async def analyze_images(self, image_paths: List[str], prompt: str) -> Dict[str, Any]:
        """
        Analyze images and return structured data

        Args:
            image_paths: List of paths to image files
            prompt: The prompt to send to the AI

        Returns:
            Dict with analysis results
        """
        pass

    @abstractmethod
    async def test_connection(self) -> tuple[bool, str]:
        """
        Test the AI provider connection

        Returns:
            Tuple of (success: bool, message: str)
        """
        pass

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling markdown code blocks"""
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Try to find JSON object in the response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(response[start:end])
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Failed to parse JSON response: {e}")
