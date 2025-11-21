#!/bin/bash
# Run all Promptfoo red team tests
# This script runs all test configurations sequentially

set -e

echo "========================================="
echo "Promptfoo Red Team - Complete Test Suite"
echo "========================================="
echo ""

# Check if promptfoo is installed
if ! command -v promptfoo &> /dev/null; then
    echo "ERROR: Promptfoo is not installed"
    echo "Install with: npm install -g promptfoo"
    exit 1
fi

# Check if RAG API is running
echo "Checking RAG API status..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "WARNING: RAG API might not be running at http://localhost:8000"
    echo "Start with: docker compose up -d"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to promptfoo_official directory
cd "$(dirname "$0")/.."

echo ""
echo "Starting test suite..."
echo ""

# Test configurations to run
configs=(
    "configs/pii_compliance.yaml:PII Compliance"
    "configs/security_vulnerabilities.yaml:Security Vulnerabilities"
    "configs/harmful_content.yaml:Harmful Content"
    "configs/brand_protection.yaml:Brand Protection"
    "configs/promptfooconfig.yaml:Comprehensive Test"
)

total_tests=${#configs[@]}
current=1

for config_entry in "${configs[@]}"; do
    IFS=':' read -r config_file test_name <<< "$config_entry"

    echo "----------------------------------------"
    echo "[$current/$total_tests] Running: $test_name"
    echo "Config: $config_file"
    echo "----------------------------------------"

    # Run promptfoo eval
    if promptfoo eval -c "$config_file"; then
        echo "✓ $test_name completed successfully"
    else
        echo "✗ $test_name failed"
        exit 1
    fi

    echo ""
    ((current++))
done

echo "========================================="
echo "All tests completed successfully!"
echo "========================================="
echo ""
echo "View results:"
echo "  promptfoo view"
echo ""
echo "Or check individual result directories:"
echo "  ls -la results/"
