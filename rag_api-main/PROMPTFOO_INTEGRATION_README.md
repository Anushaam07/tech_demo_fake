# Promptfoo Integration for RAG API

A comprehensive, modular integration of Promptfoo's security testing features into the RAG API application. This integration provides enterprise-grade red teaming, security testing, and vulnerability assessment capabilities for LLM applications.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Available Plugins](#available-plugins)
- [Available Strategies](#available-strategies)
- [Compliance Presets](#compliance-presets)
- [Report Generation](#report-generation)
- [Integration with Other Applications](#integration-with-other-applications)
- [Future Features](#future-features)
- [API Reference](#api-reference)

## 🎯 Overview

This modular Promptfoo integration brings state-of-the-art LLM security testing capabilities to your RAG application. It's designed to be:

- **Flexible**: Works with any LLM application (API, LangChain, custom)
- **Modular**: Easy to extend with new plugins and strategies
- **Comprehensive**: 100+ vulnerability tests across 6 categories
- **Production-Ready**: Async execution, detailed reporting, compliance presets
- **Future-Proof**: Architecture ready for guardrails and evaluation features

## 🏗️ Architecture

The integration follows a clean, modular architecture:

```
promptfoo_integration/
├── core/                    # Core functionality
│   ├── config.py           # Configuration management
│   ├── client.py           # Target client implementations
│   └── types.py            # Type definitions
├── red_team/               # Red teaming features
│   ├── plugins.py          # Vulnerability test generators
│   ├── strategies.py       # Attack strategies
│   ├── runner.py           # Test orchestration
│   ├── grader.py           # Response evaluation
│   └── report.py           # Report generation
├── evaluations/            # Future: Performance evaluation
├── guardrails/             # Future: Safety controls
└── utils/                  # Utility functions
```

### Key Components

1. **Core Module**: Configuration, client management, type definitions
2. **Red Team Module**: Security testing with plugins and strategies
3. **Clients**: Support for API, LangChain, and custom targets
4. **Reporting**: HTML, JSON, and text reports with visualizations

## ✨ Features

### Current Features (v1.0)

#### Red Teaming
- ✅ **104+ Security Plugins** across 6 categories
- ✅ **7 Attack Strategies** for bypassing defenses
- ✅ **Compliance Presets** (OWASP, NIST, MITRE, EU AI Act)
- ✅ **Async Execution** with configurable concurrency
- ✅ **Multiple Report Formats** (HTML, JSON, text)
- ✅ **Vulnerability Grading** with severity levels
- ✅ **Flexible Target Support** (API, LangChain, custom)

### Future Features (Roadmap)

- 🔜 **Guardrails**: Content filtering and safety controls
- 🔜 **Model Security**: Advanced adversarial testing
- 🔜 **Evaluations**: Performance and quality benchmarks
- 🔜 **LLM-Based Grading**: AI-powered response analysis
- 🔜 **CI/CD Integration**: Automated security testing

## 📦 Installation

### Prerequisites

- Python 3.8+
- FastAPI application (for API targets)
- OpenAI API key (for grading) or compatible LLM API

### Install Dependencies

```bash
# Install the RAG API with Promptfoo integration
cd rag_api-main
pip install -r requirements.txt
```

### Environment Variables

```bash
# Required for grading (if using OpenAI)
export OPENAI_API_KEY="your-api-key"

# Or use RAG-specific key
export RAG_OPENAI_API_KEY="your-api-key"

# Optional: Custom grading endpoint
export RAG_OPENAI_BASEURL="https://your-custom-endpoint.com"
```

## 🚀 Quick Start

### 1. Basic Red Team Assessment

```python
import asyncio
from promptfoo_integration import PromptfooConfig, RedTeamRunner
from promptfoo_integration.core.types import TargetConfig, PluginType

async def main():
    # Configure target
    target = TargetConfig(
        name="my-rag-api",
        type="api",
        endpoint="http://localhost:8000/v1/query",
        config={
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "prompt_key": "query",
            "response_key": "answer"
        }
    )

    # Configure assessment
    config = PromptfooConfig(
        purpose="RAG-based QA system",
        target=target,
        plugins=[
            PluginType.PROMPT_INJECTION,
            PluginType.PII,
            PluginType.HARMFUL_CONTENT
        ],
        num_tests=5
    )

    # Run assessment
    runner = RedTeamRunner(config)
    results = await runner.run_assessment()

    # Generate report
    from promptfoo_integration.red_team.report import ReportGenerator
    generator = ReportGenerator(results)
    generator.save_report(format="html", file_path="report.html")

asyncio.run(main())
```

### 2. Using Configuration File

Create `config.yaml`:

```yaml
purpose: "RAG-based documentation QA system"
target:
  name: "rag-api"
  type: "api"
  endpoint: "http://localhost:8000/v1/query"
  config:
    method: "POST"
    prompt_key: "query"
    response_key: "answer"

plugins:
  - "prompt-injection"
  - "sql-injection"
  - "harmful-content"
  - "pii"

strategies:
  - "jailbreak"
  - "base64"

num_tests: 10
output_dir: "./red_team_results"
```

Run with:

```python
from promptfoo_integration import PromptfooConfig, RedTeamRunner

config = PromptfooConfig.from_yaml("config.yaml")
runner = RedTeamRunner(config)
results = runner.run_assessment_sync()
```

### 3. Compliance Testing

```python
from promptfoo_integration import PromptfooConfig
from promptfoo_integration.core.types import CompliancePreset

config = PromptfooConfig.with_compliance_preset(
    preset=CompliancePreset.OWASP_LLM_TOP_10,
    target=target,
    purpose="OWASP compliance testing"
)

runner = RedTeamRunner(config)
results = runner.run_assessment_sync()
```

## ⚙️ Configuration

### Target Configuration

#### API Target

```python
TargetConfig(
    name="my-api",
    type="api",
    endpoint="http://localhost:8000/query",
    config={
        "method": "POST",
        "headers": {"Authorization": "Bearer token"},
        "prompt_key": "prompt",
        "response_key": "response",
        "timeout": 30
    }
)
```

#### LangChain Target

```python
from langchain.chains import RetrievalQA

TargetConfig(
    name="my-chain",
    type="langchain",
    config={
        "chain": my_chain,
        "invoke_method": "invoke"
    }
)
```

#### Custom Target

```python
def my_query_function(prompt: str, **kwargs) -> str:
    # Your custom logic
    return response

TargetConfig(
    name="custom",
    type="custom",
    config={
        "query_fn": my_query_function
    }
)
```

## 📚 Usage Examples

See the `examples/` directory for complete examples:

- **basic_red_team_example.py**: Basic API red teaming
- **langchain_red_team_example.py**: LangChain integration
- **custom_target_example.py**: Custom application testing
- **config_examples/**: YAML configuration templates

### Running Examples

```bash
# Basic example
python examples/basic_red_team_example.py

# LangChain example
python examples/langchain_red_team_example.py

# Custom target example
python examples/custom_target_example.py
```

## 🔌 Available Plugins

### Security & Access Control
- `sql-injection`: SQL injection attacks
- `shell-injection`: Shell command injection
- `prompt-injection`: Prompt manipulation attacks
- `ssrf`: Server-side request forgery
- `broken-access-control`: Access control bypass
- `debug-access`: Debug endpoint exploitation
- `rbac`: Role-based access control tests

### Trust & Safety
- `harmful-content`: Harmful content generation
- `harmful-privacy`: Privacy violation tests
- `harmful-hate`: Hate speech generation
- `harmful-violent-crime`: Violence-related content
- `harmful-specialized-advice`: Dangerous advice

### Brand Protection
- `competitors`: Competitor endorsement
- `hallucination`: Fabricated information
- `misinformation`: False information spread
- `politics`: Political bias testing

### Compliance & Legal
- `contracts`: Contract violation
- `excessive-agency`: Unauthorized actions
- `imitation`: Impersonation attempts
- `intellectual-property`: IP violation

### Data Security
- `pii`: Personal information leakage
- `overreliance`: Excessive confidence testing

## 🎯 Available Strategies

Strategies modify how attacks are delivered to bypass defenses:

- `jailbreak`: Role-play and hypothetical scenarios
- `prompt-injection`: Instruction override attempts
- `base64`: Base64 encoding obfuscation
- `rot13`: ROT13 cipher obfuscation
- `leetspeak`: Character substitution
- `multilingual`: Translation-based bypass
- `crescendo`: Gradual escalation attacks

## 📋 Compliance Presets

Pre-configured plugin sets for common frameworks:

### OWASP LLM Top 10
```python
CompliancePreset.OWASP_LLM_TOP_10
```
Tests: Prompt injection, broken access control, PII, overreliance, hallucination

### OWASP API Top 10
```python
CompliancePreset.OWASP_API_TOP_10
```
Tests: Broken access control, SQL injection, SSRF, RBAC

### NIST AI RMF
```python
CompliancePreset.NIST_AI_RMF
```
Tests: Harmful content, misinformation, PII, hallucination

### MITRE ATLAS
```python
CompliancePreset.MITRE_ATLAS
```
Tests: Prompt injection, debug access, harmful content

### EU AI Act
```python
CompliancePreset.EU_AI_ACT
```
Tests: Harmful content, PII, misinformation, hate speech

## 📊 Report Generation

### HTML Reports

Rich, interactive HTML reports with visualizations:

```python
from promptfoo_integration.red_team.report import ReportGenerator

generator = ReportGenerator(results)
generator.save_report(format="html", file_path="report.html")
```

Features:
- Executive summary with key metrics
- Vulnerability breakdown by severity
- Plugin and strategy analysis
- Detailed vulnerability listings
- Visual charts and graphs

### JSON Reports

Machine-readable format for automation:

```python
generator.save_report(format="json", file_path="report.json")
```

### Text Reports

Console-friendly text format:

```python
generator.save_report(format="text", file_path="report.txt")
```

## 🔗 Integration with Other Applications

The integration is designed to work with **any LLM application**:

### REST APIs

```python
target = TargetConfig(
    name="any-api",
    type="api",
    endpoint="https://your-api.com/endpoint",
    config={
        "headers": {"Authorization": "Bearer token"},
        "prompt_key": "input",
        "response_key": "output"
    }
)
```

### LangChain Applications

```python
target = TargetConfig(
    name="langchain-app",
    type="langchain",
    config={"chain": your_chain}
)
```

### Custom Python Functions

```python
def my_llm_function(prompt: str) -> str:
    # Your logic here
    return response

target = TargetConfig(
    name="custom",
    type="custom",
    config={"query_fn": my_llm_function}
)
```

### Gradio/Streamlit Apps

```python
import requests

def query_gradio(prompt: str) -> str:
    response = requests.post(
        "http://localhost:7860/api/predict",
        json={"data": [prompt]}
    )
    return response.json()["data"][0]

target = TargetConfig(
    name="gradio-app",
    type="custom",
    config={"query_fn": query_gradio}
)
```

## 🚧 Future Features

The modular architecture is designed for easy extension:

### Guardrails Module (Coming Soon)

```python
from promptfoo_integration.guardrails import ContentFilter

filter = ContentFilter(
    block_pii=True,
    block_harmful=True,
    block_injection=True
)
```

### Evaluations Module (Coming Soon)

```python
from promptfoo_integration.evaluations import PerformanceEvaluator

evaluator = PerformanceEvaluator(
    metrics=["accuracy", "latency", "cost"]
)
results = evaluator.evaluate(target)
```

### Model Security Module (Coming Soon)

Advanced adversarial testing and model robustness assessment.

## 📖 API Reference

### Core Classes

#### PromptfooConfig

Main configuration class for all operations.

```python
PromptfooConfig(
    purpose: str,                    # System description
    target: TargetConfig,            # Target configuration
    plugins: List[PluginType],       # Plugins to use
    strategies: List[StrategyType],  # Strategies to apply
    num_tests: int = 10,             # Tests per plugin
    grader_model: str = "gpt-4",     # Grading model
    output_dir: str = "./results"    # Output directory
)
```

Methods:
- `from_yaml(file_path)`: Load from YAML file
- `from_json(file_path)`: Load from JSON file
- `with_compliance_preset(preset, target, **kwargs)`: Create with preset

#### RedTeamRunner

Orchestrates red team assessments.

```python
runner = RedTeamRunner(config)
```

Methods:
- `run_assessment(max_concurrent=5)`: Run async assessment
- `run_assessment_sync()`: Run synchronous assessment
- `run_single_test(test_input)`: Test single input
- `generate_test_cases()`: Generate test cases
- `save_results(file_path)`: Save results to file

#### ReportGenerator

Generates comprehensive reports.

```python
generator = ReportGenerator(results)
```

Methods:
- `generate_summary()`: Get summary statistics
- `generate_html_report()`: Create HTML report
- `generate_json_report()`: Create JSON report
- `generate_text_report()`: Create text report
- `save_report(format, file_path)`: Save report to file
- `print_summary()`: Print console summary

## 🎓 Best Practices

### 1. Start Small

Begin with a few plugins and gradually expand:

```python
plugins=[
    PluginType.PROMPT_INJECTION,
    PluginType.PII
]
```

### 2. Use Compliance Presets

Leverage pre-configured sets for common frameworks:

```python
config = PromptfooConfig.with_compliance_preset(
    CompliancePreset.OWASP_LLM_TOP_10,
    target=target
)
```

### 3. Monitor Concurrency

Adjust based on your API rate limits:

```python
results = await runner.run_assessment(max_concurrent=3)
```

### 4. Regular Testing

Integrate into your development workflow:

```bash
# Run nightly
0 2 * * * python red_team_tests.py
```

### 5. Review Reports

Always review detailed HTML reports for context:

```python
generator.save_report(format="html")
```

## 🤝 Contributing

This integration is designed for extensibility:

1. **Add New Plugins**: Extend `BasePlugin` in `plugins.py`
2. **Add New Strategies**: Extend `BaseStrategy` in `strategies.py`
3. **Add New Clients**: Extend `BaseTargetClient` in `client.py`

## 📝 License

This integration follows the same license as the RAG API project.

## 🆘 Support

For issues, questions, or contributions:

1. Check existing examples in `examples/`
2. Review configuration templates in `examples/config_examples/`
3. Open an issue with detailed information

## 🎉 Acknowledgments

This integration is inspired by Promptfoo's excellent open-source security testing framework. We've adapted their concepts into a Python-native, modular implementation optimized for RAG applications and enterprise use cases.

---

**Made with ❤️ for secure LLM applications**
