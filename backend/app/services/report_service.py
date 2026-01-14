import io
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from pypdf import PdfReader, PdfWriter

from ..config import settings
from ..models.property import Property
from ..models.insurance_policy import InsurancePolicy
from ..models.item import Item
from ..models.location import Location
from ..models.document import Document, DocumentType
from ..models.image import Image


class ReportService:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        os.makedirs(template_dir, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_insurance_report(
        self,
        property: Property,
        policies: List[InsurancePolicy],
        items: List[Item],
        locations: List[Location]
    ) -> bytes:
        """Generate a complete insurance report PDF for a property."""

        # Group items by location
        items_by_location = self._group_items_by_location(items, locations)

        # Calculate totals
        total_items = len(items)
        total_value = sum(float(item.current_value or 0) for item in items)

        # Calculate value by category
        value_by_category = defaultdict(lambda: {"count": 0, "value": 0})
        for item in items:
            cat_name = item.category.name if item.category else "Uncategorized"
            value_by_category[cat_name]["count"] += 1
            value_by_category[cat_name]["value"] += float(item.current_value or 0)

        # Identify items with receipt documents and assign appendix labels
        appendix_items = []
        appendix_counter = 1
        item_appendix_map = {}  # item_id -> list of (appendix_label, document)

        for item in items:
            receipt_docs = [d for d in item.documents if d.document_type == DocumentType.RECEIPT]
            if receipt_docs:
                item_appendix_map[item.id] = []
                for doc in receipt_docs:
                    label = f"A-{appendix_counter}"
                    item_appendix_map[item.id].append((label, doc))
                    appendix_items.append({
                        "label": label,
                        "item_name": item.name,
                        "document": doc
                    })
                    appendix_counter += 1

        # Find items without receipts
        items_without_receipts = [item for item in items if item.id not in item_appendix_map]

        # Prepare template data
        template_data = {
            "property": property,
            "policies": policies,
            "items_by_location": items_by_location,
            "item_appendix_map": item_appendix_map,
            "total_items": total_items,
            "total_value": total_value,
            "value_by_category": dict(value_by_category),
            "items_without_receipts": items_without_receipts,
            "appendix_items": appendix_items,
            "generated_at": datetime.now(),
            "images_path": settings.images_path,
            "documents_path": settings.documents_path,
        }

        # Render HTML template
        template = self.env.get_template("insurance_report.html")
        html_content = template.render(**template_data)

        # Generate main report PDF
        main_pdf_bytes = HTML(string=html_content).write_pdf()

        # If there are PDF receipt attachments, merge them
        pdf_receipts = [
            item for item in appendix_items
            if item["document"].mime_type == "application/pdf"
        ]

        if pdf_receipts:
            final_pdf = self._merge_pdf_receipts(main_pdf_bytes, pdf_receipts)
            return final_pdf

        return main_pdf_bytes

    def _group_items_by_location(
        self,
        items: List[Item],
        locations: List[Location]
    ) -> List[Dict[str, Any]]:
        """Group items by their location for the report."""

        # Create location lookup
        location_lookup = {loc.id: loc for loc in locations}

        # Group items
        grouped = defaultdict(list)
        for item in items:
            loc_name = item.location.name if item.location else "No Location"
            grouped[loc_name].append(item)

        # Sort and calculate totals
        result = []
        for loc_name in sorted(grouped.keys()):
            loc_items = grouped[loc_name]
            loc_value = sum(float(item.current_value or 0) for item in loc_items)
            result.append({
                "name": loc_name,
                "items": sorted(loc_items, key=lambda x: x.name),
                "item_count": len(loc_items),
                "total_value": loc_value
            })

        return result

    def _merge_pdf_receipts(
        self,
        main_pdf_bytes: bytes,
        pdf_receipts: List[Dict[str, Any]]
    ) -> bytes:
        """Merge PDF receipt documents into the main report."""

        writer = PdfWriter()

        # Add main report pages
        main_reader = PdfReader(io.BytesIO(main_pdf_bytes))
        for page in main_reader.pages:
            writer.add_page(page)

        # Add each PDF receipt with a cover page
        for receipt_info in pdf_receipts:
            doc = receipt_info["document"]
            label = receipt_info["label"]
            item_name = receipt_info["item_name"]

            # Create cover page for this receipt
            cover_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    @page {{ size: A4; margin: 2cm; }}
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        min-height: 90vh;
                        text-align: center;
                    }}
                    .label {{ font-size: 48px; font-weight: bold; color: #333; }}
                    .title {{ font-size: 24px; margin-top: 20px; color: #666; }}
                    .filename {{ font-size: 14px; margin-top: 10px; color: #999; }}
                </style>
            </head>
            <body>
                <div class="label">Appendix {label}</div>
                <div class="title">Receipt for: {item_name}</div>
                <div class="filename">{doc.original_filename}</div>
            </body>
            </html>
            """
            cover_pdf = HTML(string=cover_html).write_pdf()
            cover_reader = PdfReader(io.BytesIO(cover_pdf))
            for page in cover_reader.pages:
                writer.add_page(page)

            # Add the actual receipt PDF
            receipt_path = os.path.join(settings.documents_path, doc.filename)
            if os.path.exists(receipt_path):
                try:
                    receipt_reader = PdfReader(receipt_path)
                    for page in receipt_reader.pages:
                        writer.add_page(page)
                except Exception as e:
                    print(f"Error reading receipt PDF {receipt_path}: {e}")

        # Write final PDF
        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    def get_item_primary_image_path(self, item: Item) -> Optional[str]:
        """Get the path to the primary image thumbnail for an item."""
        primary_image = next((img for img in item.images if img.is_primary), None)
        if not primary_image:
            primary_image = item.images[0] if item.images else None

        if primary_image:
            thumbnail_path = os.path.join(
                settings.images_path, "thumbnails", primary_image.filename
            )
            if os.path.exists(thumbnail_path):
                return thumbnail_path
            # Fall back to full image
            full_path = os.path.join(settings.images_path, primary_image.filename)
            if os.path.exists(full_path):
                return full_path

        return None
