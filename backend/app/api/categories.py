from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTree

router = APIRouter(prefix="/api/categories", tags=["categories"])


def build_category_tree(categories: List[Category], parent_id: str = None) -> List[CategoryTree]:
    """Build hierarchical category tree"""
    tree = []
    for category in categories:
        if category.parent_id == parent_id:
            children = build_category_tree(categories, category.id)
            item_count = len(category.items)
            tree.append(CategoryTree(
                id=category.id,
                name=category.name,
                parent_id=category.parent_id,
                created_at=category.created_at,
                item_count=item_count,
                children=children
            ))
    return tree


@router.get("", response_model=List[CategoryTree])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories as a tree"""
    categories = db.query(Category).all()
    return build_category_tree(categories)


@router.post("", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    # Validate parent exists if provided
    if category.parent_id:
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")

    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return CategoryResponse(
        id=db_category.id,
        name=db_category.name,
        parent_id=db_category.parent_id,
        created_at=db_category.created_at,
        item_count=0
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category: CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Update fields
    for field, value in category.model_dump(exclude_unset=True).items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)

    return CategoryResponse(
        id=db_category.id,
        name=db_category.name,
        parent_id=db_category.parent_id,
        created_at=db_category.created_at,
        item_count=len(db_category.items)
    )


@router.delete("/{category_id}")
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    """Delete a category (only if no items)"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    if db_category.items:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {len(db_category.items)} items"
        )

    db.delete(db_category)
    db.commit()

    return {"message": "Category deleted successfully"}
