#!/bin/bash

# Simple script to create placeholder PWA icons
# For production, replace these with actual designed icons

cd frontend/public

# Create a simple SVG icon
cat > icon.svg << 'EOF'
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" fill="#4CAF50"/>
  <text x="256" y="300" font-size="200" text-anchor="middle" fill="white" font-family="Arial">🏠</text>
</svg>
EOF

# Convert to PNG if ImageMagick is available
if command -v convert &> /dev/null; then
    convert icon.svg -resize 192x192 pwa-192x192.png
    convert icon.svg -resize 512x512 pwa-512x512.png
    convert icon.svg -resize 180x180 apple-touch-icon.png
    echo "Icons created successfully!"
else
    echo "ImageMagick not found. Please install it or create icons manually:"
    echo "  - pwa-192x192.png (192x192)"
    echo "  - pwa-512x512.png (512x512)"
    echo "  - apple-touch-icon.png (180x180)"
fi
