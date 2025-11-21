#!/bin/bash
# Run a single Promptfoo red team test
# Usage: ./run_single_test.sh <test_type>
# Example: ./run_single_test.sh pii

set -e

# Test type to configuration file mapping
declare -A test_configs=(
    ["pii"]="configs/pii_compliance.yaml"
    ["security"]="configs/security_vulnerabilities.yaml"
    ["harmful"]="configs/harmful_content.yaml"
    ["brand"]="configs/brand_protection.yaml"
    ["comprehensive"]="configs/promptfooconfig.yaml"
    ["all"]="configs/promptfooconfig.yaml"
)

# Display usage
usage() {
    echo "Usage: $0 <test_type>"
    echo ""
    echo "Available test types:"
    echo "  pii            - PII compliance testing (GDPR, CCPA, HIPAA)"
    echo "  security       - Security vulnerability testing (OWASP)"
    echo "  harmful        - Harmful content and safety testing"
    echo "  brand          - Brand protection testing"
    echo "  comprehensive  - Complete test suite (all plugins)"
    echo "  all            - Same as comprehensive"
    echo ""
    echo "Examples:"
    echo "  $0 pii         # Run PII compliance tests"
    echo "  $0 security    # Run security vulnerability tests"
    echo "  $0 all         # Run comprehensive test suite"
    exit 1
}

# Check arguments
if [ $# -eq 0 ]; then
    usage
fi

test_type="$1"

# Check if test type is valid
if [ -z "${test_configs[$test_type]}" ]; then
    echo "ERROR: Unknown test type '$test_type'"
    echo ""
    usage
fi

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
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to promptfoo_official directory
cd "$(dirname "$0")/.."

config_file="${test_configs[$test_type]}"

echo "========================================="
echo "Running: ${test_type} test"
echo "Config: ${config_file}"
echo "========================================="
echo ""

# Run promptfoo eval
if promptfoo eval -c "$config_file"; then
    echo ""
    echo "========================================="
    echo "✓ Test completed successfully!"
    echo "========================================="
    echo ""
    echo "View results:"
    echo "  promptfoo view"
    echo ""
    echo "Or open results directory:"
    echo "  cd results/ && ls -la"
else
    echo ""
    echo "✗ Test failed"
    exit 1
fi
