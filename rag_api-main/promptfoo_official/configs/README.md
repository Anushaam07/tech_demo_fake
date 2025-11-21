# Promptfoo Configuration Files

This directory contains official Promptfoo configuration files for different red teaming scenarios.

## Available Configurations

### 1. `promptfooconfig.yaml` - Comprehensive Testing (Recommended)
**Use case:** Complete security assessment covering all areas

**What it tests:**
- PII detection (15 tests)
- Harmful content (40 tests)
- Security vulnerabilities (55 tests)
- Brand protection (34 tests)
- Hallucination (15 tests)

**Total:** ~159 tests

**Run:**
```bash
cd promptfoo_official
promptfoo eval -c configs/promptfooconfig.yaml
```

---

### 2. `pii_compliance.yaml` - PII Compliance Testing
**Use case:** GDPR, CCPA, HIPAA compliance verification

**What it tests:**
- Credit cards, SSN, bank accounts
- Email, phone, addresses
- Medical records, health insurance
- Government IDs (passport, driver's license)

**Total:** ~30 tests

**Run:**
```bash
cd promptfoo_official
promptfoo eval -c configs/pii_compliance.yaml
```

---

### 3. `security_vulnerabilities.yaml` - OWASP Security Testing
**Use case:** Security vulnerability assessment (OWASP LLM Top 10)

**What it tests:**
- Prompt injection (OWASP LLM01)
- Shell injection
- SQL injection (OWASP API8)
- RBAC violations (OWASP API1)
- Debug access

**Total:** ~100 tests

**Run:**
```bash
cd promptfoo_official
promptfoo eval -c configs/security_vulnerabilities.yaml
```

---

### 4. `harmful_content.yaml` - Trust & Safety Testing
**Use case:** Content safety and toxicity prevention

**What it tests:**
- Hate speech
- Harassment/bullying
- Violence/terrorism
- Privacy violations
- Unsafe advice (medical, legal, financial)
- CBRN threats
- Cybercrime

**Total:** ~102 tests

**Run:**
```bash
cd promptfoo_official
promptfoo eval -c configs/harmful_content.yaml
```

---

### 5. `brand_protection.yaml` - Brand Safety Testing
**Use case:** Protect brand reputation and prevent unauthorized commitments

**What it tests:**
- Competitor mentions
- Unauthorized contracts
- Excessive agency
- Over-reliance risks
- Hallucination (brand risk)

**Total:** ~80 tests

**Run:**
```bash
cd promptfoo_official
promptfoo eval -c configs/brand_protection.yaml
```

---

## Quick Start

### Prerequisites
1. Install Promptfoo:
```bash
npm install -g promptfoo
```

2. Ensure RAG API is running:
```bash
docker compose up -d
```

3. Navigate to promptfoo_official directory:
```bash
cd promptfoo_official
```

### Run Tests

**Option 1: Comprehensive testing**
```bash
promptfoo eval -c configs/promptfooconfig.yaml
```

**Option 2: Specific testing**
```bash
# PII compliance
promptfoo eval -c configs/pii_compliance.yaml

# Security vulnerabilities
promptfoo eval -c configs/security_vulnerabilities.yaml

# Harmful content
promptfoo eval -c configs/harmful_content.yaml

# Brand protection
promptfoo eval -c configs/brand_protection.yaml
```

### View Results

```bash
# Open web UI
promptfoo view

# Or open results directory
cd results/latest
```

---

## Configuration Selection Guide

| Need | Configuration File | Tests | Time |
|------|-------------------|-------|------|
| Quick audit | `promptfooconfig.yaml` | 159 | ~5 min |
| PII compliance | `pii_compliance.yaml` | 30 | ~1 min |
| Security audit | `security_vulnerabilities.yaml` | 100 | ~3 min |
| Safety check | `harmful_content.yaml` | 102 | ~3 min |
| Brand safety | `brand_protection.yaml` | 80 | ~2 min |

---

## Customizing Configurations

### Add your own competitors
Edit `brand_protection.yaml`:
```yaml
- id: competitors
  config:
    competitors:
      - "Your Competitor 1"
      - "Your Competitor 2"
```

### Adjust test count
```yaml
redteam:
  numTests: 20  # Increase for more comprehensive testing
```

### Add custom roles for RBAC
Edit `security_vulnerabilities.yaml`:
```yaml
- id: rbac
  config:
    roles:
      - admin
      - user
      - custom_role_here
```

---

## Environment Variables

Configure the provider by setting environment variables:

```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
```

Or modify in configuration files:
```yaml
providers:
  - id: python:./promptfoo_official/providers/rag_provider.py
    config:
      env:
        RAG_API_ENDPOINT: "http://your-api:8000/query"
        RAG_FILE_ID: "your-file-id"
        RAG_K: "10"
```

---

## Results Output

All test results are saved to:
```
promptfoo_official/results/
├── latest/              # Latest test run
├── pii_compliance/      # PII test results
├── security_vulns/      # Security test results
├── harmful_content/     # Safety test results
└── brand_protection/    # Brand test results
```

Each result directory contains:
- `results.json` - Detailed test results
- `summary.txt` - Quick summary
- HTML report (if configured)

---

## Official Promptfoo Plugins Used

### PII Plugins
- `pii` - PII detection and leakage

### Harmful Content Plugins
- `harmful:hate` - Hate speech
- `harmful:harassment-bullying` - Harassment
- `harmful:violent-crime` - Violence
- `harmful:privacy` - Privacy violations
- `harmful:specialized-advice` - Unsafe advice
- `harmful:chemical-biological-weapons` - CBRN
- `harmful:cybercrime` - Cybercrime

### Security Plugins
- `prompt-injection` - Prompt injection attacks
- `shell-injection` - Shell injection
- `sql-injection` - SQL injection
- `debug-access` - Debug/system access
- `rbac` - Access control violations

### Brand & Trust Plugins
- `competitors` - Competitor mentions
- `contracts` - Unauthorized commitments
- `excessive-agency` - Overstepping boundaries
- `overreliance` - Over-reliance risks

### Other
- `hallucination` - Factual accuracy

---

## Related Documentation

- **../providers/README.md** - Provider bridge explanation
- **../scripts/README.md** - Helper scripts
- **../INTEGRATION_GUIDE.md** - Complete integration guide
