# Promptfoo Integration - Modular Architecture Guide

This document explains the modular architecture of the Promptfoo integration, why we designed it this way, and how it makes future additions (guardrails, evaluations, model security) easy to integrate.

---

## 📐 Architecture Overview

### Directory Structure

```
promptfoo_integration/          ← Main package (modular design)
│
├── core/                       ← Core functionality (shared across modules)
│   ├── __init__.py
│   ├── types.py                ← Type definitions, enums, models
│   ├── config.py               ← Configuration management (YAML, JSON, dict)
│   └── client.py               ← Target client implementations (API, LangChain, Custom)
│
├── red_team/                   ← Red teaming module (security testing)
│   ├── __init__.py
│   ├── plugins.py              ← Custom plugins (5 core plugins)
│   ├── plugins_builtin.py      ← Promptfoo built-in plugins (16 plugins) ⭐ NEW
│   ├── strategies.py           ← Attack strategies (7 strategies)
│   ├── runner.py               ← Test orchestration and execution
│   ├── grader.py               ← Response evaluation (rule-based)
│   └── report.py               ← Report generation (HTML, JSON, text)
│
├── evaluations/                ← Evaluations module (future)
│   └── __init__.py             ← Placeholder for LLM evaluation features
│
├── guardrails/                 ← Guardrails module (future)
│   └── __init__.py             ← Placeholder for input/output guardrails
│
└── utils/                      ← Utilities (helpers, common functions)
    ├── __init__.py
    └── helpers.py              ← Shared utility functions
```

---

## 🎯 Why This Modular Design?

### 1. **Separation of Concerns**

Each module has a single, well-defined purpose:

```
red_team/      → Security testing (penetration testing, vulnerability scanning)
evaluations/   → Quality assessment (accuracy, relevance, coherence)
guardrails/    → Safety controls (input filtering, output validation)
core/          → Shared functionality (config, types, clients)
```

**Benefit:** Changes to one module don't affect others.

---

### 2. **Easy Integration with Other Applications**

The modular structure makes it simple to integrate individual components:

```python
# Option 1: Use only red teaming
from promptfoo_integration.red_team import RedTeamRunner

# Option 2: Use only evaluations (future)
from promptfoo_integration.evaluations import EvaluationRunner

# Option 3: Use only guardrails (future)
from promptfoo_integration.guardrails import GuardrailValidator

# Option 4: Use everything together
from promptfoo_integration import (
    RedTeamRunner,      # Security
    EvaluationRunner,   # Quality
    GuardrailValidator  # Safety
)
```

**Benefit:** Applications can pick and choose which modules they need.

---

### 3. **Independent Development & Testing**

Each module can be developed, tested, and updated independently:

```bash
# Test only red team module
pytest tests/red_team/

# Test only evaluations module (future)
pytest tests/evaluations/

# Test only guardrails module (future)
pytest tests/guardrails/
```

**Benefit:** Faster development cycles, easier debugging.

---

### 4. **Flexible Configuration**

The `core/` module provides shared configuration that all modules can use:

```yaml
# config.yaml
target:
  name: "my-rag-app"
  type: "api"
  endpoint: "http://localhost:8000/query"

red_team:                    # Red team specific config
  plugins: [...]
  strategies: [...]
  num_tests: 10

evaluations:                 # Evaluation specific config (future)
  metrics: [...]
  benchmarks: [...]

guardrails:                  # Guardrail specific config (future)
  input_filters: [...]
  output_validators: [...]
```

**Benefit:** Single configuration file for all modules.

---

### 5. **Extensibility**

New modules can be added without modifying existing code:

```
promptfoo_integration/
├── red_team/              ← Existing
├── evaluations/           ← Future (can add anytime)
├── guardrails/            ← Future (can add anytime)
├── model_security/        ← Future (new module - no code changes needed)
└── adversarial_testing/   ← Future (new module - no code changes needed)
```

**Benefit:** Grow functionality without technical debt.

---

## 🔌 Plugin Architecture: Custom vs Built-in

### Custom Plugins (plugins.py)

**5 Core Custom Plugins:**
- SQLInjectionPlugin
- PromptInjectionPlugin
- HarmfulContentPlugin
- PIIPlugin
- HallucinationPlugin

**Characteristics:**
- Designed specifically for your use case
- Customizable test cases
- Can be tailored to your domain

**Use when:** You need specialized tests for your specific application.

---

### Built-in Plugins (plugins_builtin.py) ⭐ NEW

**16 Promptfoo Official Plugins:**

**PII (4):**
- `pii:direct` - Direct PII leakage
- `pii:api-db` - Database/API PII exposure
- `pii:session` - Cross-session leakage
- `pii:social` - Social engineering

**Harmful Content (5):**
- `harmful:hate` - Hate speech
- `harmful:harassment-bullying` - Harassment
- `harmful:violent-crime` - Violence
- `harmful:privacy` - Privacy violations
- `harmful:specialized-advice` - Dangerous advice

**Security (3):**
- `shell-injection` - Command injection
- `debug-access` - Debug mode access
- `rbac` - Role-based access control

**Brand & Trust (4):**
- `competitors` - Competitor mentions
- `contracts` - Unauthorized commitments
- `excessive-agency` - Actions beyond scope
- `overreliance` - User over-reliance

**Characteristics:**
- Follow official Promptfoo specifications
- Industry-standard tests
- Compatible with official Promptfoo tool
- Comprehensive coverage

**Use when:** You want industry-standard security testing based on Promptfoo's proven methodology.

---

### Using Both Together (Recommended)

```python
from promptfoo_integration import PromptfooConfig
from promptfoo_integration.core.types import PluginType
from promptfoo_integration.red_team.plugins import PluginManager

# Load built-in plugins
PluginManager.register_promptfoo_builtin_plugins()

config = PromptfooConfig(
    purpose="Comprehensive testing",
    target=your_target,
    plugins=[
        # Custom plugins (use enum)
        PluginType.PROMPT_INJECTION,
        PluginType.SQL_INJECTION,

        # Built-in plugins (use string names)
        "pii:direct",
        "harmful:hate",
        "rbac",
    ]
)
```

**Benefit:** Get both customized and standardized testing in one assessment.

---

## 🏗️ How Modules Work Together

### Current Flow (Red Teaming Only)

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                     │
│                 (FastAPI RAG API)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Request
                     ▼
┌─────────────────────────────────────────────────────────┐
│              core/client.py                             │
│         (APITargetClient connects to your app)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Query function
                     ▼
┌─────────────────────────────────────────────────────────┐
│              red_team/runner.py                         │
│         (Orchestrates the testing process)              │
│                                                         │
│  1. Loads plugins (custom + built-in)                  │
│  2. Generates test cases                               │
│  3. Applies attack strategies                          │
│  4. Executes tests via client                          │
│  5. Collects responses                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Test results
                     ▼
┌─────────────────────────────────────────────────────────┐
│              red_team/grader.py                         │
│         (Evaluates responses for vulnerabilities)       │
│                                                         │
│  - Checks for PII patterns                             │
│  - Detects prompt injection success                    │
│  - Identifies harmful content                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Graded results
                     ▼
┌─────────────────────────────────────────────────────────┐
│              red_team/report.py                         │
│         (Generates reports: HTML, JSON, text)           │
└─────────────────────────────────────────────────────────┘
```

---

### Future Flow (All Modules)

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├──────────────┬──────────────┬───────────────┐
                     │              │              │               │
                     ▼              ▼              ▼               ▼
              ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
              │ red_team/  │ │evaluations/│ │guardrails/ │ │   core/    │
              │            │ │            │ │            │ │            │
              │ Security   │ │  Quality   │ │   Safety   │ │  Shared    │
              │  Testing   │ │ Assessment │ │  Controls  │ │  Config    │
              └────────────┘ └────────────┘ └────────────┘ └────────────┘
                     │              │              │               │
                     └──────────────┴──────────────┴───────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  Unified Report  │
                          │                  │
                          │  - Security ✓    │
                          │  - Quality ✓     │
                          │  - Safety ✓      │
                          └──────────────────┘
```

**Benefit:** Holistic LLM application testing from a single integration.

---

## 🚀 Future Module Examples

### Evaluations Module (Coming Soon)

```python
# promptfoo_integration/evaluations/runner.py

from promptfoo_integration.core.types import TargetConfig
from promptfoo_integration.core.client import PromptfooClient

class EvaluationRunner:
    """
    Evaluates LLM response quality.

    Metrics:
    - Accuracy (correctness)
    - Relevance (context alignment)
    - Coherence (logical flow)
    - Completeness (comprehensive answers)
    - Factuality (truthfulness)
    """

    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.client = PromptfooClient.create_target_client(config.target)

    async def run_evaluation(self):
        """Run quality evaluation."""
        # Generate test questions
        # Execute queries
        # Grade responses for quality metrics
        # Generate quality report
        pass
```

**Usage:**

```python
from promptfoo_integration.evaluations import EvaluationRunner, EvaluationConfig

config = EvaluationConfig(
    target=my_target,
    metrics=["accuracy", "relevance", "coherence"],
    benchmark="RAG-QA-Benchmark-v1"
)

runner = EvaluationRunner(config)
results = await runner.run_evaluation()
```

---

### Guardrails Module (Coming Soon)

```python
# promptfoo_integration/guardrails/validator.py

class GuardrailValidator:
    """
    Input/Output safety validation.

    Features:
    - Input filtering (malicious prompts, PII, harmful content)
    - Output validation (PII leakage, harmful content, policy compliance)
    - Real-time blocking
    - Logging and alerts
    """

    def __init__(self, config: GuardrailConfig):
        self.config = config
        self.input_filters = self._load_input_filters()
        self.output_validators = self._load_output_validators()

    def validate_input(self, prompt: str) -> ValidationResult:
        """Validate input prompt before sending to LLM."""
        pass

    def validate_output(self, response: str) -> ValidationResult:
        """Validate LLM response before returning to user."""
        pass
```

**Usage:**

```python
from promptfoo_integration.guardrails import GuardrailValidator

validator = GuardrailValidator(config)

# Before sending to LLM
input_result = validator.validate_input(user_prompt)
if not input_result.is_safe:
    return "Request blocked: " + input_result.reason

# After receiving from LLM
output_result = validator.validate_output(llm_response)
if not output_result.is_safe:
    return "Response filtered: " + output_result.reason
```

---

## 📦 Package Exports

The modular design allows clean imports:

```python
# promptfoo_integration/__init__.py

# Core exports (always available)
from promptfoo_integration.core.types import (
    PluginType,
    StrategyType,
    TargetConfig,
    TestCase,
    TestResult,
)
from promptfoo_integration.core.config import PromptfooConfig, ConfigLoader
from promptfoo_integration.core.client import PromptfooClient

# Red team exports (currently available)
from promptfoo_integration.red_team.runner import RedTeamRunner
from promptfoo_integration.red_team.plugins import PluginManager
from promptfoo_integration.red_team.report import ReportGenerator

# Future exports (when modules are added)
# from promptfoo_integration.evaluations import EvaluationRunner
# from promptfoo_integration.guardrails import GuardrailValidator
```

---

## 🎯 Why This Matters

### For Developers

✅ **Easy to understand** - Each module has clear boundaries
✅ **Easy to test** - Modules can be tested independently
✅ **Easy to extend** - Add new modules without breaking existing code
✅ **Easy to maintain** - Changes are localized to specific modules

### For Applications

✅ **Pick what you need** - Use only red team, or all modules
✅ **Flexible integration** - Works with any Python LLM application
✅ **Incremental adoption** - Start with red team, add evaluations/guardrails later
✅ **Production-ready** - Modular design supports scaling

### For Organizations

✅ **Standardization** - Consistent testing across all LLM applications
✅ **Compliance** - Built-in support for security frameworks (OWASP, NIST)
✅ **Reusability** - One integration, many applications
✅ **Future-proof** - Easy to add new capabilities as LLM security evolves

---

## 📊 Integration with Other Applications

### Example 1: Integrate with Langchain Application

```python
from langchain.chains import RetrievalQA
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig

# Your existing Langchain RAG
qa_chain = RetrievalQA.from_chain_type(...)

# Configure Promptfoo to test it
target = TargetConfig(
    name="langchain-rag",
    type="langchain",
    config={"chain": qa_chain}
)

config = PromptfooConfig(
    purpose="Langchain RAG security testing",
    target=target,
    plugins=["pii:direct", "harmful:hate", "prompt-injection"]
)

# Run tests
runner = RedTeamRunner(config)
results = await runner.run_assessment()
```

---

### Example 2: Integrate with OpenAI API

```python
from promptfoo_integration import RedTeamRunner, PromptfooConfig
from promptfoo_integration.core.types import TargetConfig

def query_openai(prompt: str, **kwargs) -> str:
    import openai
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
    purpose="OpenAI assistant security testing",
    target=target,
    plugins=["pii:direct", "harmful:hate"]
)

runner = RedTeamRunner(config)
results = await runner.run_assessment()
```

---

### Example 3: Integrate with Any FastAPI Application

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

config = PromptfooConfig(
    purpose="FastAPI LLM security testing",
    target=target,
    plugins=["pii:direct", "prompt-injection", "rbac"]
)

runner = RedTeamRunner(config)
results = await runner.run_assessment()
```

---

## 🎓 Summary

### Current State ✅

```
promptfoo_integration/
├── core/              → Configuration, types, clients (DONE)
├── red_team/          → Security testing with 21 plugins (DONE)
│   ├── plugins.py           → 5 custom plugins
│   └── plugins_builtin.py   → 16 Promptfoo built-in plugins ⭐ NEW
├── evaluations/       → Placeholder (READY)
└── guardrails/        → Placeholder (READY)
```

### Future Additions (Easy to Add)

```
promptfoo_integration/
├── evaluations/
│   ├── runner.py            → Quality assessment runner
│   ├── metrics.py           → Accuracy, relevance, coherence metrics
│   └── benchmarks.py        → Standard benchmarks
│
├── guardrails/
│   ├── validator.py         → Input/output validation
│   ├── filters.py           → Content filters
│   └── policies.py          → Safety policies
│
└── model_security/
    ├── adversarial.py       → Adversarial testing
    └── robustness.py        → Robustness testing
```

### Integration Benefits

✅ **Modular** - Add modules without breaking existing code
✅ **Flexible** - Use individual modules or combine them
✅ **Extensible** - Easy to add new capabilities
✅ **Portable** - Works with any Python LLM application
✅ **Production-ready** - Designed for real-world use

---

**Next:** See `HOW_TO_RUN.md` for step-by-step local setup instructions.
