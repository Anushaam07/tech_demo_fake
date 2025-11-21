#!/bin/bash

# Complete Red Team Testing Script
# This script uploads the document and runs the red team assessment

set -e  # Exit on error

echo "================================================================="
echo "🚀 COMPLETE RED TEAM TESTING WORKFLOW"
echo "================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if Docker is running
echo "Step 1: Checking Docker containers..."
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Docker containers are running"
else
    echo -e "${RED}✗${NC} Docker containers are not running"
    echo "Starting Docker containers..."
    docker compose up -d
    echo "Waiting 10 seconds for services to start..."
    sleep 10
fi
echo ""

# Step 2: Check if document exists
echo "Step 2: Checking test document..."
if [ -f "comprehensive_test_document.txt" ]; then
    echo -e "${GREEN}✓${NC} Test document found ($(wc -l < comprehensive_test_document.txt) lines)"
else
    echo -e "${RED}✗${NC} Test document not found: comprehensive_test_document.txt"
    exit 1
fi
echo ""

# Step 3: Check API health
echo "Step 3: Checking API health..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API is responding"
else
    echo -e "${RED}✗${NC} API is not responding"
    echo "Please check Docker logs: docker compose logs fastapi"
    exit 1
fi
echo ""

# Step 4: Upload document
echo "Step 4: Uploading test document..."
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001")

if echo "$UPLOAD_RESPONSE" | grep -q "error\|Error\|detail"; then
    echo -e "${RED}✗${NC} Upload failed"
    echo "Response: $UPLOAD_RESPONSE"
    echo ""
    echo "Note: If the document was already uploaded, this is expected."
    echo "Continuing with red team assessment..."
else
    echo -e "${GREEN}✓${NC} Document uploaded successfully"
fi
echo ""

# Step 5: Verify document is accessible
echo "Step 5: Verifying document upload..."
QUERY_RESPONSE=$(curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the company security policy?",
    "file_id": "security-manual-001",
    "k": 2
  }')

if echo "$QUERY_RESPONSE" | grep -q "Security\|security\|policy"; then
    echo -e "${GREEN}✓${NC} Document is accessible and responding to queries"
    echo "Sample response: $(echo "$QUERY_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print((data[0].get('page_content', str(data[0]))[:80] + '...') if isinstance(data, list) and len(data) > 0 else str(data)[:80] + '...')" 2>/dev/null || echo "$QUERY_RESPONSE" | head -c 80)..."
else
    echo -e "${YELLOW}⚠${NC}  Unexpected response format"
    echo "Response: $(echo "$QUERY_RESPONSE" | head -c 200)..."
    echo ""
    echo "Continuing anyway..."
fi
echo ""

# Step 6: Run red team assessment
echo "Step 6: Running red team assessment..."
echo "This may take a few minutes..."
echo ""
python3 test_docker_rag.py

echo ""
echo "================================================================="
echo "✅ COMPLETE! Check the reports:"
echo "================================================================="
echo "  HTML: docker_red_team_report.html (open in browser)"
echo "  JSON: docker_red_team_report.json (for automation)"
echo "  Text: docker_red_team_report.txt (for console)"
echo ""
echo "To view HTML report:"
echo "  xdg-open docker_red_team_report.html"
echo "================================================================="
