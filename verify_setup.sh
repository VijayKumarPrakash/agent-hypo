#!/bin/bash
# Verification script for A2A service setup

echo "============================================"
echo "White Agent A2A Setup Verification"
echo "============================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
    echo "   ✓ Python $PYTHON_VERSION (OK)"
else
    echo "   ✗ Python $PYTHON_VERSION (Need 3.11+)"
    exit 1
fi

# Check if requirements are installed
echo ""
echo "2. Checking dependencies..."
MISSING=0

for package in fastapi uvicorn pydantic requests boto3 pandas numpy; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "   ✓ $package installed"
    else
        echo "   ✗ $package missing"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "   Install missing packages with:"
    echo "   pip install -r requirements.txt"
    echo ""
fi

# Check directory structure
echo ""
echo "3. Checking directory structure..."
DIRS_OK=1

for dir in app src/white_agent; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir/ exists"
    else
        echo "   ✗ $dir/ missing"
        DIRS_OK=0
    fi
done

for file in app/server.py app/agent.py app/models.py app/storage.py Dockerfile; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file missing"
        DIRS_OK=0
    fi
done

# Check environment configuration
echo ""
echo "4. Checking environment configuration..."
if [ -f ".env" ]; then
    echo "   ✓ .env file exists"

    # Check key variables
    if grep -q "S3_BUCKET" .env && grep -q "S3_ACCESS_KEY_ID" .env; then
        echo "   ✓ S3 configuration present"
    else
        echo "   ⚠ S3 configuration incomplete (check .env)"
    fi

    if grep -q "GEMINI_API_KEY" .env; then
        echo "   ✓ GEMINI_API_KEY present (LLM mode available)"
    else
        echo "   ⚠ GEMINI_API_KEY not set (will use traditional mode)"
    fi
else
    echo "   ✗ .env file not found"
    echo "     Copy .env.a2a.example to .env and configure it"
fi

# Summary
echo ""
echo "============================================"
echo "Summary"
echo "============================================"

if [ $MISSING -eq 0 ] && [ $DIRS_OK -eq 1 ]; then
    echo "✓ Setup looks good!"
    echo ""
    echo "Next steps:"
    echo "  1. Configure .env file (if not done)"
    echo "  2. Run server: uvicorn app.server:app --reload"
    echo "  3. Test: python test_a2a_service.py"
    echo "  4. View docs: http://localhost:8000/docs"
else
    echo "✗ Some issues found. Please fix them before running."
fi

echo ""
