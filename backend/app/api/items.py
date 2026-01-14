from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import tempfile
import os
from ..database import get_db
from ..models.item import Item
from ..models.image import Image as ImageModel
from ..models.category import Category
from ..schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from ..schemas.image import ImageResponse, ImageAnalysisResponse, AIAnalysisResult
from ..schemas.document import DocumentResponse
from ..services.image_service import ImageService
from ..services.ai import ClaudeProvider, OpenAIProvider, OllamaProvider, GeminiProvider
from ..utils.prompts import get_analysis_prompt
from ..api.settings import get_setting_value

router = APIRouter(prefix="/api/items", tags=["items"])


def normalize_category_name(name: str) -> str:
    """Normalize category name for comparison"""
    return name.lower().strip().replace("&", "and").replace("-", " ")


def get_word_stem(word: str) -> str:
    """Simple stemming - remove common suffixes"""
    if len(word) > 4:
        if word.endswith('ics'):
            return word[:-1]  # electronics -> electronic
        if word.endswith('s') and not word.endswith('ss'):
            return word[:-1]  # tools -> tool
        if word.endswith('ing'):
            return word[:-3]  # dining -> din
        if word.endswith('ment'):
            return word[:-4]  # equipment -> equip
    return word


def find_similar_category(suggested: str, existing_categories: List[Category]) -> Optional[Category]:
    """
    Find a similar existing category for the AI suggestion.
    Returns the matching category if found, None if truly new.
    """
    suggested_normalized = normalize_category_name(suggested)
    suggested_words = set(suggested_normalized.split())
    suggested_stems = {get_word_stem(w) for w in suggested_words}

    best_match = None
    best_score = 0

    for category in existing_categories:
        cat_normalized = normalize_category_name(category.name)
        cat_words = set(cat_normalized.split())
        cat_stems = {get_word_stem(w) for w in cat_words}

        # Exact match (case-insensitive)
        if suggested_normalized == cat_normalized:
            return category

        # Check if one contains the other
        if suggested_normalized in cat_normalized or cat_normalized in suggested_normalized:
            return category

        # Check stem overlap (handles electronics/electronic, tools/tool, etc.)
        common_stems = suggested_stems & cat_stems
        if common_stems:
            # Score based on proportion of matching stems
            score = len(common_stems) / max(len(suggested_stems), len(cat_stems))
            if score > best_score:
                best_score = score
                best_match = category

        # Also check word overlap
        common_words = suggested_words & cat_words
        if common_words:
            score = len(common_words) / max(len(suggested_words), len(cat_words))
            if score > best_score:
                best_score = score
                best_match = category

    # Return match only if score is significant
    if best_score >= 0.4:  # 40% overlap threshold
        return best_match

    return None


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
    elif provider_name == "gemini":
        api_key = get_setting_value(db, "gemini_api_key")
        if not api_key:
            raise HTTPException(status_code=400, detail="Gemini API key not configured")
        model_name = get_setting_value(db, "gemini_model")
        if not model_name:
            raise HTTPException(status_code=400, detail="Gemini model not configured. Please select a model in Settings.")
        return GeminiProvider(api_key, model_name)
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

    # Fetch existing categories for the prompt
    existing_categories = db.query(Category).all()
    category_names = [cat.name for cat in existing_categories]

    temp_files = []
    try:
        # Save images to temp files
        for file in files:
            content = await file.read()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}")
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)

        # Get AI provider and analyze with categories in prompt
        provider = get_ai_provider(db)
        prompt = get_analysis_prompt(category_names)

        analysis_result = await provider.analyze_images(temp_files, prompt)

        # Run similarity check on the suggested category
        suggested_category = analysis_result.get("category", "")
        category_is_new = analysis_result.get("category_is_new", False)

        # Even if AI says it's not new, verify against our list
        # Also check if AI said it's new but we have a similar one
        similar_category = find_similar_category(suggested_category, existing_categories)

        if similar_category:
            # Found a match - use existing category name
            analysis_result["category"] = similar_category.name
            analysis_result["category_is_new"] = False
        else:
            # Truly new category
            analysis_result["category_is_new"] = True

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
    property_id: Optional[str] = None,
    category_id: Optional[str] = None,
    location_id: Optional[str] = None,
    condition: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all items with optional filters"""
    query = db.query(Item)

    # Apply filters
    if property_id:
        query = query.filter(Item.property_id == property_id)

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
        documents = [DocumentResponse.model_validate(doc) for doc in item.documents]
        # Create dict excluding SQLAlchemy internal fields and relationships
        item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
        item_dict.pop('images', None)
        item_dict.pop('documents', None)
        item_dict.pop('category', None)
        item_dict.pop('location', None)
        item_dict.pop('property', None)

        item_response = ItemResponse(
            **item_dict,
            images=images,
            documents=documents,
            property_name=item.property.name if item.property else None,
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

    documents = [DocumentResponse.model_validate(doc) for doc in db_item.documents]
    # Create dict excluding SQLAlchemy internal fields and relationships
    item_dict = {k: v for k, v in db_item.__dict__.items() if not k.startswith('_')}
    item_dict.pop('images', None)
    item_dict.pop('documents', None)
    item_dict.pop('category', None)
    item_dict.pop('location', None)
    item_dict.pop('property', None)

    return ItemResponse(
        **item_dict,
        images=[],
        documents=documents,
        property_name=db_item.property.name if db_item.property else None,
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
    documents = [DocumentResponse.model_validate(doc) for doc in item.documents]

    # Create dict excluding SQLAlchemy internal fields and relationships
    item_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
    item_dict.pop('images', None)
    item_dict.pop('documents', None)
    item_dict.pop('category', None)
    item_dict.pop('location', None)
    item_dict.pop('property', None)

    return ItemResponse(
        **item_dict,
        images=images,
        documents=documents,
        property_name=item.property.name if item.property else None,
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
    documents = [DocumentResponse.model_validate(doc) for doc in db_item.documents]

    # Create dict excluding SQLAlchemy internal fields and relationships
    item_dict = {k: v for k, v in db_item.__dict__.items() if not k.startswith('_')}
    item_dict.pop('images', None)
    item_dict.pop('documents', None)
    item_dict.pop('category', None)
    item_dict.pop('location', None)
    item_dict.pop('property', None)

    return ItemResponse(
        **item_dict,
        images=images,
        documents=documents,
        property_name=db_item.property.name if db_item.property else None,
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
