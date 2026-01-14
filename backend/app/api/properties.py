from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.property import Property
from ..schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse, PropertyListResponse

router = APIRouter(prefix="/api/properties", tags=["properties"])


@router.get("", response_model=List[PropertyListResponse])
async def get_properties(db: Session = Depends(get_db)):
    """Get all properties with policy counts"""
    properties = db.query(Property).all()
    return [
        PropertyListResponse(
            id=p.id,
            name=p.name,
            address_city=p.address_city,
            address_country=p.address_country,
            property_type=p.property_type,
            policy_count=len(p.insurance_policies)
        )
        for p in properties
    ]


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: str, db: Session = Depends(get_db)):
    """Get a single property with its insurance policies"""
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property


@router.post("", response_model=PropertyResponse)
async def create_property(property: PropertyCreate, db: Session = Depends(get_db)):
    """Create a new property"""
    db_property = Property(**property.model_dump())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(property_id: str, property: PropertyUpdate, db: Session = Depends(get_db)):
    """Update a property"""
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")

    for field, value in property.model_dump(exclude_unset=True).items():
        setattr(db_property, field, value)

    db.commit()
    db.refresh(db_property)
    return db_property


@router.delete("/{property_id}")
async def delete_property(property_id: str, db: Session = Depends(get_db)):
    """Delete a property and its insurance policies"""
    db_property = db.query(Property).filter(Property.id == property_id).first()
    if not db_property:
        raise HTTPException(status_code=404, detail="Property not found")

    # Check if this is the last property - prevent deletion
    property_count = db.query(Property).count()
    if property_count <= 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the last property. At least one property must exist."
        )

    db.delete(db_property)
    db.commit()
    return {"message": "Property deleted successfully"}
