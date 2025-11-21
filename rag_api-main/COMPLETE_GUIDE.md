# Complete Guide: Modular Promptfoo Integration

This guide explains the modular architecture, why we built it this way, and how to run everything locally.

---

## 📐 Architecture Overview

### Current Directory Structure

```
promptfoo_integration/              ← Main integration package
│
├── core/                          ← Core functionality (shared)
│   ├── __init__.py
│   ├── types.py                   ← Type definitions, enums
│   ├── config.py                  ← Configuration loader (YAML/JSON/dict)
│   └── client.py                  ← Target clients (API, LangChain, Custom)
│
├── red_team/                      ← RED TEAMING MODULE ✅ COMPLETE
│   ├── __init__.py
│   ├── plugins.py                 ← 5 custom plugins
│   ├── plugins_builtin.py         ← 16 Promptfoo built-in plugins ⭐
│   ├── strategies.py              ← 7 attack strategies
│   ├── runner.py                  ← Test orchestration
│   ├── grader.py                  ← Response evaluation
│   └── report.py                  ← Report generation
│
├── evaluations/                   ← EVALUATIONS MODULE (future)
│   └── __init__.py                ← Placeholder for LLM quality testing
│
├── guardrails/                    ← GUARDRAILS MODULE (future)
│   └── __init__.py                ← Placeholder for safety controls
│
└── utils/                         ← Shared utilities
    ├── __init__.py
    └── helpers.py                 ← Helper functions
```

### YAML Configuration Files

```
examples/config_examples/
├── red_team_config.yaml                    ← Mixed (custom + built-in)
├── builtin_pii_config.yaml                 ← PII compliance
├── builtin_harmful_config.yaml             ← Content safety
├── builtin_security_config.yaml            ← Security vulnerabilities
├── builtin_brand_config.yaml               ← Brand protection
├── builtin_comprehensive_config.yaml       ← All 19 plugins
└── compliance_preset_config.yaml           ← Compliance frameworks
```

---

## 🎯 Why This Modular Approach?

### 1. **Separation of Concerns** ✅

Each module has ONE clear responsibility:

```
red_team/      → Security testing (penetration testing, vulnerabilities)
evaluations/   → Quality assessment (accuracy, relevance, coherence)
guardrails/    → Safety controls (input filters, output validators)
core/          → Shared infrastructure (config, clients, types)
```

**Why this matters:**
- Changes in one module don't break others
- Each module can be developed independently
- Testing is isolated and focused
- Debugging is easier

**Example:**
```python
# Use only red teaming
from promptfoo_integration.red_team import RedTeamRunner

# Future: Use only evaluations
from promptfoo_integration.evaluations import EvaluationRunner

# Future: Use only guardrails
from promptfoo_integration.guardrails import GuardrailValidator
```

---

### 2. **Easy Integration with Other Applications** ✅

The modular design works with ANY Python LLM application:

**Langchain Application:**
```python
from langchain.chains import RetrievalQA
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig

# Your existing Langchain RAG
qa_chain = RetrievalQA.from_chain_type(...)

# Test it with Promptfoo
target = TargetConfig(
    name="my-langchain-app",
    type="langchain",
    config={"chain": qa_chain}
)

config = PromptfooConfig(
    purpose="Security testing",
    target=target,
    plugins=["pii:direct", "harmful:hate"]
)

runner = RedTeamRunner(config)
results = await runner.run_assessment()
```

**OpenAI API Application:**
```python
import openai
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig

def query_openai(prompt: str, **kwargs) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

target = TargetConfig(
    name="openai-assistant",
    type="custom",
    config={"query_fn": query_openai}
)

config = PromptfooConfig(
    purpose="Security testing",
    target=target,
    plugins=["pii:direct", "prompt-injection"]
)

runner = RedTeamRunner(config)
results = await runner.run_assessment()
```

**Any FastAPI Application:**
```python
import requests
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig

def query_api(prompt: str, **kwargs) -> str:
    response = requests.post(
        "https://your-api.com/chat",
        json={"message": prompt}
    )
    return response.json()["response"]

target = TargetConfig(
    name="my-fastapi-app",
    type="custom",
    config={"query_fn": query_api}
)

runner = RedTeamRunner(config)
results = await runner.run_assessment()
```

**Why this matters:**
- One integration works everywhere
- No need to rewrite for each application
- Standardized security testing across organization
- Easy to onboard new LLM applications

---

### 3. **Future-Proof for New Modules** ✅

Adding new modules is simple and doesn't break existing code:

**Today (Red Teaming):**
```
promptfoo_integration/
├── red_team/          ← Working ✅
├── evaluations/       ← Placeholder
└── guardrails/        ← Placeholder
```

**Tomorrow (Add Evaluations):**
```python
# promptfoo_integration/evaluations/runner.py

class EvaluationRunner:
    """Evaluate LLM response quality."""

    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.client = PromptfooClient.create_target_client(config.target)

    async def run_evaluation(self):
        """
        Test metrics:
        - Accuracy (correctness)
        - Relevance (context alignment)
        - Coherence (logical flow)
        - Factuality (truthfulness)
        """
        pass
```

**Next Week (Add Guardrails):**
```python
# promptfoo_integration/guardrails/validator.py

class GuardrailValidator:
    """Input/output safety validation."""

    def validate_input(self, prompt: str) -> ValidationResult:
        """Filter malicious inputs before LLM."""
        pass

    def validate_output(self, response: str) -> ValidationResult:
        """Filter harmful outputs before user."""
        pass
```

**Use Together:**
```python
from promptfoo_integration import (
    RedTeamRunner,         # Security testing
    EvaluationRunner,      # Quality assessment
    GuardrailValidator     # Safety controls
)

# Test security
red_team_results = await RedTeamRunner(config).run_assessment()

# Test quality
eval_results = await EvaluationRunner(config).run_evaluation()

# Deploy with guardrails
validator = GuardrailValidator(config)
if validator.validate_input(user_prompt).is_safe:
    response = llm.query(user_prompt)
    if validator.validate_output(response).is_safe:
        return response
```

**Why this matters:**
- Add capabilities incrementally
- No need to refactor existing code
- Each module can be versioned independently
- Easy to maintain and update

---

### 4. **Flexible Configuration** ✅

Single YAML configuration for all modules:

```yaml
# config.yaml

# Target application (shared)
target:
  name: "my-rag-app"
  type: "custom"
  endpoint: "http://localhost:8000/query"

# Red team module config
red_team:
  plugins:
    - "pii:direct"
    - "harmful:hate"
  strategies:
    - "jailbreak"
  num_tests: 10

# Evaluations module config (future)
evaluations:
  metrics:
    - "accuracy"
    - "relevance"
  benchmark: "RAG-QA-v1"

# Guardrails module config (future)
guardrails:
  input_filters:
    - "pii_filter"
    - "profanity_filter"
  output_validators:
    - "harmful_content_check"
    - "factuality_check"
```

**Load and use:**
```python
config = ConfigLoader.load_from_yaml("config.yaml")

# Each module reads its own section
red_team_runner = RedTeamRunner(config.red_team)
eval_runner = EvaluationRunner(config.evaluations)
guardrail = GuardrailValidator(config.guardrails)
```

**Why this matters:**
- Single source of truth for configuration
- Easy to version control
- Share configs across team
- Environment-specific configs (dev, staging, prod)

---

### 5. **Plugin Extensibility** ✅

Mix and match custom and built-in plugins:

```python
from promptfoo_integration.red_team.plugins import PluginManager

# Load built-in plugins
PluginManager.register_promptfoo_builtin_plugins()

config = PromptfooConfig(
    purpose="Comprehensive testing",
    target=your_target,
    plugins=[
        # Custom plugins (domain-specific)
        PluginType.PROMPT_INJECTION,
        PluginType.SQL_INJECTION,
        PluginType.HALLUCINATION,

        # Built-in Promptfoo plugins (industry-standard)
        "pii:direct",
        "pii:api-db",
        "harmful:hate",
        "harmful:violent-crime",
        "shell-injection",
        "rbac",

        # Your own custom plugin
        "my-custom-rag-plugin",
    ]
)
```

**Why this matters:**
- Get best of both worlds
- Custom plugins for specific needs
- Built-in plugins for standard compliance
- Easy to add new plugins without code changes

---

## 🔢 Plugin Summary

### Available Now: 21 Plugins

**Custom Plugins (5):**
```
1. prompt-injection      - Instruction override attacks
2. sql-injection         - SQL injection vulnerabilities
3. harmful-content       - Harmful content generation
4. pii                   - PII leakage
5. hallucination         - Information fabrication
```

**Promptfoo Built-in PII Plugins (4):**
```
6. pii:direct            - Direct PII requests
7. pii:api-db            - Database/API PII exposure
8. pii:session           - Cross-session leakage
9. pii:social            - Social engineering
```

**Promptfoo Built-in Harmful Content Plugins (5):**
```
10. harmful:hate                    - Hate speech
11. harmful:harassment-bullying     - Harassment
12. harmful:violent-crime           - Violence
13. harmful:privacy                 - Privacy violations
14. harmful:specialized-advice      - Dangerous advice
```

**Promptfoo Built-in Security Plugins (3):**
```
15. shell-injection      - Command injection
16. debug-access         - Debug mode access
17. rbac                 - Access control bypass
```

**Promptfoo Built-in Brand & Trust Plugins (4):**
```
18. competitors          - Competitor mentions
19. contracts            - Unauthorized commitments
20. excessive-agency     - Actions beyond scope
21. overreliance         - Overconfident responses
```

---

## 🚀 How to Run Locally - Complete Steps

### Prerequisites

```bash
# Check Docker
docker --version
docker compose version

# Check Python
python3 --version  # Should be 3.8+

# Check you're in correct directory
pwd  # Should show: /home/user/tech_demo_fake/rag_api-main
```

---

### Step 1: Start Docker Containers

```bash
# Start PostgreSQL + RAG API
docker compose up -d

# Verify containers are running
docker compose ps

# Expected output:
# NAME                   STATUS
# rag_api-main-api-1     Up
# rag_api-main-db-1      Up
```

---

### Step 2: Verify RAG API is Accessible

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

---

### Step 3: Upload Test Document

```bash
# Upload the comprehensive test document
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"

# Expected output:
# {
#   "message": "File uploaded and indexed successfully",
#   "file_id": "security-manual-001",
#   "chunks": 156
# }
```

**Verify upload worked:**

```bash
# Test a query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the security policy?",
    "file_id": "security-manual-001",
    "k": 3
  }'

# Should return relevant document chunks
```

---

### Step 4: Run Red Team Tests

#### **Option A: Quick Test (Custom Plugins)**

```bash
python3 test_docker_rag.py
```

**What it does:**
- Tests 5 custom plugins
- Generates HTML, JSON, and text reports
- Takes ~2-3 minutes

**Output files:**
- `docker_red_team_report.html` - Visual report
- `docker_red_team_report.json` - Machine-readable
- `docker_red_team_report.txt` - Text summary

**View report:**
```bash
# Linux
xdg-open docker_red_team_report.html

# macOS
open docker_red_team_report.html
```

---

#### **Option B: Built-in Plugins (Recommended)**

```bash
python3 examples/test_builtin_plugins.py
```

**Interactive menu:**
```
Select an example to run:
  1. Built-in PII plugins only
  2. Built-in harmful content plugins only
  3. Built-in security plugins only
  4. Mixed custom + built-in plugins (recommended) ⭐
  5. ALL 16 built-in plugins (comprehensive)
  0. Run all examples sequentially

Enter your choice (0-5):
```

**Recommended:** Choose **4** for mixed testing

**Run directly:**
```bash
# Run option 4 directly
python3 examples/test_builtin_plugins.py 4
```

**Output:**
- `mixed_comprehensive_report.html`
- `mixed_comprehensive_report.json`

---

#### **Option C: YAML Configuration**

**Test with PII config:**
```python
# test_with_yaml.py
import asyncio
from promptfoo_integration import RedTeamRunner
from promptfoo_integration.core.config import ConfigLoader
from promptfoo_integration.red_team.plugins import PluginManager
from test_docker_rag import query_docker_rag

async def main():
    # Load built-in plugins
    PluginManager.register_promptfoo_builtin_plugins()

    # Load YAML config
    config = ConfigLoader.load_from_yaml(
        "examples/config_examples/builtin_pii_config.yaml"
    )

    # Set query function
    config.target.config["query_fn"] = query_docker_rag

    # Run tests
    runner = RedTeamRunner(config)
    results = await runner.run_assessment()

    # Generate report
    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="pii_test.html")
    generator.print_summary()

asyncio.run(main())
```

**Run:**
```bash
python3 test_with_yaml.py
```

---

#### **Option D: Automated Complete Test**

```bash
# Make script executable
chmod +x run_complete_test.sh

# Run everything
./run_complete_test.sh
```

**What it does:**
1. Checks Docker is running
2. Verifies API is accessible
3. Uploads document (if needed)
4. Runs comprehensive tests
5. Generates all reports

---

### Step 5: Review Results

#### **HTML Report:**

```bash
xdg-open docker_red_team_report.html
```

**Report sections:**
1. **Executive Summary** - Total tests, vulnerabilities, success rate
2. **Severity Breakdown** - Critical/High/Medium/Low counts
3. **Detailed Results** - Each test with input, output, vulnerability
4. **Recommendations** - Suggested fixes

#### **JSON Report (Programmatic Analysis):**

```python
import json

with open('docker_red_team_report.json', 'r') as f:
    results = json.load(f)

print(f"Total tests: {results['total_tests']}")
print(f"Vulnerabilities: {results['vulnerabilities_found']}")
print(f"Success rate: {results['attack_success_rate']}%")

# Find critical issues
critical = [r for r in results['test_results']
            if r['is_vulnerable'] and r['severity'] == 'critical']

print(f"\nCritical vulnerabilities: {len(critical)}")
for vuln in critical:
    print(f"- {vuln['explanation']}")
```

---

## 📊 Understanding Results

### Attack Success Rate

```
0-20%:   ✅ Excellent security (system is well-protected)
21-40%:  ⚠️  Good (minor improvements needed)
41-60%:  ⚠️  Significant vulnerabilities (fix high priority items)
61-80%:  🚨 Major concerns (immediate action required)
81-100%: 🚨 Critical (system is highly vulnerable)
```

### Severity Levels

| Severity | Risk | Action | Examples |
|----------|------|--------|----------|
| **Critical** | Immediate security breach | Fix before production | PII leakage, injection success |
| **High** | Significant vulnerability | Fix this sprint | RBAC bypass, harmful content |
| **Medium** | Moderate risk | Schedule fix | Hallucination, competitor mentions |
| **Low** | Minor issue | Monitor | Edge cases, rare scenarios |

---

## 🎯 Common Testing Scenarios

### Scenario 1: PII Compliance Check

```bash
# Use PII-specific YAML config
python3 << 'EOF'
import asyncio
from promptfoo_integration import RedTeamRunner
from promptfoo_integration.core.config import ConfigLoader
from promptfoo_integration.red_team.plugins import PluginManager
from test_docker_rag import query_docker_rag

async def main():
    PluginManager.register_promptfoo_builtin_plugins()
    config = ConfigLoader.load_from_yaml(
        "examples/config_examples/builtin_pii_config.yaml"
    )
    config.target.config["query_fn"] = query_docker_rag

    runner = RedTeamRunner(config)
    results = await runner.run_assessment()

    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="pii_compliance.html")
    generator.print_summary()

asyncio.run(main())
EOF
```

---

### Scenario 2: Content Safety Check

```bash
# Use harmful content YAML config
# Similar pattern with builtin_harmful_config.yaml
```

---

### Scenario 3: Complete Security Audit

```bash
# Use comprehensive YAML config
python3 examples/test_builtin_plugins.py 5
```

---

## 🔧 Troubleshooting

### Issue: "Connection refused"

**Problem:** Can't connect to `http://localhost:8000`

**Solution:**
```bash
# Check if containers are running
docker compose ps

# If not running
docker compose up -d

# Check logs
docker compose logs api

# Verify API
curl http://localhost:8000/health
```

---

### Issue: "File not found for file_id"

**Problem:** Document not uploaded

**Solution:**
```bash
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"
```

---

### Issue: Import errors

**Problem:** `ModuleNotFoundError: No module named 'promptfoo_integration'`

**Solution:**
```bash
# Ensure correct directory
cd ~/tech_demo_fake/rag_api-main

# Install dependencies
pip3 install -r requirements.txt

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📁 Quick Reference

### Directory Structure
```
rag_api-main/
├── promptfoo_integration/          ← Main package
│   ├── core/                       ← Shared
│   ├── red_team/                   ← Security testing ✅
│   ├── evaluations/                ← Quality (future)
│   └── guardrails/                 ← Safety (future)
│
├── examples/
│   ├── test_builtin_plugins.py     ← Built-in plugin examples
│   └── config_examples/            ← YAML configurations
│       ├── builtin_pii_config.yaml
│       ├── builtin_harmful_config.yaml
│       ├── builtin_security_config.yaml
│       ├── builtin_brand_config.yaml
│       └── builtin_comprehensive_config.yaml
│
└── test_docker_rag.py              ← Quick test script
```

### Quick Commands
```bash
# Start
docker compose up -d

# Upload
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"

# Test (quick)
python3 test_docker_rag.py

# Test (comprehensive)
python3 examples/test_builtin_plugins.py 4

# View
xdg-open docker_red_team_report.html

# Stop
docker compose down
```

---

## ✅ Summary

You now have:

✅ **Modular architecture** ready for future modules (guardrails, evaluations)

✅ **21 plugins** (5 custom + 16 Promptfoo built-in)

✅ **6 YAML configurations** for different testing scenarios

✅ **Easy integration** with any Python LLM application

✅ **Complete documentation** with step-by-step instructions

✅ **Production-ready** security testing framework

**Start testing now:**
```bash
python3 examples/test_builtin_plugins.py 4
```

---

## 📚 Documentation Index

- **COMPLETE_GUIDE.md** (this file) - Architecture, why, and how to run
- **HOW_TO_RUN.md** - Detailed local setup steps
- **ARCHITECTURE_GUIDE.md** - Deep dive into modular design
- **YAML_CONFIGS_GUIDE.md** - All YAML configuration files
- **PROMPTFOO_SETUP.md** - Promptfoo integration details
- **QUICK_START_PROMPTFOO.md** - Quick reference

---

**You're ready to run comprehensive security testing with modular architecture!** 🎉
