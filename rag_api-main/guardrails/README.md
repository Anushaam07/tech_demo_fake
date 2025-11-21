# Guardrails Module

Runtime protection for LLM applications.

---

## What is This?

Guardrails provide **runtime protection** that filters malicious inputs and outputs in real-time.

| Aspect | Red Teaming (promptfoo_official/) | Guardrails (this module) |
|--------|-----------------------------------|--------------------------|
| **When** | Before deployment (testing) | During runtime (production) |
| **Purpose** | Find vulnerabilities | Block attacks in real-time |
| **How** | Generate attacks, evaluate | Filter inputs/outputs |
| **Output** | Report of vulnerabilities | Block/Allow decision |

---

## Folder Structure

```
guardrails/
├── configs/
│   └── guardrails_config.yaml    # Configuration file
├── middleware/
│   ├── __init__.py
│   ├── guardrails_middleware.py  # Core guardrails logic
│   └── fastapi_integration.py    # FastAPI integration
├── scripts/
│   └── test_guardrails.py        # Test script
├── logs/
│   └── guardrails.log            # Event logs (auto-created)
└── README.md                     # This file
```

---

## Quick Start

### 1. Test Guardrails

```bash
cd ~/tech_demo_fake/tech_demo_fake/rag_api-main
python3 guardrails/scripts/test_guardrails.py
```

### 2. Use in Your Application

```python
from guardrails import GuardrailsMiddleware

# Initialize
guardrails = GuardrailsMiddleware()

# Check input before sending to LLM
result = guardrails.check_input(user_query)
if result.blocked:
    return {"error": result.message}

# Get LLM response...
llm_response = get_llm_response(user_query)

# Check output before returning to user
result = guardrails.check_output(llm_response)
if result.blocked:
    return {"answer": result.safe_response}

return {"answer": llm_response}
```

---

## What Guardrails Detect

### Input Guardrails (Filter User Inputs)

| Guardrail | What It Detects | Example |
|-----------|-----------------|---------|
| **Prompt Injection** | Attempts to override instructions | "Ignore previous instructions..." |
| **Jailbreak** | Bypass safety attempts | "Enable DAN mode..." |
| **SQL Injection** | Database attacks | "'; DROP TABLE users;--" |
| **Code Injection** | Code execution attempts | "exec(os.system('rm -rf'))" |
| **PII Detection** | Personal info in queries | Credit cards, SSN, emails |
| **Toxic Content** | Harmful requests | Violence, self-harm |

### Output Guardrails (Filter LLM Responses)

| Guardrail | What It Detects | Action |
|-----------|-----------------|--------|
| **PII Leakage** | Personal info in responses | Block or Redact |
| **Harmful Content** | Violence, illegal advice | Block |
| **Confidential Info** | Internal secrets | Block |
| **Competitor Mentions** | Competitor names | Block (optional) |

---

## Configuration

### Config File: `configs/guardrails_config.yaml`

```yaml
# Enable/disable guardrails
enabled: true

# Input guardrails
prompt_injection: true
jailbreak_detection: true
sql_injection: true
code_injection: true
pii_detection: true
toxic_content: true

# Output guardrails
confidential_info: true
competitor_mention: false

# Action: block, warn, log, redact
action_on_trigger: block

# Logging
log_events: true
log_path: "./guardrails/logs/guardrails.log"

# Custom competitors (if competitor_mention is enabled)
competitors:
  - "Competitor AI Corp"
  - "RivalLLM Inc"
```

### Load Config

```python
from guardrails import create_guardrails

guardrails = create_guardrails("guardrails/configs/guardrails_config.yaml")
```

---

## FastAPI Integration

### Option 1: Manual Check

```python
from fastapi import FastAPI
from guardrails.middleware import GuardrailsMiddlewareAPI

app = FastAPI()
guardrails = GuardrailsMiddlewareAPI("guardrails/configs/guardrails_config.yaml")

@app.post("/query")
async def query(request: QueryRequest):
    # Check input
    input_check = guardrails.check_input(request.query)
    if input_check.blocked:
        return {"error": input_check.message, "blocked": True}

    # Process with LLM
    response = await process_query(request.query)

    # Check output
    output_check = guardrails.check_output(response)
    if output_check.blocked:
        return {"answer": output_check.safe_response, "filtered": True}

    return {"answer": response}
```

### Option 2: Middleware (Auto-Check All Requests)

```python
from fastapi import FastAPI
from guardrails.middleware import add_guardrails_middleware

app = FastAPI()
add_guardrails_middleware(app, "guardrails/configs/guardrails_config.yaml")

# All POST requests will be automatically checked
```

---

## PII Redaction

```python
from guardrails import GuardrailsMiddleware

guardrails = GuardrailsMiddleware()

text = "Contact john@example.com or call 555-123-4567. SSN: 123-45-6789"
redacted = guardrails.redact_pii(text)

print(redacted)
# Output: Contact [REDACTED_EMAIL] or call [REDACTED_PHONE]. SSN: [REDACTED_SSN]
```

---

## Logging

All guardrail events are logged to `guardrails/logs/guardrails.log`:

```
2024-01-15 10:30:45 - WARNING - GUARDRAIL_TRIGGERED | Type: prompt_injection | Action: block | Message: Potential prompt injection detected
2024-01-15 10:31:12 - WARNING - GUARDRAIL_TRIGGERED | Type: pii_detection | Action: block | Message: PII detected in output: ['credit_card']
```

---

## Actions

| Action | Behavior |
|--------|----------|
| **block** | Reject request, return error |
| **warn** | Allow request, log warning |
| **log** | Allow request, log event |
| **redact** | Remove sensitive data, allow |

Set in config:
```yaml
action_on_trigger: block  # or warn, log, redact
```

---

## API Reference

### GuardrailResult

```python
@dataclass
class GuardrailResult:
    passed: bool              # Did it pass the check?
    blocked: bool             # Was it blocked?
    guardrail_type: str       # Which guardrail triggered?
    action: str               # What action was taken?
    message: str              # Human-readable message
    details: dict             # Additional details
    safe_response: str        # Safe response to return (for outputs)
    timestamp: str            # When it happened
```

### Methods

```python
guardrails = GuardrailsMiddleware()

# Check user input
result = guardrails.check_input(text)

# Check LLM output
result = guardrails.check_output(text)

# Redact PII
clean_text = guardrails.redact_pii(text)
```

---

## Integration with RAG API

### Modify Your RAG Endpoint

```python
# In your main.py or api.py

from guardrails import GuardrailsMiddleware

guardrails = GuardrailsMiddleware()

@app.post("/query")
async def query(request: QueryRequest):
    # STEP 1: Check input with guardrails
    input_result = guardrails.check_input(request.query)
    if input_result.blocked:
        return {
            "error": input_result.message,
            "blocked": True,
            "guardrail_type": input_result.guardrail_type
        }

    # STEP 2: Your existing RAG logic
    response = await your_rag_query(request.query, request.file_id)

    # STEP 3: Check output with guardrails
    output_result = guardrails.check_output(response)
    if output_result.blocked:
        return {
            "answer": output_result.safe_response,
            "filtered": True,
            "guardrail_type": output_result.guardrail_type
        }

    # STEP 4: Return safe response
    return {"answer": response}
```

---

## Comparison: Red Teaming vs Guardrails

```
DEVELOPMENT LIFECYCLE:

[Development] → [Red Teaming] → [Fix Vulnerabilities] → [Guardrails] → [Production]
                     ↓                    ↓                   ↓
               Find issues         Fix code          Block at runtime
```

**Use Both:**
1. **Red Teaming** finds vulnerabilities before deployment
2. **Guardrails** blocks attacks that slip through in production

---

## Demo Commands

```bash
# Test guardrails
cd ~/tech_demo_fake/tech_demo_fake/rag_api-main
python3 guardrails/scripts/test_guardrails.py

# Check logs
cat guardrails/logs/guardrails.log
```

---

## Next Steps

1. ✅ Test guardrails: `python3 guardrails/scripts/test_guardrails.py`
2. Integrate with your RAG API
3. Customize config for your needs
4. Monitor logs in production

---

## Related Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `promptfoo_official/` | Red teaming (testing) | ✅ Done |
| `guardrails/` | Runtime protection | ✅ Done |
| `evaluations/` | Model evaluation | 🔮 Future |
| `model_security/` | Model security scanning | 🔮 Future |
