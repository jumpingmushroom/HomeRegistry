#!/bin/bash

echo "🏠 HomeRegistry Setup Verification"
echo "=================================="
echo ""

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null; then
    echo "✅ Found ($(docker --version))"
else
    echo "❌ Not found - Please install Docker"
    exit 1
fi

# Check Docker Compose
echo -n "Checking Docker Compose... "
if command -v docker-compose &> /dev/null; then
    echo "✅ Found ($(docker-compose --version))"
else
    echo "❌ Not found - Please install Docker Compose"
    exit 1
fi

# Check required files
echo ""
echo "Checking project files..."

required_files=(
    "docker-compose.yml"
    ".env.example"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "backend/app/main.py"
    "frontend/Dockerfile"
    "frontend/package.json"
    "frontend/src/main.js"
)

all_files_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        all_files_exist=false
    fi
done

# Check .env
echo ""
if [ -f ".env" ]; then
    echo "✅ .env file exists"
else
    echo "⚠️  .env file not found - Creating from .env.example"
    cp .env.example .env
    echo "✅ Created .env - Please edit it with your AI provider credentials"
fi

echo ""
echo "=================================="
if [ "$all_files_exist" = true ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env with your AI provider credentials (or use Ollama for local AI)"
    echo "2. Run: docker-compose up -d"
    echo "3. Access: http://localhost:8080"
    echo ""
    echo "For detailed instructions, see QUICK_START.md"
else
    echo "❌ Some files are missing - Please check the repository"
    exit 1
fi
