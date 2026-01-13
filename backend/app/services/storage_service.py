import os
import uuid
import aiofiles
from ..config import settings


class StorageService:
    """Service for handling document storage"""

    def __init__(self):
        self.documents_path = settings.documents_path

    async def save_document(self, file_content: bytes, original_filename: str) -> tuple[str, int]:
        """
        Save document file

        Args:
            file_content: File content in bytes
            original_filename: Original filename

        Returns:
            Tuple of (filename, file_size)
        """
        # Generate unique filename
        ext = original_filename.split(".")[-1].lower() if "." in original_filename else "bin"
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(self.documents_path, filename)

        # Save file
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(file_content)

        file_size = len(file_content)

        return filename, file_size

    async def delete_document(self, filename: str):
        """Delete document file"""
        filepath = os.path.join(self.documents_path, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    def get_document_path(self, filename: str) -> str:
        """Get full path to document"""
        return os.path.join(self.documents_path, filename)
