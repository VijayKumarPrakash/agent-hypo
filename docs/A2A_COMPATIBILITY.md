# A2A Compatibility Guide

## Overview

**Yes, the revamped White Agent maintains full A2A (Agent-to-Agent) compatibility!**

Both the traditional and LLM-powered modes support the AgentBeats A2A protocol, allowing seamless integration with other agents like the Green Agent orchestrator.

## What's New

The agent now **automatically selects** between traditional and LLM-powered modes based on API key availability, while maintaining the same A2A interface.

### Enhanced Capabilities

When running in LLM mode, the agent advertises enhanced capabilities:

```json
{
  "status": "success",
  "agent_type": "llm_white_agent",
  "capabilities": [
    "adaptive_data_loading",
    "intelligent_variable_identification",
    "context_aware_analysis",
    "comprehensive_reporting",
    "multi_format_support"
  ],
  "ready": true,
  "llm_enabled": true
}
```

## Running A2A Server

### Quick Start

```bash
# Set API key for LLM mode (optional)
export GEMINI_API_KEY="your-key"

# Start A2A server
python src/launcher.py --mode server --agent-port 8001
```

### With Mode Selection

```bash
# Force LLM mode
python src/launcher.py --mode server --analysis-mode llm

# Force traditional mode
python src/launcher.py --mode server --analysis-mode traditional

# Auto-detect (default)
python src/launcher.py --mode server --analysis-mode auto
```

### Full Configuration

```bash
python src/launcher.py \
  --mode server \
  --analysis-mode auto \
  --agent-host 0.0.0.0 \
  --agent-port 8001 \
  --launcher-host 0.0.0.0 \
  --launcher-port 8000 \
  --inputs-dir inputs \
  --results-dir results
```

## A2A Protocol Endpoints

The launcher exposes the following endpoints:

### 1. Analysis Endpoint

**POST** `/a2a/analyze`

Request:
```json
{
  "action": "analyze_test",
  "params": {
    "test_index": 1
  }
}
```

Response (Success):
```json
{
  "status": "success",
  "results": {
    "test_index": 1,
    "result_version": 1,
    "output_dir": "results/result_1_1",
    "analysis_type": "llm_powered",
    "experiment_type": "RCT",
    "data_shape": {
      "rows": 1000,
      "columns": 5
    },
    "variables": {
      "treatment": "group",
      "outcome": "conversion_rate",
      "treatment_value": "B",
      "control_value": "A"
    },
    "analysis_summary": {
      "sample_size": 1000,
      "treatment_effect": 0.0123,
      "p_value": 0.042,
      "statistically_significant": true
    },
    "analysis_successful": true,
    "llm_models_used": {
      "data_loader": "gemini-1.5-flash",
      "analyzer": "gemini-1.5-pro",
      "report_generator": "gemini-1.5-pro"
    }
  }
}
```

Response (Error):
```json
{
  "status": "error",
  "error": "Test directory not found: inputs/test_1"
}
```

### 2. Status Endpoint

**GET** `/a2a/status`

Response (LLM Mode):
```json
{
  "status": "success",
  "agent_type": "llm_white_agent",
  "capabilities": [
    "adaptive_data_loading",
    "intelligent_variable_identification",
    "context_aware_analysis",
    "comprehensive_reporting",
    "multi_format_support"
  ],
  "ready": true,
  "llm_enabled": true
}
```

Response (Traditional Mode):
```json
{
  "status": "success",
  "agent_type": "white_agent",
  "capabilities": [
    "rct_analysis",
    "statistical_testing",
    "report_generation"
  ],
  "ready": true
}
```

### 3. Reset Endpoint

**POST** `/a2a/reset`

Response:
```json
{
  "status": "success",
  "message": "White Agent reset successfully"
}
```

### 4. Health Check

**GET** `/health`

Response:
```json
{
  "status": "healthy"
}
```

## Integration with Green Agent

The White Agent can be triggered by a Green Agent orchestrator:

### Example: Green Agent → White Agent

```python
import requests

# Green Agent sends analysis request to White Agent
response = requests.post(
    "http://localhost:8001/a2a/analyze",
    json={
        "action": "analyze_test",
        "params": {
            "test_index": 12
        }
    }
)

result = response.json()

if result["status"] == "success":
    print(f"Analysis complete!")
    print(f"ATE: {result['results']['analysis_summary']['treatment_effect']}")
    print(f"p-value: {result['results']['analysis_summary']['p_value']}")
    print(f"Report: {result['results']['output_dir']}/report/analysis_report.md")
else:
    print(f"Error: {result['error']}")
```

## Programmatic A2A Usage

You can also use the A2A interface programmatically without running a server:

```python
from white_agent.unified_agent import UnifiedWhiteAgent

# Initialize agent
agent = UnifiedWhiteAgent()

# Send A2A message
response = agent.handle_a2a_message({
    "action": "analyze_test",
    "params": {
        "test_index": 1
    }
})

# Check response
if response["status"] == "success":
    results = response["results"]
    print(f"Analysis complete: {results['output_dir']}")
else:
    print(f"Error: {response['error']}")
```

## Standalone Interactive Mode

For testing and development:

```bash
python src/launcher.py --mode standalone
```

Interactive commands:
```
> analyze 1        # Analyze test_1
> status          # Check agent status
> reset           # Reset agent state
> quit            # Exit
```

## AgentBeats Platform Integration

### Using agentbeats CLI

If you have the AgentBeats CLI installed:

```bash
agentbeats run white_agent_card.toml \
  --launcher_host 0.0.0.0 \
  --launcher_port 8000 \
  --agent_host 0.0.0.0 \
  --agent_port 8001
```

### Agent Card Configuration

The `white_agent_card.toml` file specifies the agent configuration:

```toml
[agent]
name = "white_agent"
type = "analysis"
version = "2.0.0"

[agent.capabilities]
rct_analysis = true
statistical_testing = true
report_generation = true
llm_powered = true
adaptive_data_loading = true
multi_format_support = true

[agent.endpoints]
analyze = "/a2a/analyze"
status = "/a2a/status"
reset = "/a2a/reset"
health = "/health"

[agent.network]
default_port = 8001

[agent.config]
inputs_dir = "inputs"
results_dir = "results"
```

## API Compatibility Matrix

| Feature | Traditional Mode | LLM Mode | A2A Compatible |
|---------|------------------|----------|----------------|
| **analyze_test action** | ✅ | ✅ | ✅ |
| **get_status action** | ✅ | ✅ | ✅ |
| **reset method** | ✅ | ✅ | ✅ |
| **FastAPI server** | ✅ | ✅ | ✅ |
| **Programmatic A2A** | ✅ | ✅ | ✅ |
| **AgentBeats CLI** | ✅ | ✅ | ✅ |
| **Data format flexibility** | ❌ CSV only | ✅ Any format | ✅ |
| **Variable auto-detection** | ⚠️ Heuristic | ✅ LLM-guided | ✅ |

## Message Flow Example

### Multi-Agent Workflow

```
┌─────────────┐                ┌─────────────┐                ┌─────────────┐
│    Green    │                │    White    │                │   Results   │
│    Agent    │                │    Agent    │                │   Storage   │
└──────┬──────┘                └──────┬──────┘                └──────┬──────┘
       │                              │                              │
       │ POST /a2a/analyze            │                              │
       │ test_index: 12               │                              │
       ├─────────────────────────────>│                              │
       │                              │                              │
       │                              │ Load data (LLM mode)         │
       │                              │ Analyze experiment            │
       │                              │ Generate report              │
       │                              │                              │
       │                              │ Save results ───────────────>│
       │                              │                              │
       │ Response: results            │                              │
       │<─────────────────────────────┤                              │
       │                              │                              │
       │ Notify user                  │                              │
       │                              │                              │
```

## Backward Compatibility

All existing A2A integrations continue to work:

### Old Code (Still Works)
```python
from white_agent import WhiteAgent

agent = WhiteAgent()
response = agent.handle_a2a_message({
    "action": "analyze_test",
    "params": {"test_index": 1}
})
```

### New Code (Enhanced)
```python
from white_agent.unified_agent import UnifiedWhiteAgent

# Auto-detects mode, same interface
agent = UnifiedWhiteAgent()
response = agent.handle_a2a_message({
    "action": "analyze_test",
    "params": {"test_index": 1}
})

# Check mode
if agent.is_llm_powered:
    print("Using LLM-powered analysis")
```

## Environment Variables

For A2A server deployment:

```bash
# Optional: Enable LLM mode
export GEMINI_API_KEY="your-gemini-api-key"

# Optional: Custom directories
export WHITE_AGENT_INPUTS_DIR="inputs"
export WHITE_AGENT_RESULTS_DIR="results"
```

## Docker Deployment

Example Dockerfile for A2A server:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn

# Copy agent code
COPY src/ ./src/
COPY inputs/ ./inputs/

# Set environment variables
ENV GEMINI_API_KEY=""
ENV WHITE_AGENT_INPUTS_DIR="inputs"
ENV WHITE_AGENT_RESULTS_DIR="results"

# Expose A2A port
EXPOSE 8001

# Run server
CMD ["python", "src/launcher.py", "--mode", "server", "--agent-port", "8001"]
```

Build and run:
```bash
docker build -t white-agent .
docker run -p 8001:8001 -e GEMINI_API_KEY="your-key" white-agent
```

## Testing A2A Endpoints

### Using curl

```bash
# Check status
curl http://localhost:8001/a2a/status

# Analyze test
curl -X POST http://localhost:8001/a2a/analyze \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze_test", "params": {"test_index": 1}}'

# Reset agent
curl -X POST http://localhost:8001/a2a/reset

# Health check
curl http://localhost:8001/health
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8001"

# Check status
response = requests.get(f"{BASE_URL}/a2a/status")
print(response.json())

# Analyze test
response = requests.post(
    f"{BASE_URL}/a2a/analyze",
    json={
        "action": "analyze_test",
        "params": {"test_index": 1}
    }
)
print(response.json())

# Reset
response = requests.post(f"{BASE_URL}/a2a/reset")
print(response.json())
```

## Error Handling

The A2A interface provides consistent error responses:

```json
{
  "status": "error",
  "error": "Detailed error message"
}
```

Common errors:
- `"Missing required parameter: test_index"`
- `"Test directory not found: inputs/test_X"`
- `"Unknown action: invalid_action"`
- `"Failed to load data from ..."`
- `"Analysis failed: ..."`

## Security Considerations

### API Key Protection
- Never expose GEMINI_API_KEY in version control
- Use environment variables or secrets management
- Consider rate limiting for production deployments

### Network Security
- Use HTTPS in production
- Implement authentication for A2A endpoints
- Restrict access to trusted agents only

### Data Privacy
- Be aware that LLM mode sends data samples to Gemini API
- Consider data sensitivity when choosing modes
- Use traditional mode for highly sensitive data

## Performance Considerations

### Response Times

**Traditional Mode:**
- Typical: 2-5 seconds
- Suitable for: High-throughput scenarios

**LLM Mode:**
- Typical: 10-30 seconds
- Suitable for: Flexible data analysis

### Scaling

For high-volume A2A deployments:

1. **Load Balancing**: Run multiple instances behind a load balancer
2. **Caching**: Cache analysis results for repeated tests
3. **Async Processing**: Use background jobs for long-running analyses
4. **Mode Selection**: Use traditional mode when data is standardized

## Monitoring & Logging

The launcher includes comprehensive logging:

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

Monitor these events:
- A2A request received
- Mode selection (LLM vs traditional)
- Analysis start/complete
- Errors and failures
- Reset signals

## Summary

✅ **Full A2A compatibility maintained**
✅ **Backward compatible with existing integrations**
✅ **Enhanced capabilities in LLM mode**
✅ **Automatic mode selection**
✅ **Same A2A interface for both modes**
✅ **Production-ready for AgentBeats platform**

The revamped White Agent seamlessly integrates with the AgentBeats A2A protocol while providing enhanced flexibility through LLM-powered analysis!
