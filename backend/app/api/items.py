from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import tempfile
import os
from ..database import get_db
from ..models.item import Item
from ..models.image import Image as ImageModel
from ..schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from ..schemas.image import ImageResponse, ImageAnalysisResponse, AIAnalysisResult
from ..services.image_service import ImageService
from ..services.ai import ClaudeProvider, OpenAIProvider, OllamaProvider
from ..utils.prompts import get_analysis_prompt
from ..api.settings import get_setting_value

router = APIRouter(prefix="/api/items", tags=["items"])


def get_ai_provider(db: Session):
    """Get configured AI provider"""
    provider_name = get_setting_value(db, "ai_provider", "claude")

    if provider_name == "claude":
        api_key = get_setting_value(db, "claude_api_key")
        if not api_key:
            raise HTTPException(status_code=400, detail="Claude API key not configured")
        return ClaudeProvider(api_key)
    elif provider_name == "openai":
        api_key = get_setting_value(db, "openai_api_key")
        if not api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")
        return OpenAIProvider(api_key)
    elif provider_name == "ollama":
        endpoint = get_setting_value(db, "ollama_endpoint", "http://ollama:11434")
        return OllamaProvider(endpoint)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown AI provider: {provider_name}")


@router.post("/analyze-images", response_model=ImageAnalysisResponse)
async def analyze_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Analyze images with AI before creating an item"""
    if not files:
        raise HTTPException(status_code=400, detail="No images provided")

    temp_files = []
    try:
        # Save images to temp files
        for file in files:
            content = await file.read()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}")
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)

        # Get AI provider and analyze
        provider = get_ai_provider(db)
        prompt = get_analysis_prompt()

        analysis_result = await provider.analyze_images(temp_files, prompt)

        # Convert to response format
        ai_result = AIAnalysisResult(**analysis_result)

        return ImageAnalysisResponse(
            success=True,
            analysis=ai_result,
            image_count=len(files)
        )

    except Exception as e:
        return ImageAnalysisResponse(
            success=False,
            error=str(e),
            image_count=len(files)
        )
    finally:
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@router.get("", response_model=ItemListResponse)
async def get_items(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    location_id: Optional[str] = None,
    condition: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all items with optional filters"""
    query = db.query(Item)

    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Item.name.ilike(search_filter),
                Item.description.ilike(search_filter),
                Item.manufacturer.ilike(search_filter),
                Item.model_number.ilike(search_filter),
                Item.serial_number.ilike(search_filter)
            )
        )

    if category_id:
        query = query.filter(Item.category_id == category_id)

    if location_id:
        query = query.filter(Item.location_id == location_id)

    if condition:
        query = query.filter(Item.condition == condition)

    # Get total count
    total = query.count()

    # Get items
    items = query.offset(skip).limit(limit).all()

    # Convert to response
    item_responses = []
    for item in items:
        images = [ImageResponse.model_validate(img) for img in item.images]
        item_response = ItemResponse(
            **item.__dict__,
            images=images,
            documents=[],
            category_name=item.category.name if item.category else None,
            location_name=item.location.name if item.location else None
        )
        item_responses.append(item_response)

    return ItemListResponse(
        items=item_responses,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.post("", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return ItemResponse(
        **db_item.__dict__,
        images=[],
        documents=[],
        category_name=db_item.category.name if db_item.category else None,
        location_name=db_item.location.name if db_item.location else None
    )


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    images = [ImageResponse.model_validate(img) for img in item.images]

    return ItemResponse(
        **item.__dict__,
        images=images,
        documents=[],
        category_name=item.category.name if item.category else None,
        location_name=item.location.name if item.location else None
    )


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)

    images = [ImageResponse.model_validate(img) for img in db_item.images]

    return ItemResponse(
        **db_item.__dict__,
        images=images,
        documents=[],
        category_name=db_item.category.name if db_item.category else None,
        location_name=db_item.location.name if db_item.location else None
    )


@router.delete("/{item_id}")
async def delete_item(item_id: str, db: Session = Depends(get_db)):
    """Delete an item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Images and documents will be cascade deleted
    db.delete(db_item)
    db.commit()

    return {"message": "Item deleted successfully"}


@router.post("/{item_id}/images", response_model=ImageResponse)
async def add_item_image(
    item_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Add an image to an existing item"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Read file content
    content = await file.read()

    # Save image
    image_service = ImageService()
    filename, thumbnail_filename, file_size, width, height = await image_service.save_image(
        content, file.filename
    )

    # Create image record
    is_primary = len(item.images) == 0  # First image is primary
    db_image = ImageModel(
        item_id=item_id,
        filename=filename,
        original_filename=file.filename,
        file_size=file_size,
        mime_type=file.content_type or "image/jpeg",
        width=width,
        height=height,
        is_primary=is_primary
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return ImageResponse.model_validate(db_image)
