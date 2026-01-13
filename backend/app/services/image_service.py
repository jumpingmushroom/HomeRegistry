from PIL import Image
import os
import uuid
from typing import Tuple
import io
from ..config import settings


class ImageService:
    """Service for handling image upload, optimization, and storage"""

    def __init__(self):
        self.images_path = settings.images_path
        self.thumbnails_path = os.path.join(settings.images_path, "thumbnails")

    async def save_image(self, file_content: bytes, original_filename: str) -> Tuple[str, str, int, int, int]:
        """
        Save image and create thumbnail

        Args:
            file_content: Image file content in bytes
            original_filename: Original filename

        Returns:
            Tuple of (filename, thumbnail_filename, file_size, width, height)
        """
        # Generate unique filename
        ext = original_filename.split(".")[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
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

        # Convert RGBA to RGB if needed (for JPEG)
        if image.mode == "RGBA" and ext in ["jpg", "jpeg"]:
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            image = rgb_image

        # Save optimized image
        if ext in ["jpg", "jpeg"]:
            image.save(filepath, "JPEG", quality=85, optimize=True)
        elif ext == "png":
            image.save(filepath, "PNG", optimize=True)
        elif ext == "webp":
            image.save(filepath, "WEBP", quality=85)
        else:
            image.save(filepath)

        # Get file size
        file_size = os.path.getsize(filepath)

        # Create thumbnail
        thumbnail_filename = await self._create_thumbnail(image, filename)

        return filename, thumbnail_filename, file_size, width, height

    async def _create_thumbnail(self, image: Image.Image, filename: str) -> str:
        """Create thumbnail from image"""
        # Create thumbnail (300x300)
        thumbnail = image.copy()
        thumbnail.thumbnail((300, 300), Image.Resampling.LANCZOS)

        # Save as WebP for better compression
        thumbnail_filename = f"{filename.rsplit('.', 1)[0]}.webp"
        thumbnail_path = os.path.join(self.thumbnails_path, thumbnail_filename)

        # Convert RGBA to RGB if needed
        if thumbnail.mode == "RGBA":
            rgb_thumbnail = Image.new("RGB", thumbnail.size, (255, 255, 255))
            rgb_thumbnail.paste(thumbnail, mask=thumbnail.split()[3])
            thumbnail = rgb_thumbnail

        thumbnail.save(thumbnail_path, "WEBP", quality=80)

        return thumbnail_filename

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
