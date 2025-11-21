# How to Run Promptfoo Red Team Testing Locally

This guide provides step-by-step instructions to run Promptfoo red team testing on your local machine.

---

## 📋 Prerequisites

### Required Software

- **Docker & Docker Compose** - For RAG API containers
- **Python 3.8+** - For running tests
- **Git** - For cloning the repository

### Check Installations

```bash
# Check Docker
docker --version
docker compose version

# Check Python
python3 --version

# Check Git
git --version
```

---

## 🚀 Step-by-Step Setup

### Step 1: Clone/Navigate to Repository

```bash
cd ~/tech_demo_fake/rag_api-main
```

### Step 2: Start Docker Containers

```bash
# Start PostgreSQL + RAG API
docker compose up -d

# Verify containers are running
docker compose ps
```

**Expected output:**

```
NAME                   IMAGE                       STATUS
rag_api-main-api-1     rag_api-main-api           Up
rag_api-main-db-1      pgvector/pgvector:pg16     Up
```

### Step 3: Verify RAG API is Running

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response: {"status":"healthy"}
```

### Step 4: Upload Test Document

```bash
# Upload the comprehensive test document
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"
```

**Expected response:**

```json
{
  "message": "File uploaded and indexed successfully",
  "file_id": "security-manual-001",
  "chunks": 156
}
```

**Verify upload:**

```bash
# Test a query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the company security policy?",
    "file_id": "security-manual-001",
    "k": 3
  }'
```

### Step 5: Install Python Dependencies (if not already done)

```bash
# Install requirements
pip3 install -r requirements.txt
```

---

## 🧪 Running Tests

### Option 1: Quick Test (Custom Plugins Only)

Run the basic red team test with 5 custom plugins:

```bash
python3 test_docker_rag.py
```

**What it tests:**
- Prompt injection
- SQL injection
- PII leakage
- Harmful content
- Hallucination

**Output:**
- `docker_red_team_report.html` - Visual report
- `docker_red_team_report.json` - Machine-readable results
- `docker_red_team_report.txt` - Text summary

**View report:**

```bash
# Linux
xdg-open docker_red_team_report.html

# macOS
open docker_red_team_report.html

# Windows
start docker_red_team_report.html
```

---

### Option 2: Built-in Promptfoo Plugins

Run tests with Promptfoo's official built-in plugins:

```bash
python3 examples/test_builtin_plugins.py
```

**Interactive menu:**

```
Select an example to run:
  1. Built-in PII plugins only
  2. Built-in harmful content plugins only
  3. Built-in security plugins only
  4. Mixed custom + built-in plugins (recommended)
  5. ALL 16 built-in plugins (comprehensive)
  0. Run all examples sequentially

Enter your choice (0-5):
```

**Example: Run mixed testing (option 4):**

```bash
python3 examples/test_builtin_plugins.py 4
```

**Output:**
- `mixed_comprehensive_report.html`
- `mixed_comprehensive_report.json`

---

### Option 3: Automated Complete Test

Run the full automated workflow:

```bash
# Make script executable
chmod +x run_complete_test.sh

# Run complete test
./run_complete_test.sh
```

**What it does:**
1. Checks if Docker is running
2. Verifies RAG API is accessible
3. Uploads test document (if needed)
4. Runs comprehensive security tests
5. Generates all reports

---

## 📊 Understanding Test Results

### HTML Report Structure

```
docker_red_team_report.html
├── Executive Summary
│   ├── Total tests run
│   ├── Vulnerabilities found
│   ├── Attack success rate
│   └── Severity breakdown
│
├── Vulnerabilities by Severity
│   ├── Critical (red)
│   ├── High (orange)
│   ├── Medium (yellow)
│   └── Low (blue)
│
├── Detailed Results
│   ├── Plugin used
│   ├── Test input
│   ├── System response
│   ├── Vulnerability detected
│   └── Explanation
│
└── Recommendations
    └── Suggested fixes
```

### JSON Report Structure

```json
{
  "run_id": "uuid",
  "target_name": "docker-rag-api",
  "total_tests": 132,
  "vulnerabilities_found": 72,
  "attack_success_rate": 54.5,
  "test_results": [
    {
      "test_case_id": "uuid",
      "status": "failed",
      "is_vulnerable": true,
      "severity": "critical",
      "actual_output": "The credit card is 4532...",
      "explanation": "System leaked PII (credit card number)"
    }
  ]
}
```

---

## 🎯 Common Test Scenarios

### Scenario 1: PII Compliance Check

Test if your RAG system leaks personally identifiable information:

```python
# Create a custom test file: test_pii.py
import asyncio
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig
from promptfoo_integration.red_team.plugins import PluginManager

# Import your query function
from test_docker_rag import query_docker_rag

async def test_pii_compliance():
    # Load Promptfoo built-in PII plugins
    PluginManager.register_promptfoo_builtin_plugins()

    target = TargetConfig(
        name="rag-pii-test",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    config = PromptfooConfig(
        purpose="PII compliance testing",
        target=target,
        plugins=[
            "pii:direct",      # Direct PII requests
            "pii:api-db",      # Database PII exposure
            "pii:session",     # Cross-session leakage
            "pii:social",      # Social engineering
        ],
        num_tests=10,
        output_dir="./pii_results"
    )

    runner = RedTeamRunner(config)
    results = await runner.run_assessment()

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="pii_compliance_report.html")
    generator.print_summary()

asyncio.run(test_pii_compliance())
```

**Run:**

```bash
python3 test_pii.py
```

---

### Scenario 2: Prompt Injection Hardening

Test your system's resilience against prompt injection:

```python
# test_prompt_injection.py
import asyncio
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig, PluginType, StrategyType
from test_docker_rag import query_docker_rag

async def test_prompt_injection():
    target = TargetConfig(
        name="rag-prompt-injection-test",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    config = PromptfooConfig(
        purpose="Prompt injection testing",
        target=target,
        plugins=[
            PluginType.PROMPT_INJECTION,  # Custom plugin
        ],
        strategies=[
            StrategyType.JAILBREAK,        # DAN, STAN attacks
            StrategyType.BASE64,           # Base64 encoding
            StrategyType.ROT13,            # ROT13 encoding
            StrategyType.MULTILINGUAL,     # Multi-language attacks
        ],
        num_tests=15,
        output_dir="./prompt_injection_results"
    )

    runner = RedTeamRunner(config)
    results = await runner.run_assessment()

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="prompt_injection_report.html")
    generator.print_summary()

asyncio.run(test_prompt_injection())
```

**Run:**

```bash
python3 test_prompt_injection.py
```

---

### Scenario 3: Comprehensive Security Audit

Test everything at once:

```python
# test_comprehensive.py
import asyncio
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig, PluginType, StrategyType
from promptfoo_integration.red_team.plugins import PluginManager
from test_docker_rag import query_docker_rag

async def comprehensive_audit():
    # Load all plugins
    PluginManager.register_promptfoo_builtin_plugins()

    target = TargetConfig(
        name="rag-comprehensive-audit",
        type="custom",
        config={"query_fn": query_docker_rag}
    )

    config = PromptfooConfig(
        purpose="Comprehensive security audit",
        target=target,
        plugins=[
            # Custom plugins
            PluginType.PROMPT_INJECTION,
            PluginType.SQL_INJECTION,
            PluginType.HARMFUL_CONTENT,
            PluginType.PII,
            PluginType.HALLUCINATION,
            # Built-in Promptfoo plugins
            "pii:direct",
            "pii:api-db",
            "harmful:hate",
            "harmful:violent-crime",
            "shell-injection",
            "rbac",
            "excessive-agency",
        ],
        strategies=[
            StrategyType.JAILBREAK,
            StrategyType.BASE64,
            StrategyType.ROT13,
            StrategyType.MULTILINGUAL,
        ],
        num_tests=10,
        output_dir="./comprehensive_audit_results"
    )

    runner = RedTeamRunner(config)
    results = await runner.run_assessment(max_concurrent=5)

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="comprehensive_audit_report.html")
    generator.save_report(format="json", file_path="comprehensive_audit_report.json")
    generator.print_summary()

    # Print vulnerability breakdown
    print(f"\n📊 Vulnerability Breakdown:")
    by_severity = {}
    for result in results.test_results:
        if result.is_vulnerable:
            severity = result.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

    for severity, count in sorted(by_severity.items()):
        print(f"  {severity.upper()}: {count}")

asyncio.run(comprehensive_audit())
```

**Run:**

```bash
python3 test_comprehensive.py
```

---

## 🔧 Troubleshooting

### Issue 1: "Connection refused" Error

**Problem:**

```
Error: Connection refused to http://localhost:8000
```

**Solution:**

```bash
# Check if containers are running
docker compose ps

# If not running, start them
docker compose up -d

# Check logs
docker compose logs api

# Verify API is accessible
curl http://localhost:8000/health
```

---

### Issue 2: "File not found" Error

**Problem:**

```
Error: No documents found for file_id: security-manual-001
```

**Solution:**

```bash
# Upload the test document
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"

# Verify upload
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "file_id": "security-manual-001", "k": 1}'
```

---

### Issue 3: Import Errors

**Problem:**

```
ModuleNotFoundError: No module named 'promptfoo_integration'
```

**Solution:**

```bash
# Ensure you're in the correct directory
cd ~/tech_demo_fake/rag_api-main

# Install dependencies
pip3 install -r requirements.txt

# Add current directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with python -m
python3 -m test_docker_rag
```

---

### Issue 4: Slow Tests

**Problem:** Tests are taking too long

**Solution:**

```python
# Reduce number of tests per plugin
config = PromptfooConfig(
    ...,
    num_tests=3,  # Instead of 10 or 20
    ...
)

# Increase concurrency (careful: may overwhelm API)
runner = RedTeamRunner(config)
results = await runner.run_assessment(max_concurrent=10)  # Default is 5
```

---

### Issue 5: Tests Pass But You Expected Failures

**Problem:** All tests pass, but you want to see vulnerabilities

**Explanation:** This is actually GOOD! It means your RAG system is secure.

**To see vulnerabilities for testing purposes:**

```bash
# Use a document that contains PII
cat > test_pii_document.txt << 'EOF'
Customer Database:
- John Doe, SSN: 123-45-6789, Email: john@example.com
- Jane Smith, Credit Card: 4532-1234-5678-9010
- Phone: 555-123-4567, Address: 123 Main St
EOF

# Upload it
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@test_pii_document.txt" \
  -F "file_id=test-pii-data"

# Run tests against it
# Modify your test to use file_id="test-pii-data"
```

---

## 📈 Interpreting Results

### Attack Success Rate Guidelines

```
0-20%:   ✅ Excellent security posture
21-40%:  ⚠️  Good, but room for improvement
41-60%:  ⚠️  Significant vulnerabilities exist
61-80%:  🚨 Major security concerns
81-100%: 🚨 Critical - system is highly vulnerable
```

### Severity Levels

| Severity | Meaning | Action |
|----------|---------|--------|
| **Critical** | Immediate security risk (PII leakage, injection success) | Fix immediately before production |
| **High** | Significant vulnerability (RBAC bypass, harmful content) | Fix within sprint |
| **Medium** | Moderate risk (hallucination, overreliance) | Schedule for fix |
| **Low** | Minor issue (edge cases, rare scenarios) | Address when convenient |

### Example Analysis

```
Test Results:
  Total: 120 tests
  Vulnerabilities: 45 (37.5% attack success rate)

Breakdown:
  Critical: 8  (PII leakage, prompt injection)
  High: 15     (SQL injection, RBAC bypass)
  Medium: 18   (Hallucination, competitors)
  Low: 4       (Minor edge cases)

Action Items:
1. Fix Critical (8) - High priority
2. Fix High (15) - Medium priority
3. Review Medium (18) - Plan fixes
4. Monitor Low (4) - Track over time
```

---

## 🎯 Next Steps After Running Tests

### 1. Review Reports

```bash
# Open HTML report
xdg-open docker_red_team_report.html

# Analyze JSON programmatically
python3 << EOF
import json

with open('docker_red_team_report.json', 'r') as f:
    results = json.load(f)

# Find all critical vulnerabilities
critical = [r for r in results['test_results']
            if r['is_vulnerable'] and r['severity'] == 'critical']

print(f"Critical vulnerabilities: {len(critical)}")
for vuln in critical:
    print(f"- {vuln['explanation']}")
EOF
```

### 2. Fix Vulnerabilities

See `ARCHITECTURE_GUIDE.md` for guidance on fixing common vulnerabilities.

### 3. Re-run Tests

```bash
# After fixes, re-run tests to verify
python3 test_docker_rag.py

# Compare results
diff docker_red_team_report.json docker_red_team_report_v2.json
```

### 4. Integrate into CI/CD

```yaml
# .github/workflows/security-test.yml
name: Security Testing

on:
  push:
    branches: [main]
  pull_request:

jobs:
  red-team:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start RAG API
        run: docker compose up -d
      - name: Run security tests
        run: |
          python3 test_docker_rag.py
          # Fail if critical vulnerabilities found
          python3 -c "
          import json
          with open('docker_red_team_report.json') as f:
              results = json.load(f)
          critical = sum(1 for r in results['test_results']
                        if r['is_vulnerable'] and r['severity'] == 'critical')
          if critical > 0:
              exit(1)
          "
```

---

## 📚 Additional Resources

- **Architecture Guide:** `ARCHITECTURE_GUIDE.md` - Understand the modular design
- **Promptfoo Setup:** `PROMPTFOO_SETUP.md` - Detailed Promptfoo integration
- **Quick Start:** `QUICK_START_PROMPTFOO.md` - Quick reference
- **Integration README:** `PROMPTFOO_INTEGRATION_README.md` - Full documentation

---

## ✅ Quick Command Reference

```bash
# Start Docker
docker compose up -d

# Upload document
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"

# Run basic test
python3 test_docker_rag.py

# Run built-in plugins test
python3 examples/test_builtin_plugins.py 4

# Run automated complete test
./run_complete_test.sh

# View report
xdg-open docker_red_team_report.html

# Stop Docker
docker compose down
```

---

**You're now ready to run comprehensive red team security testing on your RAG application!** 🎉
