from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.document import Document, DocumentType
from ..models.user import User
from ..services.auth_service import get_current_user
from ..schemas.document import DocumentResponse
from ..services.storage_service import StorageService

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/items/{item_id}/documents", response_model=DocumentResponse)
async def upload_document(
    item_id: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for an item"""
    from ..models.item import Item

    # Check item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Validate document type
    try:
        doc_type = DocumentType(document_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")

    # Read file content
    content = await file.read()

    # Save document
    storage_service = StorageService()
    filename, file_size = await storage_service.save_document(content, file.filename)

    # Create document record
    db_document = Document(
        item_id=item_id,
        filename=filename,
        original_filename=file.filename,
        document_type=doc_type,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return DocumentResponse.model_validate(db_document)


@router.get("/documents/{document_id}", response_class=FileResponse)
async def download_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Download a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    storage_service = StorageService()
    filepath = storage_service.get_document_path(document.filename)

    return FileResponse(
        filepath,
        filename=document.original_filename,
        media_type=document.mime_type
    )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    storage_service = StorageService()
    await storage_service.delete_document(document.filename)

    # Delete database record
    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}
