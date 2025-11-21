# How to Run Promptfoo Red Team Tests

Quick start guide for running official Promptfoo red team assessments.

---

## Prerequisites (5 minutes)

### 1. Install Node.js and npm

**Check if already installed:**
```bash
node --version
npm --version
```

**If not installed:**
- Download from: https://nodejs.org/ (LTS version recommended)
- Or use package manager:
```bash
# Ubuntu/Debian
sudo apt install nodejs npm

# macOS
brew install node
```

---

### 2. Install Promptfoo

```bash
npm install -g promptfoo
```

**Verify installation:**
```bash
promptfoo --version
```

---

### 3. Install Python Dependencies

```bash
pip3 install requests aiohttp
```

---

### 4. Start RAG API

```bash
# From project root
docker compose up -d

# Verify it's running
curl http://localhost:8000/health
```

---

## Quick Start (2 minutes)

### Option 1: Automated Setup

```bash
cd promptfoo_official/scripts
./setup.sh
```

This script will:
- Check all prerequisites
- Install Promptfoo if needed
- Verify RAG API is accessible
- Set up provider scripts

Then test the provider:
```bash
./test_provider.sh
```

---

### Option 2: Manual Setup

```bash
# Navigate to promptfoo_official
cd promptfoo_official

# Make scripts executable
chmod +x scripts/*.sh
chmod +x providers/*.py

# Test provider connection
python3 providers/rag_provider.py "What is Docker?"
```

Expected output (JSON):
```json
{
  "output": "Docker is a platform...",
  "metadata": {
    "sources": [...],
    "file_id": "security-manual-001"
  }
}
```

---

## Run Your First Test (1 minute)

### PII Compliance Test

```bash
cd promptfoo_official/scripts
./run_single_test.sh pii
```

**What it tests:**
- Credit card leakage
- SSN exposure
- Email/phone disclosure
- Medical record privacy

**Time:** ~1 minute
**Tests:** 30 tests

---

## View Results

### Option 1: Web UI (Recommended)

```bash
promptfoo view
```

Opens browser with interactive results dashboard.

---

### Option 2: Command Line

```bash
# Quick summary
cat ../results/pii_compliance/summary.txt

# Detailed JSON
jq . ../results/pii_compliance/results.json

# Failed tests only
jq '.tests[] | select(.pass == false)' ../results/pii_compliance/results.json
```

---

## Run Other Tests

### All Available Tests

```bash
cd promptfoo_official/scripts

# PII Compliance (GDPR, CCPA, HIPAA)
./run_single_test.sh pii              # 30 tests, ~1 min

# Security Vulnerabilities (OWASP)
./run_single_test.sh security         # 100 tests, ~3 min

# Harmful Content (Trust & Safety)
./run_single_test.sh harmful          # 102 tests, ~3 min

# Brand Protection
./run_single_test.sh brand            # 80 tests, ~2 min

# Comprehensive (All categories)
./run_single_test.sh comprehensive    # 159 tests, ~5 min
```

---

### Run All Tests

```bash
./run_all_tests.sh
```

**Runs:**
1. PII compliance
2. Security vulnerabilities
3. Harmful content
4. Brand protection
5. Comprehensive test

**Total time:** ~15-20 minutes

---

## Understanding Results

### Test Results Structure

```
results/
├── latest/              # Most recent test
│   ├── results.json     # Detailed results
│   └── summary.txt      # Quick summary
│
├── pii_compliance/      # PII test results
├── security_vulns/      # Security test results
├── harmful_content/     # Safety test results
└── brand_protection/    # Brand test results
```

---

### Reading Results

**Summary:**
```bash
cat results/latest/summary.txt
```

Example output:
```
Red Team Assessment Results
===========================
Total Tests: 30
Passed: 28
Failed: 2
Success Rate: 93.3%

Failed Tests:
- PII leakage in response #12: Credit card detected
- PII leakage in response #24: SSN detected
```

**Detailed Results:**
```bash
promptfoo view
```

Shows:
- Each test prompt
- Model response
- Pass/fail status
- Failure reason
- Vulnerability details

---

## Common Workflows

### Daily Testing
```bash
# Quick security check
cd promptfoo_official/scripts
./run_single_test.sh security
```

---

### Pre-Deployment
```bash
# Comprehensive audit
cd promptfoo_official/scripts
./run_all_tests.sh
```

---

### Compliance Verification
```bash
# PII compliance
./run_single_test.sh pii

# Content safety
./run_single_test.sh harmful
```

---

## Troubleshooting

### "Promptfoo command not found"

**Solution:**
```bash
npm install -g promptfoo
```

---

### "RAG API not accessible"

**Solution:**
```bash
# Check if running
docker compose ps

# Start if needed
docker compose up -d

# Test endpoint
curl http://localhost:8000/health
```

---

### "Provider test failed"

**Solution 1:** Check environment variables
```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
```

**Solution 2:** Test provider directly
```bash
cd promptfoo_official
python3 providers/rag_provider.py "test query"
```

---

### "Permission denied"

**Solution:**
```bash
cd promptfoo_official
chmod +x scripts/*.sh
chmod +x providers/*.py
```

---

## Customization

### Test Different Document

```bash
export RAG_FILE_ID="your-document-id"
./run_single_test.sh pii
```

---

### Adjust Test Count

Edit `configs/pii_compliance.yaml`:
```yaml
redteam:
  numTests: 50  # Increase from default
```

---

### Add Your Competitors

Edit `configs/brand_protection.yaml`:
```yaml
plugins:
  - id: competitors
    config:
      competitors:
        - "Your Competitor 1"
        - "Your Competitor 2"
```

---

## Next Steps

### For Beginners
1. ✅ Run setup: `./setup.sh`
2. ✅ Test provider: `./test_provider.sh`
3. ✅ Run PII test: `./run_single_test.sh pii`
4. ✅ View results: `promptfoo view`

### For Regular Use
1. Run tests before each deployment
2. Review results in web UI
3. Fix identified vulnerabilities
4. Re-test to verify fixes

### For Advanced Users
1. Read `INTEGRATION_GUIDE.md` for complete documentation
2. Customize configurations in `configs/`
3. Create custom providers for other LLM apps
4. Integrate with CI/CD pipelines

---

## Quick Reference

```bash
# Setup and test
cd promptfoo_official/scripts
./setup.sh
./test_provider.sh

# Run specific test
./run_single_test.sh [pii|security|harmful|brand|comprehensive]

# Run all tests
./run_all_tests.sh

# View results
promptfoo view
```

---

## Documentation

- **INTEGRATION_GUIDE.md** - Complete integration documentation
- **configs/README.md** - Configuration files reference
- **providers/README.md** - Provider implementation details
- **scripts/README.md** - Helper scripts documentation

---

**Ready to start testing?**

```bash
cd promptfoo_official/scripts
./setup.sh && ./run_single_test.sh pii
```

🎉 Your first red team assessment will complete in ~1 minute!
