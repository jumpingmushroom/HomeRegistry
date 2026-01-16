"""
Service for exporting all data to a ZIP archive.
"""
import json
import csv
import io
import os
import shutil
import tempfile
import zipfile
import logging
from datetime import datetime
from typing import Dict, Any, List

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


class ExportService:
    """Service for exporting all data to ZIP archive."""

    def _serialize_model(self, obj) -> Dict[str, Any]:
        """Convert a SQLAlchemy model to a dictionary."""
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            # Handle datetime and date objects
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            # Handle Decimal
            elif hasattr(value, '__float__'):
                value = float(value)
            result[column.name] = value
        return result

    def _get_all_data(self, db: Session) -> Dict[str, Any]:
        """Query all data from the database."""
        # Get all records
        properties = db.query(Property).all()
        categories = db.query(Category).all()
        locations = db.query(Location).all()
        items = db.query(Item).all()
        insurance_policies = db.query(InsurancePolicy).all()
        images = db.query(Image).all()
        documents = db.query(Document).all()

        # Build lookup maps for names
        property_map = {p.id: p.name for p in properties}
        category_map = {c.id: c.name for c in categories}
        location_map = {l.id: l.name for l in locations}

        # Serialize all data
        return {
            "export_date": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "properties": [self._serialize_model(p) for p in properties],
            "categories": [self._serialize_model(c) for c in categories],
            "locations": [self._serialize_model(l) for l in locations],
            "items": [self._serialize_model(i) for i in items],
            "insurance_policies": [self._serialize_model(p) for p in insurance_policies],
            "images": [self._serialize_model(img) for img in images],
            "documents": [self._serialize_model(doc) for doc in documents],
            "_lookups": {
                "properties": property_map,
                "categories": category_map,
                "locations": location_map,
            }
        }

    def _generate_items_csv(self, data: Dict[str, Any]) -> str:
        """Generate CSV content for items."""
        output = io.StringIO()

        fieldnames = [
            'id', 'name', 'description', 'property_name', 'category_name',
            'location_name', 'manufacturer', 'model_number', 'serial_number',
            'condition', 'quantity', 'purchase_date', 'purchase_price',
            'current_value', 'currency', 'warranty_expiration', 'barcode',
            'tags', 'notes', 'created_at'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        lookups = data.get("_lookups", {})
        property_map = lookups.get("properties", {})
        category_map = lookups.get("categories", {})
        location_map = lookups.get("locations", {})

        for item in data.get("items", []):
            row = {
                'id': item.get('id'),
                'name': item.get('name'),
                'description': item.get('description'),
                'property_name': property_map.get(item.get('property_id'), ''),
                'category_name': category_map.get(item.get('category_id'), ''),
                'location_name': location_map.get(item.get('location_id'), ''),
                'manufacturer': item.get('manufacturer'),
                'model_number': item.get('model_number'),
                'serial_number': item.get('serial_number'),
                'condition': item.get('condition'),
                'quantity': item.get('quantity'),
                'purchase_date': item.get('purchase_date'),
                'purchase_price': item.get('purchase_price'),
                'current_value': item.get('current_value'),
                'currency': item.get('currency'),
                'warranty_expiration': item.get('warranty_expiration'),
                'barcode': item.get('barcode'),
                'tags': ','.join(item.get('tags') or []) if item.get('tags') else '',
                'notes': item.get('notes'),
                'created_at': item.get('created_at'),
            }
            writer.writerow(row)

        return output.getvalue()

    def create_export_zip(self, db: Session) -> str:
        """
        Create a ZIP archive with all data.

        Returns the path to the created ZIP file.
        """
        logger.info("Starting data export...")

        # Get all data
        data = self._get_all_data(db)

        # Create temp directory for building the archive
        temp_dir = tempfile.mkdtemp(prefix="homeregistry_export_")

        try:
            # Create data.json (without internal lookups)
            json_data = {k: v for k, v in data.items() if not k.startswith('_')}
            json_path = os.path.join(temp_dir, "data.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            # Create items.csv
            csv_content = self._generate_items_csv(data)
            csv_path = os.path.join(temp_dir, "items.csv")
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)

            # Create images directory and copy files
            images_dir = os.path.join(temp_dir, "images")
            os.makedirs(images_dir, exist_ok=True)

            for image in data.get("images", []):
                item_id = image.get("item_id")
                filename = image.get("filename")
                original_filename = image.get("original_filename", filename)

                if item_id and filename:
                    # Create item subdirectory
                    item_images_dir = os.path.join(images_dir, item_id)
                    os.makedirs(item_images_dir, exist_ok=True)

                    # Source path
                    src_path = os.path.join(settings.images_path, filename)

                    if os.path.exists(src_path):
                        # Use original filename if available, otherwise use stored filename
                        dst_filename = original_filename or filename
                        dst_path = os.path.join(item_images_dir, dst_filename)

                        # Handle duplicate filenames
                        counter = 1
                        base, ext = os.path.splitext(dst_filename)
                        while os.path.exists(dst_path):
                            dst_filename = f"{base}_{counter}{ext}"
                            dst_path = os.path.join(item_images_dir, dst_filename)
                            counter += 1

                        shutil.copy2(src_path, dst_path)
                    else:
                        logger.warning(f"Image file not found: {src_path}")

            # Create documents directory and copy files
            documents_dir = os.path.join(temp_dir, "documents")
            os.makedirs(documents_dir, exist_ok=True)

            for document in data.get("documents", []):
                item_id = document.get("item_id")
                filename = document.get("filename")
                original_filename = document.get("original_filename", filename)

                if item_id and filename:
                    # Create item subdirectory
                    item_docs_dir = os.path.join(documents_dir, item_id)
                    os.makedirs(item_docs_dir, exist_ok=True)

                    # Source path
                    src_path = os.path.join(settings.documents_path, filename)

                    if os.path.exists(src_path):
                        # Use original filename if available
                        dst_filename = original_filename or filename
                        dst_path = os.path.join(item_docs_dir, dst_filename)

                        # Handle duplicate filenames
                        counter = 1
                        base, ext = os.path.splitext(dst_filename)
                        while os.path.exists(dst_path):
                            dst_filename = f"{base}_{counter}{ext}"
                            dst_path = os.path.join(item_docs_dir, dst_filename)
                            counter += 1

                        shutil.copy2(src_path, dst_path)
                    else:
                        logger.warning(f"Document file not found: {src_path}")

            # Create the ZIP file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            zip_filename = f"homeregistry_export_{timestamp}.zip"
            zip_path = os.path.join(tempfile.gettempdir(), zip_filename)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            logger.info(f"Export created: {zip_path}")
            return zip_path

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)


# Singleton instance
export_service = ExportService()
