AI_ANALYSIS_PROMPT = """Analyze these image(s) of a household item and extract information in JSON format:

{
  "item_name": "descriptive name",
  "category": "best matching category from: Electronics, Tools, Furniture, Kitchen, Clothing, Books, Toys, Sports, Garden, Automotive, Office, Other",
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
}

Tags should be useful search keywords (e.g., "electronic", "fragile", "warranty", "valuable", "seasonal").
If multiple items in images, focus on the primary/largest item. Return ONLY valid JSON, no markdown formatting."""


def get_analysis_prompt() -> str:
    """Get the AI analysis prompt"""
    return AI_ANALYSIS_PROMPT
