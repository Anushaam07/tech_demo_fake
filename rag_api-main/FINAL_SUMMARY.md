# Modular Promptfoo Integration - Complete Summary

This document explains the modular architecture, where built-in plugins are located, why we designed it this way, and how to run everything locally.

---

## 📐 Current Modular Architecture

### Structure Overview

```
promptfoo_integration/              ← Main package (modular design)
│
├── core/                          ← Shared core (used by all modules)
│   ├── __init__.py
│   ├── types.py                   ← Common types, enums, models
│   ├── config.py                  ← YAML/JSON config loader
│   └── client.py                  ← Target clients (API, LangChain, Custom)
│
├── red_team/                      ← RED TEAM MODULE ✅ COMPLETE
│   ├── __init__.py
│   ├── plugins.py                 ← 5 custom plugins
│   ├── plugins_builtin.py         ← 16 Promptfoo built-in plugins ⭐ NEW
│   ├── strategies.py              ← 7 attack strategies
│   ├── runner.py                  ← Test orchestration
│   ├── grader.py                  ← Response evaluation
│   └── report.py                  ← Report generation (HTML/JSON/text)
│
├── evaluations/                   ← EVALUATIONS MODULE (ready for future)
│   └── __init__.py                ← Placeholder for quality testing
│
├── guardrails/                    ← GUARDRAILS MODULE (ready for future)
│   └── __init__.py                ← Placeholder for safety controls
│
└── utils/                         ← Shared utilities
    ├── __init__.py
    └── helpers.py
```

### Configuration Files

```
examples/config_examples/
├── red_team_config.yaml                    ← Mixed (custom + built-in)
├── builtin_pii_config.yaml                 ← PII compliance ⭐ NEW
├── builtin_harmful_config.yaml             ← Content safety ⭐ NEW
├── builtin_security_config.yaml            ← Security tests ⭐ NEW
├── builtin_brand_config.yaml               ← Brand protection ⭐ NEW
├── builtin_comprehensive_config.yaml       ← All 19 plugins ⭐ NEW
└── compliance_preset_config.yaml           ← Compliance frameworks
```

---

## 🔌 Where Are the Built-in Plugins?

### Location: `promptfoo_integration/red_team/plugins_builtin.py` ⭐

This file contains **16 Promptfoo official built-in plugins**:

**PII Plugins (4):**
```python
class PIIDirectPlugin(BasePlugin):
    """Plugin ID: pii:direct"""
    # Tests direct PII leakage

class PIIAPIDBPlugin(BasePlugin):
    """Plugin ID: pii:api-db"""
    # Tests database/API PII exposure

class PIISessionPlugin(BasePlugin):
    """Plugin ID: pii:session"""
    # Tests cross-session leakage

class PIISocialPlugin(BasePlugin):
    """Plugin ID: pii:social"""
    # Tests social engineering
```

**Harmful Content Plugins (5):**
```python
class HarmfulHatePlugin(BasePlugin):
    """Plugin ID: harmful:hate"""

class HarmfulHarassmentPlugin(BasePlugin):
    """Plugin ID: harmful:harassment-bullying"""

class HarmfulViolentCrimePlugin(BasePlugin):
    """Plugin ID: harmful:violent-crime"""

class HarmfulPrivacyPlugin(BasePlugin):
    """Plugin ID: harmful:privacy"""

class HarmfulSpecializedAdvicePlugin(BasePlugin):
    """Plugin ID: harmful:specialized-advice"""
```

**Security Plugins (3):**
```python
class ShellInjectionPlugin(BasePlugin):
    """Plugin ID: shell-injection"""

class DebugAccessPlugin(BasePlugin):
    """Plugin ID: debug-access"""

class RBACPlugin(BasePlugin):
    """Plugin ID: rbac"""
```

**Brand & Trust Plugins (4):**
```python
class CompetitorsPlugin(BasePlugin):
    """Plugin ID: competitors"""

class ContractsPlugin(BasePlugin):
    """Plugin ID: contracts"""

class ExcessiveAgencyPlugin(BasePlugin):
    """Plugin ID: excessive-agency"""

class OverreliancePlugin(BasePlugin):
    """Plugin ID: overreliance"""
```

### How to Load Built-in Plugins

```python
from promptfoo_integration.red_team.plugins import PluginManager

# Load all Promptfoo built-in plugins
PluginManager.register_promptfoo_builtin_plugins()

# Now you have 21 plugins total:
# - 5 custom plugins (always available)
# - 16 Promptfoo built-in plugins (loaded)
```

---

## 🎯 Why This Modular Approach?

### 1. **Separation of Concerns**

Each module has ONE clear responsibility:

```
red_team/      → Security testing (vulnerabilities, penetration testing)
evaluations/   → Quality assessment (accuracy, relevance, coherence)
guardrails/    → Safety controls (input filters, output validators)
core/          → Shared infrastructure (config, clients, types)
```

**Benefits:**
- ✅ Changes in one module don't affect others
- ✅ Test each module independently
- ✅ Debug issues faster
- ✅ Easier to understand and maintain

---

### 2. **Easy Integration with ANY LLM Application**

The modular design works with any Python LLM app:

```python
# Works with Langchain
from langchain.chains import RetrievalQA
target = TargetConfig(type="langchain", config={"chain": qa_chain})

# Works with OpenAI
def query_openai(prompt): ...
target = TargetConfig(type="custom", config={"query_fn": query_openai})

# Works with your RAG API
def query_docker_rag(prompt): ...
target = TargetConfig(type="custom", config={"query_fn": query_docker_rag})

# Works with any FastAPI
def query_api(prompt): ...
target = TargetConfig(type="custom", config={"query_fn": query_api})
```

**Benefits:**
- ✅ One integration works everywhere
- ✅ No rewriting for each application
- ✅ Standardize security testing across organization
- ✅ Easy onboarding for new LLM apps

---

### 3. **Future-Proof for New Modules**

Adding new capabilities is simple:

```
TODAY:
promptfoo_integration/
├── red_team/          ← Security testing ✅ WORKING
├── evaluations/       ← Placeholder (ready to add)
└── guardrails/        ← Placeholder (ready to add)

TOMORROW (add evaluations):
├── evaluations/
│   ├── runner.py      ← Quality assessment
│   ├── metrics.py     ← Accuracy, relevance, coherence
│   └── benchmarks.py  ← Standard benchmarks

NEXT WEEK (add guardrails):
├── guardrails/
│   ├── validator.py   ← Input/output validation
│   ├── filters.py     ← Content filters
│   └── policies.py    ← Safety policies
```

**Benefits:**
- ✅ Add modules without breaking existing code
- ✅ Each module can be developed independently
- ✅ Version modules separately
- ✅ Pick and choose what you need

---

### 4. **Flexible Plugin System**

Mix custom and built-in plugins:

```python
config = PromptfooConfig(
    purpose="Comprehensive testing",
    target=your_target,
    plugins=[
        # Custom plugins (your specific needs)
        PluginType.PROMPT_INJECTION,
        PluginType.SQL_INJECTION,
        PluginType.HALLUCINATION,

        # Promptfoo built-in (industry-standard)
        "pii:direct",
        "pii:api-db",
        "harmful:hate",
        "harmful:violent-crime",
        "shell-injection",
        "rbac",
    ]
)
```

**Benefits:**
- ✅ Best of both worlds
- ✅ Custom plugins for domain-specific tests
- ✅ Built-in plugins for compliance
- ✅ Easy to add new plugins

---

### 5. **Configuration Flexibility**

Single YAML for all modules:

```yaml
# config.yaml

# Target (shared by all modules)
target:
  name: "my-rag-app"
  type: "custom"

# Red team module
red_team:
  plugins: ["pii:direct", "harmful:hate"]
  num_tests: 10

# Evaluations module (future)
evaluations:
  metrics: ["accuracy", "relevance"]

# Guardrails module (future)
guardrails:
  input_filters: ["pii_filter"]
  output_validators: ["harmful_check"]
```

**Benefits:**
- ✅ Single source of truth
- ✅ Version control friendly
- ✅ Share configs across team
- ✅ Environment-specific configs

---

## 📊 What You Have Now

### Total: 21 Plugins

**Custom Plugins (5) - Always Available:**
1. `prompt-injection` - Instruction override attacks
2. `sql-injection` - SQL injection vulnerabilities
3. `harmful-content` - Harmful content generation
4. `pii` - PII leakage
5. `hallucination` - Information fabrication

**Promptfoo Built-in PII Plugins (4) - Industry Standard:**
6. `pii:direct` - Direct PII requests
7. `pii:api-db` - Database/API PII exposure
8. `pii:session` - Cross-session leakage
9. `pii:social` - Social engineering attacks

**Promptfoo Built-in Harmful Content Plugins (5):**
10. `harmful:hate` - Hate speech generation
11. `harmful:harassment-bullying` - Harassment content
12. `harmful:violent-crime` - Violence instructions
13. `harmful:privacy` - Privacy violations
14. `harmful:specialized-advice` - Dangerous advice

**Promptfoo Built-in Security Plugins (3):**
15. `shell-injection` - Command injection
16. `debug-access` - Debug mode access
17. `rbac` - Access control bypass

**Promptfoo Built-in Brand & Trust Plugins (4):**
18. `competitors` - Competitor mentions
19. `contracts` - Unauthorized commitments
20. `excessive-agency` - Actions beyond scope
21. `overreliance` - Overconfident responses

### Attack Strategies (7)
- `jailbreak` - DAN, STAN jailbreak templates
- `base64` - Base64 encoding attacks
- `rot13` - ROT13 encoding attacks
- `leetspeak` - L33t sp34k obfuscation
- `multilingual` - Multi-language attacks
- `crescendo` - Gradual escalation attacks
- `prompt-injection` - Instruction override

---

## 🚀 How to Run Locally - Step by Step

### Prerequisites

```bash
# Verify Docker is installed
docker --version
docker compose version

# Verify Python 3.8+
python3 --version

# Navigate to project
cd ~/tech_demo_fake/rag_api-main
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

### Step 2: Verify RAG API

```bash
# Check health
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

---

### Step 3: Upload Test Document

```bash
# Upload comprehensive test document
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

**Verify upload:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the security policy?",
    "file_id": "security-manual-001",
    "k": 3
  }'
```

---

### Step 4: Run Tests

#### **Option A: Quick Test (Custom Plugins Only)**

```bash
python3 test_docker_rag.py
```

**Output:**
- `docker_red_team_report.html` - Visual report
- `docker_red_team_report.json` - Machine-readable
- `docker_red_team_report.txt` - Text summary

**View:**
```bash
xdg-open docker_red_team_report.html  # Linux
open docker_red_team_report.html      # macOS
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

Enter your choice (0-5): 4
```

**Or run directly:**
```bash
python3 examples/test_builtin_plugins.py 4
```

---

#### **Option C: YAML Configuration**

Create a test script:

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
        "examples/config_examples/builtin_comprehensive_config.yaml"
    )

    # Set query function
    config.target.config["query_fn"] = query_docker_rag

    # Run tests
    runner = RedTeamRunner(config)
    results = await runner.run_assessment()

    # Generate report
    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="comprehensive_test.html")
    generator.print_summary()

asyncio.run(main())
```

**Run:**
```bash
python3 test_with_yaml.py
xdg-open comprehensive_test.html
```

---

#### **Option D: Automated Complete Test**

```bash
chmod +x run_complete_test.sh
./run_complete_test.sh
```

---

### Step 5: Review Results

#### HTML Report Structure:
1. **Executive Summary** - Total tests, vulnerabilities, attack success rate
2. **Severity Breakdown** - Critical/High/Medium/Low counts
3. **Detailed Results** - Each test with input, output, vulnerability explanation
4. **Recommendations** - Suggested fixes

#### Analyze JSON Programmatically:
```python
import json

with open('docker_red_team_report.json', 'r') as f:
    results = json.load(f)

print(f"Total tests: {results['total_tests']}")
print(f"Vulnerabilities: {results['vulnerabilities_found']}")
print(f"Attack success rate: {results['attack_success_rate']}%")

# Find critical issues
critical = [r for r in results['test_results']
            if r['is_vulnerable'] and r['severity'] == 'critical']

print(f"\nCritical vulnerabilities: {len(critical)}")
for vuln in critical:
    print(f"  - {vuln['explanation']}")
```

---

## 🎯 Quick Testing Scenarios

### Scenario 1: PII Compliance Check

```bash
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
# Use builtin_harmful_config.yaml
# Similar pattern as above
```

---

### Scenario 3: Complete Security Audit

```bash
python3 examples/test_builtin_plugins.py 5
```

---

## 📁 Project Structure Summary

```
rag_api-main/
│
├── promptfoo_integration/          ← Main package (modular)
│   ├── core/                       ← Shared (config, types, clients)
│   ├── red_team/                   ← Security testing ✅
│   │   ├── plugins.py              ← 5 custom plugins
│   │   ├── plugins_builtin.py      ← 16 built-in plugins ⭐
│   │   ├── strategies.py           ← 7 strategies
│   │   ├── runner.py               ← Orchestration
│   │   ├── grader.py               ← Evaluation
│   │   └── report.py               ← Reports
│   ├── evaluations/                ← Quality testing (future)
│   └── guardrails/                 ← Safety controls (future)
│
├── examples/
│   ├── test_builtin_plugins.py     ← Examples with built-in plugins ⭐
│   └── config_examples/            ← YAML configs
│       ├── builtin_pii_config.yaml             ⭐
│       ├── builtin_harmful_config.yaml         ⭐
│       ├── builtin_security_config.yaml        ⭐
│       ├── builtin_brand_config.yaml           ⭐
│       └── builtin_comprehensive_config.yaml   ⭐
│
├── test_docker_rag.py              ← Quick test script
├── run_complete_test.sh            ← Automated test
│
└── Documentation/
    ├── COMPLETE_GUIDE.md           ← This file
    ├── ARCHITECTURE_GUIDE.md       ← Architecture deep dive
    ├── HOW_TO_RUN.md               ← Detailed setup
    ├── YAML_CONFIGS_GUIDE.md       ← YAML reference
    └── PROMPTFOO_SETUP.md          ← Promptfoo details
```

---

## 🔧 Troubleshooting

### "Connection refused"
```bash
docker compose up -d
curl http://localhost:8000/health
```

### "File not found"
```bash
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"
```

### "Module not found"
```bash
cd ~/tech_demo_fake/rag_api-main
pip3 install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## ✅ Quick Command Reference

```bash
# Start
docker compose up -d

# Upload
curl -X POST http://localhost:8000/embed-upload \
  -F "uploaded_file=@comprehensive_test_document.txt" \
  -F "file_id=security-manual-001"

# Test (quick)
python3 test_docker_rag.py

# Test (comprehensive with built-ins)
python3 examples/test_builtin_plugins.py 4

# View
xdg-open docker_red_team_report.html

# Stop
docker compose down
```

---

## 🎉 Summary

You now have a **complete, modular, production-ready** framework:

✅ **Modular architecture** - red_team/, evaluations/, guardrails/

✅ **21 plugins** - 5 custom + 16 Promptfoo built-in

✅ **6 YAML configs** - Ready for different scenarios

✅ **7 attack strategies** - Comprehensive testing

✅ **Easy integration** - Works with any Python LLM app

✅ **Future-proof** - Ready for evaluations & guardrails

✅ **Complete docs** - Architecture, setup, examples

**Start testing now:**
```bash
python3 examples/test_builtin_plugins.py 4
```

---

## 📚 Documentation Index

- **COMPLETE_GUIDE.md** (this file) - Everything explained
- **ARCHITECTURE_GUIDE.md** - Deep dive into modular design
- **HOW_TO_RUN.md** - Detailed local setup
- **YAML_CONFIGS_GUIDE.md** - All YAML configurations
- **PROMPTFOO_SETUP.md** - Promptfoo integration details

**All committed and ready to use!** 🚀
