from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import time

# SQLite URL format
SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.database_url}"

# Create engine with proper SQLite settings for production use
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  # 30 second timeout for locked database
    },
    pool_pre_ping=True,
    echo=False,
)


# Enable WAL mode for better concurrent access
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Run database migrations for schema changes"""
    from sqlalchemy import inspect, text
    import uuid

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # Check if items table exists
    if 'items' in table_names:
        columns = [col['name'] for col in inspector.get_columns('items')]

        # Add missing columns
        migrations = []
        if 'purchase_location' not in columns:
            migrations.append("ALTER TABLE items ADD COLUMN purchase_location VARCHAR(255)")
        if 'barcode' not in columns:
            migrations.append("ALTER TABLE items ADD COLUMN barcode VARCHAR(255)")
        if 'tags' not in columns:
            migrations.append("ALTER TABLE items ADD COLUMN tags JSON")
        if 'property_id' not in columns:
            migrations.append("ALTER TABLE items ADD COLUMN property_id VARCHAR(36) REFERENCES properties(id)")

        # Execute migrations
        if migrations:
            with engine.connect() as conn:
                for migration in migrations:
                    print(f"Running migration: {migration}")
                    conn.execute(text(migration))
                    conn.commit()

    # Check if locations table exists and add property_id
    if 'locations' in table_names:
        columns = [col['name'] for col in inspector.get_columns('locations')]
        if 'property_id' not in columns:
            with engine.connect() as conn:
                print("Running migration: ALTER TABLE locations ADD COLUMN property_id")
                conn.execute(text("ALTER TABLE locations ADD COLUMN property_id VARCHAR(36) REFERENCES properties(id)"))
                conn.commit()

    # Create default property if properties table exists but is empty
    default_property_id = None
    if 'properties' in table_names:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM properties"))
            count = result.scalar()

            if count == 0:
                # Create default property
                default_property_id = str(uuid.uuid4())
                conn.execute(text("""
                    INSERT INTO properties (
                        id, name, address_street, address_city, address_state,
                        address_postal_code, address_country, primary_contact_name,
                        property_type
                    ) VALUES (
                        :id, 'My Home', 'Address not set', 'City not set', 'State not set',
                        '00000', 'Country not set', 'Owner not set', 'HOUSE'
                    )
                """), {"id": default_property_id})
                conn.commit()
                print(f"Created default property with ID: {default_property_id}")
            else:
                # Get the first property ID for migration
                result = conn.execute(text("SELECT id FROM properties LIMIT 1"))
                row = result.fetchone()
                if row:
                    default_property_id = row[0]

    # Assign existing items and locations to the default property
    if default_property_id:
        with engine.connect() as conn:
            # Update items without property_id
            result = conn.execute(text("UPDATE items SET property_id = :prop_id WHERE property_id IS NULL"), {"prop_id": default_property_id})
            if result.rowcount > 0:
                print(f"Assigned {result.rowcount} items to default property")
            conn.commit()

            # Update locations without property_id
            result = conn.execute(text("UPDATE locations SET property_id = :prop_id WHERE property_id IS NULL"), {"prop_id": default_property_id})
            if result.rowcount > 0:
                print(f"Assigned {result.rowcount} locations to default property")
            conn.commit()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    run_migrations()
