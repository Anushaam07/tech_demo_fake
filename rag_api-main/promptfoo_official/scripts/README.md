# Promptfoo Helper Scripts

This directory contains helper scripts to simplify running Promptfoo red team tests.

## Available Scripts

### 1. `setup.sh` - Initial Setup
**Purpose:** Set up Promptfoo integration and verify all dependencies

**What it does:**
- Checks Node.js and npm installation
- Installs Promptfoo CLI if not present
- Verifies Python dependencies
- Configures provider scripts
- Checks Docker and RAG API status
- Provides next steps

**Usage:**
```bash
cd promptfoo_official/scripts
./setup.sh
```

**When to use:** First time setup or troubleshooting installation issues

---

### 2. `test_provider.sh` - Test Provider Connection
**Purpose:** Verify that the Python provider can communicate with RAG API

**What it does:**
- Checks RAG API accessibility
- Tests sync provider (`rag_provider.py`)
- Tests async provider (`rag_provider_async.py`)
- Sends a test query and displays response

**Usage:**
```bash
cd promptfoo_official/scripts
./test_provider.sh
```

**When to use:** Before running tests, or if you suspect provider connection issues

---

### 3. `run_single_test.sh` - Run Individual Tests
**Purpose:** Run a specific test configuration

**What it does:**
- Validates test type
- Checks prerequisites (Promptfoo, RAG API)
- Runs specified test configuration
- Displays results summary

**Usage:**
```bash
cd promptfoo_official/scripts

# Run PII compliance tests
./run_single_test.sh pii

# Run security vulnerability tests
./run_single_test.sh security

# Run harmful content tests
./run_single_test.sh harmful

# Run brand protection tests
./run_single_test.sh brand

# Run comprehensive test suite
./run_single_test.sh comprehensive
# or
./run_single_test.sh all
```

**Available test types:**
- `pii` - PII compliance (GDPR, CCPA, HIPAA)
- `security` - Security vulnerabilities (OWASP)
- `harmful` - Harmful content and safety
- `brand` - Brand protection
- `comprehensive` / `all` - Complete test suite

**When to use:** Targeted testing for specific security areas

---

### 4. `run_all_tests.sh` - Run Complete Test Suite
**Purpose:** Run all test configurations sequentially

**What it does:**
- Checks prerequisites
- Runs all 5 test configurations in order:
  1. PII compliance
  2. Security vulnerabilities
  3. Harmful content
  4. Brand protection
  5. Comprehensive test
- Reports progress and success/failure for each

**Usage:**
```bash
cd promptfoo_official/scripts
./run_all_tests.sh
```

**When to use:** Comprehensive security audit before deployment

**Note:** This takes longer (~15-20 minutes) as it runs all tests

---

## Quick Start Workflow

### First Time Setup
```bash
# 1. Navigate to scripts directory
cd promptfoo_official/scripts

# 2. Run setup
./setup.sh

# 3. Test provider connection
./test_provider.sh

# 4. Run your first test
./run_single_test.sh pii
```

### Regular Testing Workflow
```bash
# 1. Ensure RAG API is running
docker compose up -d

# 2. Run specific test
cd promptfoo_official/scripts
./run_single_test.sh security

# 3. View results
promptfoo view
```

### Before Deployment
```bash
# Run complete test suite
cd promptfoo_official/scripts
./run_all_tests.sh

# Review all results
cd ../results
ls -la
```

---

## Troubleshooting

### "Promptfoo is not installed"
Run setup script:
```bash
./setup.sh
```

Or install manually:
```bash
npm install -g promptfoo
```

### "RAG API is not accessible"
Start Docker containers:
```bash
cd ../..
docker compose up -d
```

Check API health:
```bash
curl http://localhost:8000/health
```

### "Provider test failed"
1. Ensure RAG API is running
2. Check if document is uploaded
3. Verify environment variables:
```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
```

### "Permission denied" errors
Make scripts executable:
```bash
chmod +x *.sh
```

---

## Environment Variables

Configure provider behavior with these environment variables:

```bash
# RAG API endpoint
export RAG_API_ENDPOINT="http://localhost:8000/query"

# Document file ID to query
export RAG_FILE_ID="security-manual-001"

# Number of results to return
export RAG_K="4"

# Request timeout (async provider only)
export RAG_TIMEOUT="30"
```

Set these before running tests to customize behavior.

---

## Script Output

All scripts provide:
- Clear progress indicators
- Success/failure status
- Next steps guidance
- Error messages with solutions

Example output:
```
=========================================
Running: pii test
Config: configs/pii_compliance.yaml
=========================================

✓ Running Promptfoo eval...
✓ 30 tests completed
✓ Results saved to results/pii_compliance/

View results:
  promptfoo view
```

---

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run Promptfoo Red Team Tests
  run: |
    cd promptfoo_official/scripts
    ./setup.sh
    ./run_all_tests.sh
```

```yaml
# GitLab CI example
promptfoo_tests:
  script:
    - cd promptfoo_official/scripts
    - ./setup.sh
    - ./run_all_tests.sh
  artifacts:
    paths:
      - promptfoo_official/results/
```

---

## Related Documentation

- **../configs/README.md** - Configuration files guide
- **../providers/README.md** - Provider implementation details
- **../INTEGRATION_GUIDE.md** - Complete integration documentation
