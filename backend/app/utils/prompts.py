AI_ANALYSIS_PROMPT_TEMPLATE = """Analyze these image(s) of a household item and extract information in JSON format.

EXISTING CATEGORIES: {categories}

CATEGORY INSTRUCTIONS:
- STRONGLY PREFER selecting from the existing categories listed above
- Only suggest a NEW category if the item truly doesn't fit any existing category
- If suggesting a new category, use a broad, reusable name (e.g., "Pet Supplies" not "Dog Food")
- Set "category_is_new" to true ONLY if suggesting a category not in the list above

Return this exact JSON structure:
{{
  "item_name": "descriptive name",
  "category": "category name (from existing list or new if necessary)",
  "category_is_new": false,
  "description": "detailed 2-3 sentence description",
  "manufacturer": "brand/manufacturer if visible, otherwise null",
  "model_number": "model number if visible, otherwise null",
  "serial_number": "serial number if visible (look carefully), otherwise null",
  "barcode": "barcode/UPC number if visible, otherwise null",
  "condition": "new|excellent|good|fair|poor",
  "estimated_value_nok": estimated price in Norwegian Kroner or null,
  "purchase_location": "store/retailer name if visible on packaging/receipts, otherwise null",
  "suggested_location": "suggested room/location (Kitchen, Living Room, Bedroom, Garage, etc.)",
  "tags": ["descriptive", "tags", "for", "item"],
  "key_features": ["feature1", "feature2", "feature3"],
  "warranty_info": "any visible warranty information, otherwise null",
  "confidence_score": 0.0-1.0
}}

Tags should be useful search keywords (e.g., "electronic", "fragile", "warranty", "valuable", "seasonal").
If multiple items in images, focus on the primary/largest item. Return ONLY valid JSON, no markdown formatting."""


def get_analysis_prompt(categories: list[str] = None) -> str:
    """Get the AI analysis prompt with existing categories"""
    if categories:
        category_list = ", ".join(categories)
    else:
        # Fallback to default categories if none provided
        category_list = "Electronics, Furniture, Appliances, Kitchen & Dining, Clothing & Accessories, Tools & Equipment, Outdoor & Garden, Sports & Recreation, Books & Media, Art & Decor, Jewelry & Watches, Musical Instruments, Toys & Games, Office Supplies, Health & Personal Care, Automotive"

    return AI_ANALYSIS_PROMPT_TEMPLATE.format(categories=category_list)
