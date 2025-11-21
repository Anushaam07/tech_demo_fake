# Official Promptfoo Integration Guide

Complete guide for integrating Promptfoo red teaming with RAG API and other LLM applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Folder Structure](#folder-structure)
4. [How Everything Works](#how-everything-works)
5. [Quick Start](#quick-start)
6. [Detailed Usage](#detailed-usage)
7. [Integration with Other LLM Applications](#integration-with-other-llm-applications)
8. [Comparison: Our Python Implementation vs Official Promptfoo](#comparison)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What is This Integration?

This integration brings **official Promptfoo** red teaming capabilities to your RAG application. It provides:

- **Official Promptfoo CLI** - Industry-standard red teaming tool with 100+ built-in plugins
- **Python Provider Bridge** - Connects Promptfoo to Python-based LLM applications
- **Pre-configured Test Suites** - Ready-to-use configurations for different security scenarios
- **Helper Scripts** - Simplified testing workflow
- **Comprehensive Documentation** - Clear guidance for setup and customization

### Why Use Official Promptfoo?

**Official Promptfoo** (this integration):
- ✅ 100+ battle-tested plugins maintained by security experts
- ✅ Regular updates with latest attack vectors
- ✅ Industry standard used by major companies
- ✅ Web UI for results visualization
- ✅ Active community and support
- ✅ Compliance framework alignment (OWASP, NIST)

**Our Python Implementation** (already in codebase):
- ✅ No Node.js dependency
- ✅ Pure Python integration
- ✅ Custom plugins for domain-specific testing
- ✅ Direct API integration
- ✅ Easier to modify and extend

**Recommendation:** Use **both**:
- **Official Promptfoo** for comprehensive industry-standard testing
- **Python implementation** for custom domain-specific tests

---

## Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Promptfoo Red Team Suite                     │
│                         (Node.js)                               │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ PII Plugins  │  │   Harmful    │  │   Security   │         │
│  │   (4)        │  │  Plugins (7) │  │  Plugins (5) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │    Brand     │  │     Other    │                            │
│  │  Plugins (4) │  │  Plugins     │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────────────────────────────────────────────────────────┘
                           │
                           │ Calls provider script
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              Python Provider Bridge (This Layer)                │
│                                                                  │
│  ┌─────────────────────┐   ┌──────────────────────┐           │
│  │  rag_provider.py    │   │ rag_provider_async.py│           │
│  │  (Sync)             │   │  (Async)             │           │
│  └─────────────────────┘   └──────────────────────┘           │
└────────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP POST requests
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                     Your LLM Application                        │
│                    (RAG API - FastAPI)                          │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │   Retrieval  │──▶│  LLM Model   │──▶│   Response   │       │
│  │   (Vector DB)│   │  Generation  │   │   Formatting │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
└────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Promptfoo** generates adversarial prompt
2. **Promptfoo** calls Python provider with prompt
3. **Provider** forwards prompt to RAG API via HTTP
4. **RAG API** queries vector database for relevant context
5. **RAG API** sends context + query to LLM
6. **LLM** generates response
7. **RAG API** returns response to provider
8. **Provider** formats response as JSON for Promptfoo
9. **Promptfoo** evaluates response against security criteria
10. **Promptfoo** logs results and generates report

---

## Folder Structure

```
promptfoo_official/
├── configs/                          # Promptfoo YAML configurations
│   ├── promptfooconfig.yaml          # Main comprehensive config
│   ├── pii_compliance.yaml           # PII testing (GDPR, CCPA, HIPAA)
│   ├── security_vulnerabilities.yaml # OWASP security testing
│   ├── harmful_content.yaml          # Content safety testing
│   ├── brand_protection.yaml         # Brand safety testing
│   └── README.md                     # Config documentation
│
├── providers/                        # Python provider bridges
│   ├── rag_provider.py               # Sync provider
│   ├── rag_provider_async.py         # Async provider (recommended)
│   └── README.md                     # Provider documentation
│
├── scripts/                          # Helper scripts
│   ├── setup.sh                      # Initial setup
│   ├── test_provider.sh              # Test provider connection
│   ├── run_single_test.sh            # Run individual tests
│   ├── run_all_tests.sh              # Run complete test suite
│   └── README.md                     # Scripts documentation
│
├── results/                          # Test results (created automatically)
│   ├── latest/                       # Latest test run
│   ├── pii_compliance/               # PII test results
│   ├── security_vulns/               # Security test results
│   ├── harmful_content/              # Safety test results
│   └── brand_protection/             # Brand test results
│
├── plugins/                          # Custom Promptfoo plugins (optional)
│   └── (your custom plugins here)
│
├── INTEGRATION_GUIDE.md              # This document
└── HOW_TO_RUN.md                     # Quick start guide
```

### Where is What?

| Component | Location | Purpose |
|-----------|----------|---------|
| **Test Configurations** | `configs/*.yaml` | Define what to test and how |
| **Provider Bridge** | `providers/*.py` | Connect Promptfoo to your API |
| **Helper Scripts** | `scripts/*.sh` | Simplify testing workflow |
| **Test Results** | `results/` | Store test outputs |
| **Documentation** | `*.md files` | Guides and references |

---

## How Everything Works

### 1. Configuration Files (configs/)

**Purpose:** Define test scenarios

**What they contain:**
- Which plugins to use (PII, harmful, security, etc.)
- Number of tests per plugin
- Attack strategies (jailbreak, base64, etc.)
- Provider configuration
- Output settings

**Example:**
```yaml
# configs/pii_compliance.yaml
description: "PII compliance testing"

providers:
  - id: python:./promptfoo_official/providers/rag_provider.py
    config:
      env:
        RAG_API_ENDPOINT: "http://localhost:8000/query"

redteam:
  numTests: 20
  plugins:
    - id: pii
      numTests: 30
      config:
        piiTypes:
          - credit-card
          - ssn
          - email

outputPath: "./promptfoo_official/results/pii_compliance"
```

**How Promptfoo uses it:**
1. Reads configuration file
2. Loads specified plugins
3. Generates test cases using plugins
4. Calls provider for each test
5. Evaluates responses
6. Saves results to outputPath

---

### 2. Provider Bridge (providers/)

**Purpose:** Connect Promptfoo (Node.js) to your LLM app (Python)

**How it works:**

```python
# providers/rag_provider.py

def main():
    # 1. Get prompt from Promptfoo (command line argument)
    prompt = sys.argv[1]

    # 2. Forward to RAG API
    response = requests.post(
        "http://localhost:8000/query",
        json={"question": prompt, "file_id": "security-manual-001", "k": 4}
    )

    # 3. Format response for Promptfoo
    result = {
        "output": response.json()["answer"],
        "metadata": {"sources": response.json()["sources"]}
    }

    # 4. Return JSON to Promptfoo
    print(json.dumps(result))
```

**Why needed:**
- Promptfoo is Node.js, your app is Python
- Provider translates between them
- Allows Promptfoo to test any Python LLM application

---

### 3. Helper Scripts (scripts/)

**Purpose:** Simplify testing workflow

| Script | What It Does | When to Use |
|--------|--------------|-------------|
| `setup.sh` | Install dependencies, verify setup | First time, troubleshooting |
| `test_provider.sh` | Test provider connection | Before running tests |
| `run_single_test.sh` | Run specific test suite | Targeted testing |
| `run_all_tests.sh` | Run all test suites | Comprehensive audit |

**Example usage:**
```bash
cd promptfoo_official/scripts

# First time
./setup.sh

# Test connection
./test_provider.sh

# Run PII tests
./run_single_test.sh pii

# Run everything
./run_all_tests.sh
```

---

### 4. Test Results (results/)

**Purpose:** Store test outputs

**What's created:**
- `results.json` - Detailed test results
- `summary.txt` - Quick summary
- `report.html` - Web-based report (if configured)

**Structure:**
```
results/
├── latest/           # Symlink to most recent test
├── pii_compliance/
│   ├── results.json
│   └── summary.txt
├── security_vulns/
│   ├── results.json
│   └── summary.txt
└── ...
```

**Viewing results:**
```bash
# Web UI (recommended)
promptfoo view

# Command line
cat results/latest/summary.txt

# JSON
jq . results/latest/results.json
```

---

## Quick Start

### Prerequisites

1. **Node.js and npm**
```bash
node --version  # Should be v16+
npm --version
```

2. **Promptfoo CLI**
```bash
npm install -g promptfoo
```

3. **Python dependencies**
```bash
pip3 install requests aiohttp
```

4. **RAG API running**
```bash
docker compose up -d
curl http://localhost:8000/health
```

---

### Step 1: Setup

```bash
cd promptfoo_official/scripts
./setup.sh
```

This script:
- Checks all dependencies
- Installs Promptfoo if needed
- Verifies RAG API is accessible
- Sets up provider scripts

---

### Step 2: Test Provider Connection

```bash
./test_provider.sh
```

Expected output:
```json
{
  "output": "Docker is a platform for developing...",
  "metadata": {
    "sources": [...],
    "file_id": "security-manual-001"
  }
}
```

---

### Step 3: Run Your First Test

```bash
# Run PII compliance tests
./run_single_test.sh pii
```

This will:
1. Check prerequisites
2. Run 30 PII-specific tests
3. Save results to `results/pii_compliance/`
4. Show summary

---

### Step 4: View Results

```bash
# Option 1: Web UI (recommended)
promptfoo view

# Option 2: Command line
cat ../results/pii_compliance/summary.txt

# Option 3: JSON
jq . ../results/pii_compliance/results.json
```

---

## Detailed Usage

### Running Different Test Scenarios

#### PII Compliance Testing
```bash
./run_single_test.sh pii
```
**Tests:** 30 tests covering credit cards, SSN, email, phone, medical records
**Time:** ~1 minute
**Use case:** GDPR, CCPA, HIPAA compliance verification

---

#### Security Vulnerability Testing
```bash
./run_single_test.sh security
```
**Tests:** 100 tests covering prompt injection, SQL injection, shell injection, RBAC
**Time:** ~3 minutes
**Use case:** OWASP LLM Top 10 compliance

---

#### Harmful Content Testing
```bash
./run_single_test.sh harmful
```
**Tests:** 102 tests covering hate speech, harassment, violence, unsafe advice
**Time:** ~3 minutes
**Use case:** Trust & Safety compliance

---

#### Brand Protection Testing
```bash
./run_single_test.sh brand
```
**Tests:** 80 tests covering competitor mentions, unauthorized commitments
**Time:** ~2 minutes
**Use case:** Brand reputation protection

---

#### Comprehensive Testing
```bash
./run_single_test.sh comprehensive
```
**Tests:** 159 tests covering all categories
**Time:** ~5 minutes
**Use case:** Pre-deployment security audit

---

### Running All Tests

```bash
./run_all_tests.sh
```

**Runs in order:**
1. PII compliance
2. Security vulnerabilities
3. Harmful content
4. Brand protection
5. Comprehensive test

**Total time:** ~15-20 minutes

**Use case:** Complete security assessment before major deployment

---

### Customizing Tests

#### Adjust Number of Tests

Edit config file (e.g., `configs/pii_compliance.yaml`):

```yaml
redteam:
  numTests: 50  # Increased from 20
  plugins:
    - id: pii
      numTests: 100  # Increased from 30
```

#### Add Your Competitors

Edit `configs/brand_protection.yaml`:

```yaml
plugins:
  - id: competitors
    config:
      competitors:
        - "Your Competitor 1"
        - "Your Competitor 2"
        - "Your Competitor 3"
```

#### Change Attack Strategies

Edit any config file:

```yaml
redteam:
  strategies:
    - jailbreak
    - prompt-injection
    - base64
    - rot13
    - leetspeak
    - multilingual     # Add new strategy
```

#### Test Different Documents

Set environment variable:

```bash
export RAG_FILE_ID="your-document-id"
./run_single_test.sh pii
```

Or edit config:

```yaml
providers:
  - id: python:./promptfoo_official/providers/rag_provider.py
    config:
      env:
        RAG_FILE_ID: "your-document-id"
```

---

## Integration with Other LLM Applications

This integration is **designed to work with any LLM application**. Here's how to adapt it:

### For OpenAI API

Create `providers/openai_provider.py`:

```python
#!/usr/bin/env python3
import sys
import json
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    prompt = sys.argv[1]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    result = {
        "output": response.choices[0].message.content,
        "metadata": {
            "model": response.model,
            "tokens": response.usage.total_tokens
        }
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

Update config:

```yaml
providers:
  - id: python:./promptfoo_official/providers/openai_provider.py
    config:
      env:
        OPENAI_API_KEY: "your-key-here"
```

---

### For Anthropic Claude API

Create `providers/claude_provider.py`:

```python
#!/usr/bin/env python3
import sys
import json
import os
import anthropic

def main():
    prompt = sys.argv[1]

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    result = {
        "output": response.content[0].text,
        "metadata": {
            "model": response.model,
            "stop_reason": response.stop_reason
        }
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

---

### For HuggingFace Models

Create `providers/huggingface_provider.py`:

```python
#!/usr/bin/env python3
import sys
import json
import os
from transformers import pipeline

# Load model once
generator = pipeline('text-generation', model='gpt2')

def main():
    prompt = sys.argv[1]

    response = generator(
        prompt,
        max_length=200,
        num_return_sequences=1
    )

    result = {
        "output": response[0]['generated_text'],
        "metadata": {
            "model": "gpt2"
        }
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

---

### For Local Models (Ollama)

Create `providers/ollama_provider.py`:

```python
#!/usr/bin/env python3
import sys
import json
import requests
import os

def main():
    prompt = sys.argv[1]
    model = os.getenv("OLLAMA_MODEL", "llama2")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    result = {
        "output": response.json()["response"],
        "metadata": {
            "model": model
        }
    }

    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

---

### For Any Custom API

**General template:**

```python
#!/usr/bin/env python3
import sys
import json
import requests
import os

def main():
    # 1. Get prompt from Promptfoo
    prompt = sys.argv[1]

    # 2. Get API configuration from environment
    api_endpoint = os.getenv("YOUR_API_ENDPOINT")
    api_key = os.getenv("YOUR_API_KEY")

    # 3. Call your API
    response = requests.post(
        api_endpoint,
        json={
            "prompt": prompt,
            # Add any other required fields
        },
        headers={
            "Authorization": f"Bearer {api_key}"
        }
    )

    # 4. Extract response
    data = response.json()
    output_text = data["your_response_field"]

    # 5. Format for Promptfoo
    result = {
        "output": output_text,
        "metadata": {
            # Add any relevant metadata
        }
    }

    # 6. Return JSON
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

**Then update config:**

```yaml
providers:
  - id: python:./promptfoo_official/providers/your_custom_provider.py
    config:
      env:
        YOUR_API_ENDPOINT: "https://your-api.com/generate"
        YOUR_API_KEY: "your-key"
```

---

## Comparison

### Our Python Implementation vs Official Promptfoo

| Feature | Python Implementation | Official Promptfoo |
|---------|----------------------|-------------------|
| **Installation** | None (pure Python) | Requires Node.js + npm |
| **Plugin Count** | 5 custom plugins | 100+ built-in plugins |
| **Maintenance** | Manual updates | Automatic updates from Promptfoo team |
| **Industry Standard** | Custom | Used by major companies |
| **Customization** | Very easy (Python) | Requires Node.js knowledge |
| **Web UI** | No | Yes (promptfoo view) |
| **Reports** | HTML | HTML + JSON + Web UI |
| **Performance** | Good | Excellent (optimized) |
| **Compliance** | Custom | OWASP, NIST aligned |
| **Community** | Internal | Large community |
| **API Integration** | Direct | Via provider bridge |

### When to Use Each

**Use Python Implementation:**
- Quick custom testing
- Domain-specific plugins
- No Node.js environment
- Tight Python integration
- Full control over plugin logic

**Use Official Promptfoo:**
- Comprehensive security audits
- Industry-standard compliance
- Latest attack vectors
- Professional reports
- Web-based result viewing
- Pre-deployment testing

**Use Both (Recommended):**
1. **Official Promptfoo** for general security testing
2. **Python implementation** for domain-specific tests

---

## Best Practices

### 1. Test Regularly

```bash
# Run quick test after each deployment
./run_single_test.sh pii

# Run comprehensive test weekly
./run_all_tests.sh
```

### 2. Start with Targeted Tests

Don't start with comprehensive testing. Build up:

```bash
# Week 1: PII
./run_single_test.sh pii

# Week 2: Security
./run_single_test.sh security

# Week 3: Harmful
./run_single_test.sh harmful

# Week 4: Comprehensive
./run_all_tests.sh
```

### 3. Review Results Thoroughly

```bash
# Don't just check if tests passed
# Review what was tested
promptfoo view

# Look for patterns in failures
jq '.tests[] | select(.pass == false)' results/latest/results.json
```

### 4. Customize for Your Domain

Add your specific:
- Competitors
- PII types
- Prohibited topics
- Brand guidelines

### 5. Integrate with CI/CD

```yaml
# .github/workflows/red-team.yml
name: Red Team Testing

on:
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  red-team:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install Promptfoo
        run: npm install -g promptfoo
      - name: Run Red Team Tests
        run: |
          cd promptfoo_official/scripts
          ./setup.sh
          ./run_all_tests.sh
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: red-team-results
          path: promptfoo_official/results/
```

### 6. Version Control Results

```bash
# .gitignore
promptfoo_official/results/*/

# But keep summaries
!promptfoo_official/results/*/summary.txt
```

---

## Troubleshooting

### Promptfoo Not Installed

**Error:** `command not found: promptfoo`

**Solution:**
```bash
cd promptfoo_official/scripts
./setup.sh
```

Or manually:
```bash
npm install -g promptfoo
```

---

### RAG API Not Accessible

**Error:** `RAG API is not accessible at http://localhost:8000`

**Solution:**
```bash
# Start Docker containers
docker compose up -d

# Check status
docker compose ps

# Test endpoint
curl http://localhost:8000/health
```

---

### Provider Test Failed

**Error:** Provider returns error or empty output

**Solutions:**

1. **Check environment variables:**
```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
```

2. **Verify document exists:**
```bash
curl http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "file_id": "security-manual-001", "k": 4}'
```

3. **Check provider script:**
```bash
python3 promptfoo_official/providers/rag_provider.py "test query"
```

---

### Tests Take Too Long

**Issue:** Tests running slower than expected

**Solutions:**

1. **Use async provider:**
```yaml
providers:
  - id: python:./promptfoo_official/providers/rag_provider_async.py
```

2. **Reduce test count:**
```yaml
redteam:
  numTests: 5  # Reduced from 10
```

3. **Run targeted tests:**
```bash
# Instead of comprehensive
./run_single_test.sh pii
```

---

### Permission Denied Errors

**Error:** `Permission denied` when running scripts

**Solution:**
```bash
cd promptfoo_official/scripts
chmod +x *.sh
chmod +x ../providers/*.py
```

---

## Next Steps

### For First-Time Users

1. ✅ Complete setup: `./setup.sh`
2. ✅ Test provider: `./test_provider.sh`
3. ✅ Run first test: `./run_single_test.sh pii`
4. ✅ View results: `promptfoo view`
5. ✅ Review documentation in each folder

### For Regular Users

1. Run tests before deployments
2. Review results weekly
3. Customize configurations for your needs
4. Integrate with CI/CD
5. Track vulnerabilities over time

### For Integration with Other Apps

1. Create custom provider (see examples above)
2. Update config to use your provider
3. Test with `test_provider.sh`
4. Run initial test suite
5. Customize plugins and strategies

---

## Related Documentation

- **configs/README.md** - All available test configurations
- **providers/README.md** - Provider implementation details
- **scripts/README.md** - Helper scripts reference
- **HOW_TO_RUN.md** - Quick start guide

---

## Support and Resources

### Official Promptfoo Resources
- Website: https://www.promptfoo.dev/
- Docs: https://www.promptfoo.dev/docs/intro/
- GitHub: https://github.com/promptfoo/promptfoo
- Community: https://discord.gg/promptfoo

### This Integration
- Issues: Report in your project repository
- Questions: Check documentation in each folder
- Customization: Modify configs and providers

---

**You now have complete Promptfoo red teaming integrated with your RAG application!** 🎉

Start testing with:
```bash
cd promptfoo_official/scripts
./run_single_test.sh pii
```
