from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.location import Location
from ..schemas.location import LocationCreate, LocationUpdate, LocationResponse, LocationTree

router = APIRouter(prefix="/api/locations", tags=["locations"])


def build_location_tree(locations: List[Location], parent_id: str = None) -> List[LocationTree]:
    """Build hierarchical location tree"""
    tree = []
    for location in locations:
        if location.parent_id == parent_id:
            children = build_location_tree(locations, location.id)
            item_count = len(location.items)
            tree.append(LocationTree(
                id=location.id,
                name=location.name,
                description=location.description,
                property_id=location.property_id,
                location_type=location.location_type,
                parent_id=location.parent_id,
                created_at=location.created_at,
                updated_at=location.updated_at,
                item_count=item_count,
                property_name=location.property.name if location.property else None,
                children=children
            ))
    return tree


@router.get("", response_model=List[LocationTree])
async def get_locations(
    property_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all locations as a tree, optionally filtered by property"""
    query = db.query(Location)
    if property_id:
        query = query.filter(Location.property_id == property_id)
    locations = query.all()
    return build_location_tree(locations)


@router.post("", response_model=LocationResponse)
async def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Create a new location"""
    # Validate parent exists if provided
    if location.parent_id:
        parent = db.query(Location).filter(Location.id == location.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent location not found")

    db_location = Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)

    return LocationResponse(
        id=db_location.id,
        name=db_location.name,
        description=db_location.description,
        property_id=db_location.property_id,
        location_type=db_location.location_type,
        parent_id=db_location.parent_id,
        created_at=db_location.created_at,
        updated_at=db_location.updated_at,
        item_count=0,
        property_name=db_location.property.name if db_location.property else None
    )


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(location_id: str, location: LocationUpdate, db: Session = Depends(get_db)):
    """Update a location"""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Update fields
    for field, value in location.model_dump(exclude_unset=True).items():
        setattr(db_location, field, value)

    db.commit()
    db.refresh(db_location)

    return LocationResponse(
        id=db_location.id,
        name=db_location.name,
        description=db_location.description,
        property_id=db_location.property_id,
        location_type=db_location.location_type,
        parent_id=db_location.parent_id,
        created_at=db_location.created_at,
        updated_at=db_location.updated_at,
        item_count=len(db_location.items),
        property_name=db_location.property.name if db_location.property else None
    )


@router.delete("/{location_id}")
async def delete_location(location_id: str, db: Session = Depends(get_db)):
    """Delete a location (only if no items)"""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")

    if db_location.items:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete location with {len(db_location.items)} items"
        )

    db.delete(db_location)
    db.commit()

    return {"message": "Location deleted successfully"}
