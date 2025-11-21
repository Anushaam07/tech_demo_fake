#!/bin/bash
# Test the RAG provider to ensure it's working correctly
# This script sends a test query to the RAG API via the provider

set -e

echo "========================================="
echo "Testing RAG Provider"
echo "========================================="
echo ""

# Check if RAG API is running
echo "Checking RAG API..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "ERROR: RAG API is not accessible at http://localhost:8000"
    echo "Start with: docker compose up -d"
    exit 1
fi

echo "✓ RAG API is running"
echo ""

# Test query
test_query="What security measures are in place?"

echo "Testing provider with query:"
echo "  \"$test_query\""
echo ""

# Navigate to promptfoo_official directory
cd "$(dirname "$0")/.."

echo "Running sync provider..."
echo "----------------------------------------"
python3 providers/rag_provider.py "$test_query"
echo ""
echo "----------------------------------------"
echo ""

echo "Running async provider..."
echo "----------------------------------------"
python3 providers/rag_provider_async.py "$test_query"
echo ""
echo "----------------------------------------"
echo ""

echo "✓ Provider test completed successfully!"
echo ""
echo "Both providers are working correctly."
echo "You can now run Promptfoo tests with these providers."
