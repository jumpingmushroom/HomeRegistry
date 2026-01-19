"""
Service for restoring data from a ZIP archive export.
"""
import json
import os
import shutil
import tempfile
import zipfile
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple

from sqlalchemy.orm import Session

from ..config import settings
from ..models.item import Item
from ..models.category import Category
from ..models.location import Location
from ..models.property import Property
from ..models.insurance_policy import InsurancePolicy
from ..models.image import Image
from ..models.document import Document

logger = logging.getLogger(__name__)


class RestoreService:
    """Service for restoring data from ZIP archive export."""

    def _parse_datetime(self, value: str) -> datetime:
        """Parse ISO datetime string to datetime object."""
        if not value:
            return None
        # Handle various ISO formats
        value = value.rstrip('Z')
        for fmt in [
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d'
        ]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    def _parse_date(self, value: str) -> str:
        """Parse date string, return as-is if valid."""
        if not value:
            return None
        return value.split('T')[0] if 'T' in value else value

    def _clear_all_data(self, db: Session) -> Dict[str, int]:
        """Clear all data from the database. Returns counts of deleted records."""
        counts = {}

        # Delete in order to respect foreign keys
        counts['images'] = db.query(Image).delete()
        counts['documents'] = db.query(Document).delete()
        counts['items'] = db.query(Item).delete()
        counts['insurance_policies'] = db.query(InsurancePolicy).delete()
        counts['locations'] = db.query(Location).delete()
        counts['categories'] = db.query(Category).delete()
        counts['properties'] = db.query(Property).delete()

        db.commit()

        # Clear image files
        if os.path.exists(settings.images_path):
            for f in os.listdir(settings.images_path):
                file_path = os.path.join(settings.images_path, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Clear thumbnail files
        thumbnails_path = os.path.join(settings.images_path, 'thumbnails')
        if os.path.exists(thumbnails_path):
            for f in os.listdir(thumbnails_path):
                file_path = os.path.join(thumbnails_path, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # Clear document files
        if os.path.exists(settings.documents_path):
            for f in os.listdir(settings.documents_path):
                file_path = os.path.join(settings.documents_path, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        logger.info(f"Cleared all data: {counts}")
        return counts

    def _record_exists(self, db: Session, model, record_id: str) -> bool:
        """Check if a record with given ID exists."""
        return db.query(model).filter(model.id == record_id).first() is not None

    def restore_from_zip(
        self,
        db: Session,
        zip_path: str,
        mode: str = "merge"
    ) -> Dict[str, Any]:
        """
        Restore data from a ZIP archive.

        Args:
            db: Database session
            zip_path: Path to the ZIP file
            mode: "merge" (add new, skip existing) or "replace" (clear all, then restore)

        Returns:
            Summary dict with counts of imported/skipped records
        """
        logger.info(f"Starting restore from {zip_path} in {mode} mode")

        result = {
            "mode": mode,
            "imported": {},
            "skipped": {},
            "errors": [],
            "files_restored": {"images": 0, "documents": 0}
        }

        # Extract ZIP to temp directory
        temp_dir = tempfile.mkdtemp(prefix="homeregistry_restore_")

        try:
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)

            # Load data.json
            json_path = os.path.join(temp_dir, "data.json")
            if not os.path.exists(json_path):
                raise ValueError("Invalid backup: data.json not found")

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clear data if replace mode
            if mode == "replace":
                cleared = self._clear_all_data(db)
                result["cleared"] = cleared

            # Import in order: properties -> categories -> locations -> items -> images -> documents -> insurance_policies

            # 1. Properties
            imported, skipped = self._import_properties(db, data.get("properties", []), mode)
            result["imported"]["properties"] = imported
            result["skipped"]["properties"] = skipped

            # 2. Categories (handle hierarchy)
            imported, skipped = self._import_categories(db, data.get("categories", []), mode)
            result["imported"]["categories"] = imported
            result["skipped"]["categories"] = skipped

            # 3. Locations (handle hierarchy)
            imported, skipped = self._import_locations(db, data.get("locations", []), mode)
            result["imported"]["locations"] = imported
            result["skipped"]["locations"] = skipped

            # 4. Items
            imported, skipped = self._import_items(db, data.get("items", []), mode)
            result["imported"]["items"] = imported
            result["skipped"]["items"] = skipped

            # 5. Images (metadata + files)
            imported, skipped, files_count = self._import_images(
                db, data.get("images", []), temp_dir, mode
            )
            result["imported"]["images"] = imported
            result["skipped"]["images"] = skipped
            result["files_restored"]["images"] = files_count

            # 6. Documents (metadata + files)
            imported, skipped, files_count = self._import_documents(
                db, data.get("documents", []), temp_dir, mode
            )
            result["imported"]["documents"] = imported
            result["skipped"]["documents"] = skipped
            result["files_restored"]["documents"] = files_count

            # 7. Insurance policies
            imported, skipped = self._import_insurance_policies(
                db, data.get("insurance_policies", []), mode
            )
            result["imported"]["insurance_policies"] = imported
            result["skipped"]["insurance_policies"] = skipped

            db.commit()
            logger.info(f"Restore completed: {result}")

        except Exception as e:
            db.rollback()
            logger.error(f"Restore failed: {e}")
            result["errors"].append(str(e))
            raise
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

        return result

    def _import_properties(
        self, db: Session, properties: List[Dict], mode: str
    ) -> Tuple[int, int]:
        """Import properties. Returns (imported_count, skipped_count)."""
        imported = 0
        skipped = 0

        for prop_data in properties:
            prop_id = prop_data.get("id")

            if mode == "merge" and self._record_exists(db, Property, prop_id):
                skipped += 1
                continue

            prop = Property(
                id=prop_id,
                name=prop_data.get("name"),
                address=prop_data.get("address"),
                property_type=prop_data.get("property_type"),
                notes=prop_data.get("notes"),
                created_at=self._parse_datetime(prop_data.get("created_at")) or datetime.utcnow()
            )
            db.add(prop)
            imported += 1

        db.flush()
        return imported, skipped

    def _import_categories(
        self, db: Session, categories: List[Dict], mode: str
    ) -> Tuple[int, int]:
        """Import categories, handling parent-child relationships."""
        imported = 0
        skipped = 0

        # First pass: import categories without parent_id
        for cat_data in categories:
            cat_id = cat_data.get("id")

            if mode == "merge" and self._record_exists(db, Category, cat_id):
                skipped += 1
                continue

            cat = Category(
                id=cat_id,
                name=cat_data.get("name"),
                description=cat_data.get("description"),
                icon=cat_data.get("icon"),
                parent_id=None,  # Set later
                created_at=self._parse_datetime(cat_data.get("created_at")) or datetime.utcnow()
            )
            db.add(cat)
            imported += 1

        db.flush()

        # Second pass: update parent_id relationships
        for cat_data in categories:
            parent_id = cat_data.get("parent_id")
            if parent_id:
                cat = db.query(Category).filter(Category.id == cat_data.get("id")).first()
                if cat:
                    cat.parent_id = parent_id

        db.flush()
        return imported, skipped

    def _import_locations(
        self, db: Session, locations: List[Dict], mode: str
    ) -> Tuple[int, int]:
        """Import locations, handling parent-child relationships."""
        imported = 0
        skipped = 0

        # First pass: import locations without parent_id
        for loc_data in locations:
            loc_id = loc_data.get("id")

            if mode == "merge" and self._record_exists(db, Location, loc_id):
                skipped += 1
                continue

            loc = Location(
                id=loc_id,
                name=loc_data.get("name"),
                description=loc_data.get("description"),
                property_id=loc_data.get("property_id"),
                parent_id=None,  # Set later
                created_at=self._parse_datetime(loc_data.get("created_at")) or datetime.utcnow()
            )
            db.add(loc)
            imported += 1

        db.flush()

        # Second pass: update parent_id relationships
        for loc_data in locations:
            parent_id = loc_data.get("parent_id")
            if parent_id:
                loc = db.query(Location).filter(Location.id == loc_data.get("id")).first()
                if loc:
                    loc.parent_id = parent_id

        db.flush()
        return imported, skipped

    def _import_items(
        self, db: Session, items: List[Dict], mode: str
    ) -> Tuple[int, int]:
        """Import items."""
        imported = 0
        skipped = 0

        for item_data in items:
            item_id = item_data.get("id")

            if mode == "merge" and self._record_exists(db, Item, item_id):
                skipped += 1
                continue

            item = Item(
                id=item_id,
                name=item_data.get("name"),
                description=item_data.get("description"),
                property_id=item_data.get("property_id"),
                category_id=item_data.get("category_id"),
                location_id=item_data.get("location_id"),
                manufacturer=item_data.get("manufacturer"),
                model_number=item_data.get("model_number"),
                serial_number=item_data.get("serial_number"),
                barcode=item_data.get("barcode"),
                purchase_date=self._parse_date(item_data.get("purchase_date")),
                purchase_price=item_data.get("purchase_price"),
                purchase_location=item_data.get("purchase_location"),
                current_value=item_data.get("current_value"),
                currency=item_data.get("currency", "NOK"),
                condition=item_data.get("condition"),
                quantity=item_data.get("quantity", 1),
                warranty_expiration=self._parse_date(item_data.get("warranty_expiration")),
                notes=item_data.get("notes"),
                tags=item_data.get("tags"),
                custom_fields=item_data.get("custom_fields"),
                created_at=self._parse_datetime(item_data.get("created_at")) or datetime.utcnow(),
                updated_at=self._parse_datetime(item_data.get("updated_at"))
            )
            db.add(item)
            imported += 1

        db.flush()
        return imported, skipped

    def _import_images(
        self, db: Session, images: List[Dict], temp_dir: str, mode: str
    ) -> Tuple[int, int, int]:
        """Import image metadata and copy files. Returns (imported, skipped, files_copied)."""
        imported = 0
        skipped = 0
        files_copied = 0

        for img_data in images:
            img_id = img_data.get("id")

            if mode == "merge" and self._record_exists(db, Image, img_id):
                skipped += 1
                continue

            # Create new filename for the image
            original_filename = img_data.get("original_filename", "image.jpg")
            ext = os.path.splitext(original_filename)[1] or ".jpg"
            new_filename = f"{uuid.uuid4()}{ext}"

            img = Image(
                id=img_id,
                item_id=img_data.get("item_id"),
                filename=new_filename,
                original_filename=original_filename,
                file_size=img_data.get("file_size"),
                mime_type=img_data.get("mime_type"),
                width=img_data.get("width"),
                height=img_data.get("height"),
                is_primary=img_data.get("is_primary", False),
                ai_analysis=img_data.get("ai_analysis"),
                created_at=self._parse_datetime(img_data.get("created_at")) or datetime.utcnow()
            )
            db.add(img)
            imported += 1

            # Copy image file
            item_id = img_data.get("item_id")
            old_original_filename = img_data.get("original_filename")

            if item_id and old_original_filename:
                # Look for the file in the export
                src_path = os.path.join(temp_dir, "images", item_id, old_original_filename)

                if os.path.exists(src_path):
                    dst_path = os.path.join(settings.images_path, new_filename)
                    shutil.copy2(src_path, dst_path)
                    files_copied += 1

                    # Try to create thumbnail
                    try:
                        from .image_service import ImageService
                        image_service = ImageService()
                        image_service.create_thumbnail(new_filename)
                    except Exception as e:
                        logger.warning(f"Failed to create thumbnail for {new_filename}: {e}")

        db.flush()
        return imported, skipped, files_copied

    def _import_documents(
        self, db: Session, documents: List[Dict], temp_dir: str, mode: str
    ) -> Tuple[int, int, int]:
        """Import document metadata and copy files. Returns (imported, skipped, files_copied)."""
        imported = 0
        skipped = 0
        files_copied = 0

        for doc_data in documents:
            doc_id = doc_data.get("id")

            if mode == "merge" and self._record_exists(db, Document, doc_id):
                skipped += 1
                continue

            # Create new filename for the document
            original_filename = doc_data.get("original_filename", "document.pdf")
            ext = os.path.splitext(original_filename)[1] or ".pdf"
            new_filename = f"{uuid.uuid4()}{ext}"

            doc = Document(
                id=doc_id,
                item_id=doc_data.get("item_id"),
                filename=new_filename,
                original_filename=original_filename,
                file_size=doc_data.get("file_size"),
                mime_type=doc_data.get("mime_type"),
                document_type=doc_data.get("document_type", "other"),
                created_at=self._parse_datetime(doc_data.get("created_at")) or datetime.utcnow()
            )
            db.add(doc)
            imported += 1

            # Copy document file
            item_id = doc_data.get("item_id")
            old_original_filename = doc_data.get("original_filename")

            if item_id and old_original_filename:
                # Look for the file in the export
                src_path = os.path.join(temp_dir, "documents", item_id, old_original_filename)

                if os.path.exists(src_path):
                    dst_path = os.path.join(settings.documents_path, new_filename)
                    shutil.copy2(src_path, dst_path)
                    files_copied += 1

        db.flush()
        return imported, skipped, files_copied

    def _import_insurance_policies(
        self, db: Session, policies: List[Dict], mode: str
    ) -> Tuple[int, int]:
        """Import insurance policies."""
        imported = 0
        skipped = 0

        for policy_data in policies:
            policy_id = policy_data.get("id")

            if mode == "merge" and self._record_exists(db, InsurancePolicy, policy_id):
                skipped += 1
                continue

            policy = InsurancePolicy(
                id=policy_id,
                property_id=policy_data.get("property_id"),
                provider=policy_data.get("provider"),
                policy_number=policy_data.get("policy_number"),
                policy_type=policy_data.get("policy_type"),
                coverage_amount=policy_data.get("coverage_amount"),
                deductible=policy_data.get("deductible"),
                premium=policy_data.get("premium"),
                premium_frequency=policy_data.get("premium_frequency"),
                start_date=self._parse_date(policy_data.get("start_date")),
                end_date=self._parse_date(policy_data.get("end_date")),
                notes=policy_data.get("notes"),
                created_at=self._parse_datetime(policy_data.get("created_at")) or datetime.utcnow()
            )
            db.add(policy)
            imported += 1

        db.flush()
        return imported, skipped


# Singleton instance
restore_service = RestoreService()
