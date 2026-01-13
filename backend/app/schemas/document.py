from pydantic import BaseModel
from datetime import datetime
from ..models.document import DocumentType


class DocumentUpload(BaseModel):
    document_type: DocumentType


class DocumentResponse(BaseModel):
    id: str
    item_id: str
    filename: str
    original_filename: str
    document_type: DocumentType
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True
