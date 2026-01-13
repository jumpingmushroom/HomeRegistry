from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..utils.init_data import init_default_categories, init_default_locations

router = APIRouter(prefix="/api/init", tags=["initialization"])


@router.post("/default-data")
async def initialize_default_data(db: Session = Depends(get_db)):
    """Initialize default categories and locations"""
    categories_added = init_default_categories(db)
    locations_added = init_default_locations(db)

    return {
        "success": True,
        "categories_added": categories_added,
        "locations_added": locations_added,
        "message": "Default data initialized" if (categories_added or locations_added) else "Data already exists"
    }
