"""
Initialize default categories and locations for first-time setup.
This can be run optionally during the setup wizard.
"""

from sqlalchemy.orm import Session
from ..models.category import Category
from ..models.location import Location, LocationType


DEFAULT_CATEGORIES = [
    "Electronics",
    "Tools",
    "Furniture",
    "Kitchen",
    "Clothing",
    "Books",
    "Toys",
    "Sports",
    "Garden",
    "Automotive",
    "Office",
    "Other"
]


def init_default_categories(db: Session):
    """Initialize default categories if none exist"""
    existing_count = db.query(Category).count()
    if existing_count > 0:
        return False

    for cat_name in DEFAULT_CATEGORIES:
        category = Category(name=cat_name, parent_id=None)
        db.add(category)

    db.commit()
    return True


def init_default_locations(db: Session):
    """Initialize a basic location structure"""
    existing_count = db.query(Location).count()
    if existing_count > 0:
        return False

    # Create home
    home = Location(
        name="My Home",
        description="Main residence",
        location_type=LocationType.HOME,
        parent_id=None
    )
    db.add(home)
    db.commit()
    db.refresh(home)

    # Create floors
    floors = [
        Location(name="Ground Floor", location_type=LocationType.FLOOR, parent_id=home.id),
        Location(name="First Floor", location_type=LocationType.FLOOR, parent_id=home.id),
        Location(name="Basement", location_type=LocationType.FLOOR, parent_id=home.id),
    ]

    for floor in floors:
        db.add(floor)

    db.commit()

    # Refresh to get IDs
    for floor in floors:
        db.refresh(floor)

    # Create some common rooms on ground floor
    ground_floor = floors[0]
    rooms = [
        Location(name="Living Room", location_type=LocationType.ROOM, parent_id=ground_floor.id),
        Location(name="Kitchen", location_type=LocationType.ROOM, parent_id=ground_floor.id),
        Location(name="Bathroom", location_type=LocationType.ROOM, parent_id=ground_floor.id),
    ]

    for room in rooms:
        db.add(room)

    # Create garage at home level
    garage = Location(
        name="Garage",
        location_type=LocationType.ROOM,
        parent_id=home.id
    )
    db.add(garage)

    db.commit()
    return True
