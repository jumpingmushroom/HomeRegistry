from PIL import Image
import os
import uuid
from typing import Tuple
import io
import asyncio
import functools
from ..config import settings


class ImageService:
    """Service for handling image upload, optimization, and storage"""

    def __init__(self):
        self.images_path = settings.images_path
        self.thumbnails_path = os.path.join(settings.images_path, "thumbnails")

    async def save_image(self, file_content: bytes, original_filename: str) -> Tuple[str, str, int, int, int]:
        """
        Save image and create thumbnail using run_in_executor to avoid blocking
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._process_and_save, 
            file_content, 
            original_filename
        )

    def _process_and_save(self, file_content: bytes, original_filename: str) -> Tuple[str, str, int, int, int]:
        """Synchronous part of image processing"""
        # Generate unique filename - prefer webp for efficiency
        filename = f"{uuid.uuid4()}.webp"
        filepath = os.path.join(self.images_path, filename)

        # Open image
        image = Image.open(io.BytesIO(file_content))

        # Get original dimensions
        width, height = image.size

        # Optimize and resize main image if too large
        max_width = 1920
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            width, height = image.size

        # Convert RGBA to RGB if needed (WebP supports alpha, but we might want to flatten)
        if image.mode == "RGBA":
            # If we want to keep alpha, we can. But usually for photos it's not needed.
            # Let's keep it for WebP, but flatten for specific use cases if needed.
            pass

        # Save as WebP for best compression/quality ratio
        image.save(filepath, "WEBP", quality=80, method=6) # method 6 is slowest but best compression

        # Get file size
        file_size = os.path.getsize(filepath)

        # Create thumbnail
        thumbnail_filename = self._sync_create_thumbnail(image, filename)

        return filename, thumbnail_filename, file_size, width, height

    def _sync_create_thumbnail(self, image: Image.Image, filename: str) -> str:
        """Create thumbnail from image (synchronous)"""
        # Create thumbnail (300x300)
        thumbnail = image.copy()
        thumbnail.thumbnail((300, 300), Image.Resampling.LANCZOS)

        # Save as WebP for better compression
        thumbnail_filename = f"{filename.rsplit('.', 1)[0]}_thumb.webp"
        thumbnail_path = os.path.join(self.thumbnails_path, thumbnail_filename)

        thumbnail.save(thumbnail_path, "WEBP", quality=75)

        return thumbnail_filename

    async def _create_thumbnail(self, image: Image.Image, filename: str) -> str:
        # This is now handled by _sync_create_thumbnail, but keeping for compatibility if needed
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_create_thumbnail, image, filename)

    async def delete_image(self, filename: str, thumbnail_filename: str = None):
        """Delete image and thumbnail"""
        # Delete main image
        filepath = os.path.join(self.images_path, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete thumbnail
        if thumbnail_filename:
            thumbnail_path = os.path.join(self.thumbnails_path, thumbnail_filename)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

    def get_image_path(self, filename: str) -> str:
        """Get full path to image"""
        return os.path.join(self.images_path, filename)

    def get_thumbnail_path(self, thumbnail_filename: str) -> str:
        """Get full path to thumbnail"""
        return os.path.join(self.thumbnails_path, thumbnail_filename)
