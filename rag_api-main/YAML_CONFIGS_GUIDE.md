# YAML Configuration Files - Complete Reference

This document lists all available YAML configuration files with built-in Promptfoo plugins.

---

## 📁 Available Configuration Files

### 1. **red_team_config.yaml** - Mixed Testing (Recommended)
**Location:** `examples/config_examples/red_team_config.yaml`

**What it tests:**
- 3 Custom plugins
- 6 Promptfoo built-in plugins (PII, harmful, security)
- Mixed approach for comprehensive testing

**Plugins:**
```yaml
plugins:
  # Custom plugins
  - "prompt-injection"
  - "sql-injection"
  - "hallucination"

  # Built-in PII
  - "pii:direct"
  - "pii:api-db"
  - "pii:session"

  # Built-in harmful
  - "harmful:hate"
  - "harmful:privacy"

  # Built-in security
  - "rbac"
  - "shell-injection"
```

**Use when:** You want balanced testing with both custom and industry-standard plugins.

---

### 2. **builtin_pii_config.yaml** - PII Compliance Testing
**Location:** `examples/config_examples/builtin_pii_config.yaml`

**What it tests:**
- All 4 Promptfoo PII plugins
- PII compliance (GDPR, CCPA, HIPAA)

**Plugins:**
```yaml
plugins:
  - id: "pii:direct"
    config:
      piiTypes:
        - credit-card
        - ssn
        - email
        - phone
        - address

  - "pii:api-db"
  - "pii:session"
  - "pii:social"
```

**Use when:** You need to verify PII compliance and data protection.

---

### 3. **builtin_harmful_config.yaml** - Content Safety Testing
**Location:** `examples/config_examples/builtin_harmful_config.yaml`

**What it tests:**
- All 5 Promptfoo harmful content plugins
- Content safety and trust & safety compliance

**Plugins:**
```yaml
plugins:
  - "harmful:hate"
  - "harmful:harassment-bullying"
  - "harmful:violent-crime"
  - "harmful:privacy"
  - id: "harmful:specialized-advice"
    config:
      categories:
        - medical
        - legal
        - financial
```

**Use when:** You need to ensure your system doesn't generate harmful content.

---

### 4. **builtin_security_config.yaml** - Security Vulnerability Testing
**Location:** `examples/config_examples/builtin_security_config.yaml`

**What it tests:**
- All 3 Promptfoo security plugins
- OWASP compliance

**Plugins:**
```yaml
plugins:
  - "shell-injection"
  - "debug-access"
  - id: "rbac"
    config:
      roles:
        - admin
        - user
        - guest
```

**Use when:** You need to test for security vulnerabilities and access control.

---

### 5. **builtin_brand_config.yaml** - Brand Protection Testing
**Location:** `examples/config_examples/builtin_brand_config.yaml`

**What it tests:**
- All 4 Promptfoo brand & trust plugins
- Brand protection and commitment control

**Plugins:**
```yaml
plugins:
  - id: "competitors"
    config:
      competitors:
        - "CompetitorA"
        - "CompetitorB"

  - "contracts"
  - "excessive-agency"
  - "overreliance"
```

**Use when:** You need to protect brand reputation and prevent unauthorized commitments.

---

### 6. **builtin_comprehensive_config.yaml** - Complete Testing
**Location:** `examples/config_examples/builtin_comprehensive_config.yaml`

**What it tests:**
- 3 Custom plugins
- 16 Promptfoo built-in plugins
- ALL security, safety, and compliance areas

**Total:** 19 plugins

**Use when:** You need comprehensive security audit covering everything.

---

## 🚀 How to Use These Configurations

### Method 1: Direct Python Usage

```python
from promptfoo_integration import RedTeamRunner
from promptfoo_integration.core.config import ConfigLoader
from promptfoo_integration.red_team.plugins import PluginManager

# Load built-in plugins
PluginManager.register_promptfoo_builtin_plugins()

# Load configuration from YAML
config = ConfigLoader.load_from_yaml(
    "examples/config_examples/builtin_pii_config.yaml"
)

# Set query function (required - can't serialize functions in YAML)
from test_docker_rag import query_docker_rag
config.target.config["query_fn"] = query_docker_rag

# Run tests
runner = RedTeamRunner(config)
results = await runner.run_assessment()

# Generate report
from promptfoo_integration.red_team.report import ReportGenerator
generator = ReportGenerator(results)
generator.save_report(format="html", file_path="results.html")
```

---

### Method 2: Create Custom Test Script

**Example: PII Compliance Test**

```python
# test_pii_compliance.py
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

    # Generate reports
    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="pii_compliance.html")
    generator.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
```

**Run:**
```bash
python3 test_pii_compliance.py
```

---

## 📊 Plugin Coverage Summary

| Configuration File | Custom | PII | Harmful | Security | Brand | Total |
|-------------------|--------|-----|---------|----------|-------|-------|
| `red_team_config.yaml` | 3 | 3 | 2 | 2 | 0 | 10 |
| `builtin_pii_config.yaml` | 0 | 4 | 0 | 0 | 0 | 4 |
| `builtin_harmful_config.yaml` | 0 | 0 | 5 | 0 | 0 | 5 |
| `builtin_security_config.yaml` | 0 | 0 | 0 | 3 | 0 | 3 |
| `builtin_brand_config.yaml` | 0 | 0 | 0 | 0 | 4 | 4 |
| `builtin_comprehensive_config.yaml` | 3 | 4 | 5 | 3 | 4 | **19** |

---

## 🎯 Configuration Selection Guide

### Choose Based on Your Needs:

**For Quick Testing:**
- Use `red_team_config.yaml` (10 plugins, mixed approach)

**For Compliance Testing:**
- PII/GDPR: `builtin_pii_config.yaml`
- Content Safety: `builtin_harmful_config.yaml`
- Security: `builtin_security_config.yaml`

**For Specific Domain:**
- Brand Protection: `builtin_brand_config.yaml`

**For Complete Audit:**
- Use `builtin_comprehensive_config.yaml` (all 19 plugins)

---

## 🔧 Customizing Configurations

### Add Your Own Plugins

```yaml
plugins:
  # Existing built-in plugins
  - "pii:direct"
  - "harmful:hate"

  # Add custom plugin
  - "your-custom-plugin"
```

### Adjust Test Parameters

```yaml
# Run more tests per plugin
num_tests: 20  # Default is 10

# Add more strategies
strategies:
  - "jailbreak"
  - "base64"
  - "rot13"
  - "leetspeak"
  - "multilingual"
```

### Configure Plugin Options

```yaml
plugins:
  - id: "pii:direct"
    config:
      piiTypes:
        - credit-card
        - ssn
        - passport
        - driver-license  # Add custom PII types

  - id: "rbac"
    config:
      roles:
        - admin
        - superuser
        - moderator  # Add custom roles
```

---

## 📝 All Plugin IDs Reference

### Custom Plugins (Use as strings)
```yaml
- "prompt-injection"
- "sql-injection"
- "harmful-content"
- "pii"
- "hallucination"
```

### Promptfoo Built-in PII Plugins
```yaml
- "pii:direct"
- "pii:api-db"
- "pii:session"
- "pii:social"
```

### Promptfoo Built-in Harmful Content Plugins
```yaml
- "harmful:hate"
- "harmful:harassment-bullying"
- "harmful:violent-crime"
- "harmful:privacy"
- "harmful:specialized-advice"
```

### Promptfoo Built-in Security Plugins
```yaml
- "shell-injection"
- "debug-access"
- "rbac"
```

### Promptfoo Built-in Brand & Trust Plugins
```yaml
- "competitors"
- "contracts"
- "excessive-agency"
- "overreliance"
```

---

## ✅ Quick Start Commands

```bash
# 1. Test PII compliance
python3 -c "
import asyncio
from promptfoo_integration import RedTeamRunner
from promptfoo_integration.core.config import ConfigLoader
from promptfoo_integration.red_team.plugins import PluginManager
from test_docker_rag import query_docker_rag

async def test():
    PluginManager.register_promptfoo_builtin_plugins()
    config = ConfigLoader.load_from_yaml('examples/config_examples/builtin_pii_config.yaml')
    config.target.config['query_fn'] = query_docker_rag
    runner = RedTeamRunner(config)
    await runner.run_assessment()

asyncio.run(test())
"

# 2. Test harmful content
# (Similar pattern with builtin_harmful_config.yaml)

# 3. Comprehensive test
# (Similar pattern with builtin_comprehensive_config.yaml)
```

---

## 📚 Related Documentation

- **HOW_TO_RUN.md** - Step-by-step local setup
- **ARCHITECTURE_GUIDE.md** - Modular architecture explanation
- **PROMPTFOO_SETUP.md** - Complete Promptfoo integration guide

---

**All YAML configurations are ready to use with built-in Promptfoo plugins!** ✅
