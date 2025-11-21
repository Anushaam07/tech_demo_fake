# Promptfoo Providers - RAG API Bridge

This directory contains custom Python providers that bridge Promptfoo (Node.js) with the RAG API (Python).

## What is a Provider?

In Promptfoo, a **provider** is a script or service that:
1. Receives a prompt/query from Promptfoo
2. Processes the query (forwards to your LLM/API)
3. Returns the response back to Promptfoo

Our providers act as a **bridge** between:
- **Promptfoo** (Node.js red teaming tool)
- **RAG API** (Python FastAPI application)

## Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Promptfoo  │─────▶│  Python Provider │─────▶│   RAG API   │
│  (Node.js)  │◀─────│     (Bridge)     │◀─────│   (Python)  │
└─────────────┘      └──────────────────┘      └─────────────┘
                            │
                            │
                     ┌──────▼───────┐
                     │  PostgreSQL  │
                     │  + pgvector  │
                     └──────────────┘
```

**Flow:**
1. Promptfoo generates adversarial prompts
2. Promptfoo calls Python provider with prompt
3. Provider forwards prompt to RAG API
4. RAG API queries vector database
5. RAG API returns answer with sources
6. Provider formats response for Promptfoo
7. Promptfoo evaluates response for vulnerabilities

## Available Providers

### 1. `rag_provider.py` - Synchronous Provider

**Purpose:** Basic synchronous provider for standard testing

**Features:**
- Simple HTTP requests to RAG API
- JSON input/output
- Error handling
- Configurable via environment variables

**Usage:**
```bash
# Direct usage
python3 rag_provider.py "What security measures are in place?"

# With Promptfoo
promptfoo eval -c configs/promptfooconfig.yaml
```

**Configuration:**
```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
```

**When to use:**
- Standard testing scenarios
- Simple setups
- Low concurrency requirements

---

### 2. `rag_provider_async.py` - Asynchronous Provider

**Purpose:** Advanced async provider for high-performance concurrent testing

**Features:**
- Async HTTP requests using `aiohttp`
- Batch query support
- Configurable timeouts
- Better performance for concurrent tests
- Connection pooling

**Usage:**
```bash
# Direct usage
python3 rag_provider_async.py "What security measures are in place?"

# With Promptfoo
promptfoo eval -c configs/promptfooconfig.yaml
```

**Configuration:**
```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
export RAG_TIMEOUT="30"  # Request timeout in seconds
```

**When to use:**
- High-volume testing
- Concurrent test execution
- Performance-critical scenarios
- Batch testing

---

## How Providers Work

### Input Format

Promptfoo calls the provider with a prompt as a command-line argument:

```bash
python3 rag_provider.py "Your prompt here"
```

### Output Format

Provider must output JSON to stdout:

```json
{
  "output": "The answer from RAG API",
  "metadata": {
    "sources": [...],
    "file_id": "security-manual-001",
    "k": 4
  }
}
```

**Required fields:**
- `output` - The response text (what Promptfoo will evaluate)

**Optional fields:**
- `metadata` - Additional context (sources, file_id, etc.)
- `error` - Error message if request failed

### Error Handling

If the provider encounters an error, it returns:

```json
{
  "output": "Error description",
  "error": "Technical error details"
}
```

This ensures Promptfoo receives a response even if the API call fails.

---

## Provider Configuration in Promptfoo

### YAML Configuration

In your `promptfooconfig.yaml`:

```yaml
providers:
  - id: python:./promptfoo_official/providers/rag_provider.py
    label: "RAG API Provider"
    config:
      env:
        RAG_API_ENDPOINT: "http://localhost:8000/query"
        RAG_FILE_ID: "security-manual-001"
        RAG_K: "4"
```

**Key components:**
- `id: python:` - Tells Promptfoo to execute a Python script
- `./promptfoo_official/providers/rag_provider.py` - Path to provider script
- `env:` - Environment variables passed to provider

### Using Async Provider

```yaml
providers:
  - id: python:./promptfoo_official/providers/rag_provider_async.py
    label: "RAG API Async Provider"
    config:
      env:
        RAG_API_ENDPOINT: "http://localhost:8000/query"
        RAG_FILE_ID: "security-manual-001"
        RAG_K: "4"
        RAG_TIMEOUT: "30"
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RAG_API_ENDPOINT` | RAG API query endpoint | `http://localhost:8000/query` |
| `RAG_FILE_ID` | Document ID to query | `security-manual-001` |
| `RAG_K` | Number of results | `4` |

### Optional Variables

| Variable | Description | Default | Provider |
|----------|-------------|---------|----------|
| `RAG_TIMEOUT` | Request timeout (seconds) | `30` | Async only |

### Setting Variables

**Option 1: Export in shell**
```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
```

**Option 2: In YAML config**
```yaml
providers:
  - id: python:./promptfoo_official/providers/rag_provider.py
    config:
      env:
        RAG_API_ENDPOINT: "http://localhost:8000/query"
        RAG_FILE_ID: "security-manual-001"
        RAG_K: "4"
```

**Option 3: .env file**
```bash
# .env
RAG_API_ENDPOINT=http://localhost:8000/query
RAG_FILE_ID=security-manual-001
RAG_K=4
```

Then load:
```bash
source .env
promptfoo eval -c configs/promptfooconfig.yaml
```

---

## Testing Providers

### Manual Testing

```bash
# Test sync provider
python3 rag_provider.py "What is Docker?"

# Test async provider
python3 rag_provider_async.py "What is Docker?"
```

Expected output:
```json
{
  "output": "Docker is a platform...",
  "metadata": {
    "sources": [...],
    "file_id": "security-manual-001",
    "k": 4
  }
}
```

### Using Test Script

```bash
cd ../scripts
./test_provider.sh
```

This script:
- Checks RAG API availability
- Tests both providers
- Displays formatted results

---

## Customizing Providers

### Adding Custom Headers

Edit `rag_provider.py`:

```python
response = requests.post(
    self.endpoint,
    json=payload,
    headers={
        "Authorization": "Bearer your-token",
        "X-Custom-Header": "value"
    },
    timeout=30
)
```

### Adding Authentication

```python
def __init__(self, endpoint, file_id, k, api_key=None):
    self.endpoint = endpoint
    self.file_id = file_id
    self.k = k
    self.api_key = api_key or os.getenv("RAG_API_KEY")

def query(self, prompt):
    headers = {}
    if self.api_key:
        headers["Authorization"] = f"Bearer {self.api_key}"

    response = requests.post(
        self.endpoint,
        json=payload,
        headers=headers,
        timeout=30
    )
```

### Adding Response Transformation

```python
def query(self, prompt):
    # ... make request ...

    data = response.json()

    # Transform response
    transformed_output = self.transform_response(data)

    return {
        "output": transformed_output,
        "metadata": {...}
    }

def transform_response(self, data):
    """Custom response transformation"""
    answer = data.get("answer", "")
    sources = data.get("sources", [])

    # Add source citations
    if sources:
        answer += "\n\nSources:\n"
        for i, source in enumerate(sources, 1):
            answer += f"{i}. {source['text'][:100]}...\n"

    return answer
```

---

## Integration with Other LLM Applications

These providers can be adapted for any LLM application. Here's how:

### For OpenAI API

```python
import openai

def query(self, prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "output": response.choices[0].message.content,
        "metadata": {
            "model": response.model,
            "tokens": response.usage.total_tokens
        }
    }
```

### For Anthropic Claude API

```python
import anthropic

def query(self, prompt):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "output": response.content[0].text,
        "metadata": {
            "model": response.model,
            "stop_reason": response.stop_reason
        }
    }
```

### For Local Models (Ollama)

```python
import requests

def query(self, prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": prompt
        }
    )

    return {
        "output": response.json()["response"],
        "metadata": {
            "model": "llama2"
        }
    }
```

---

## Troubleshooting

### "Connection refused" error

**Cause:** RAG API is not running

**Solution:**
```bash
docker compose up -d
curl http://localhost:8000/health
```

### "Module not found" error

**Cause:** Missing Python dependencies

**Solution:**
```bash
pip3 install requests aiohttp
```

### "Permission denied" error

**Cause:** Provider script is not executable

**Solution:**
```bash
chmod +x rag_provider.py rag_provider_async.py
```

### "Timeout" error

**Cause:** Request taking too long

**Solution:**
- Increase timeout: `export RAG_TIMEOUT="60"`
- Check RAG API performance
- Use async provider for better concurrency

### Provider returns empty output

**Cause:** Environment variables not set

**Solution:**
```bash
export RAG_API_ENDPOINT="http://localhost:8000/query"
export RAG_FILE_ID="security-manual-001"
export RAG_K="4"
```

---

## Performance Considerations

### Sync Provider
- **Throughput:** ~10-20 requests/second
- **Concurrency:** Limited by sequential execution
- **Use case:** Small test suites (< 100 tests)

### Async Provider
- **Throughput:** ~50-100 requests/second
- **Concurrency:** Handles many concurrent requests
- **Use case:** Large test suites (100+ tests)

**Recommendation:** Use async provider for comprehensive testing

---

## Related Documentation

- **../configs/README.md** - Configuration files
- **../scripts/README.md** - Helper scripts
- **../INTEGRATION_GUIDE.md** - Complete integration guide

---

## Next Steps

1. Test providers: `../scripts/test_provider.sh`
2. Configure Promptfoo: Edit `../configs/promptfooconfig.yaml`
3. Run tests: `../scripts/run_single_test.sh pii`
4. View results: `promptfoo view`
