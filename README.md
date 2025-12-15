# White Agent - RCT Analysis

An autonomous agent for analyzing randomized controlled trials (RCTs) and A/B tests, built for CS 294 and compatible with the A2A (Agent-to-Agent) protocol.

## Overview

The White Agent performs comprehensive statistical analysis on experimental data. It supports two deployment modes:
- **A2A HTTP Service**: Cloud-ready stateless API for agent orchestration
- **Legacy CLI Mode**: Local file-based analysis tool

### Key Features

- **LLM-Powered Analysis**: Adapts to any data format with intelligent variable detection
- **Automated Statistics**: ATE, p-values, confidence intervals, effect sizes, regression analysis
- **Covariate Balance Checking**: Verifies randomization quality
- **Reproducible Code**: Generates Python scripts to reproduce analyses
- **Multiple Data Formats**: CSV, JSON, Parquet, Excel support
- **A2A Compatible**: Standard A2A protocol with cloud storage integration
- **Dual Mode**: Auto-detects between LLM mode (with API key) and traditional statistical mode

## Quick Start

### A2A Service (Recommended for Production)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.a2a.example .env
# Edit .env with your S3 credentials and optional Gemini API key
```

3. **Run server:**
```bash
uvicorn app.server:app --reload
```

4. **Test it:**
```bash
# Visit http://localhost:8000/docs for interactive API
# Or run: python test_a2a_service.py
```

See [QUICK_START_A2A.md](QUICK_START_A2A.md) for detailed A2A setup.

### Legacy CLI Mode

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Optional - configure Gemini API:**
```bash
cp .env.example .env
# Edit .env and add GEMINI_API_KEY for LLM-powered reports
```

3. **Run analysis:**
```bash
python legacy_main.py
```

The agent works without an API key using traditional statistical methods.

## Documentation

- **[QUICK_START_A2A.md](QUICK_START_A2A.md)** - 5-minute A2A service setup
- **[README_A2A.md](README_A2A.md)** - Complete A2A technical documentation
- **[START_HERE.md](START_HERE.md)** - Deployment guide for cloud platforms
- **[DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)** - Step-by-step deployment instructions
- **[docs/LLM_POWERED_ANALYSIS.md](docs/LLM_POWERED_ANALYSIS.md)** - LLM mode capabilities
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture
- **[docs/A2A_COMPATIBILITY.md](docs/A2A_COMPATIBILITY.md)** - A2A protocol details

## Project Structure

```
agent-hypo/
├── app/                       # A2A HTTP service
│   ├── server.py             # FastAPI server
│   ├── agent.py              # Stateless agent logic
│   ├── models.py             # Request/response schemas
│   └── storage.py            # S3 cloud storage
├── src/white_agent/          # Core analysis engine
│   ├── agent.py              # Traditional WhiteAgent class
│   ├── llm_agent.py          # LLM-powered agent
│   ├── unified_agent.py      # Auto-detecting unified interface
│   ├── analyzer.py           # Statistical methods
│   ├── llm_analyzer.py       # LLM adaptive analysis
│   ├── data_loader.py        # Data parsing
│   └── report_generator.py  # Report generation
├── inputs/                   # Test data (legacy CLI mode)
├── results/                  # Analysis outputs (legacy CLI mode)
├── docs/                     # Technical documentation
├── examples/                 # Usage examples
├── legacy_main.py            # CLI entry point
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container definition
└── .well-known/agent-card.json  # A2A agent card
```

## API Usage

### A2A HTTP Service

```bash
# Health check
curl http://localhost:8000/health

# Run analysis
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "context_url": "https://example.com/context.txt",
    "data_url": "https://example.com/data.csv",
    "mode": "auto"
  }'
```

**Response:**
```json
{
  "status": "success",
  "run_id": "abc-123",
  "mode_used": "llm",
  "analysis_summary": {
    "sample_size": 1000,
    "treatment_effect": 0.1234,
    "p_value": 0.0023,
    "statistically_significant": true
  },
  "outputs": {
    "report_url": "https://...",
    "results_url": "https://...",
    "analysis_code_url": "https://..."
  }
}
```

### Legacy CLI Usage

```bash
# Analyze latest test
python legacy_main.py

# Analyze specific test
python legacy_main.py --test-index 1

# List available tests
python legacy_main.py --list
```

### Programmatic Usage

```python
from white_agent.unified_agent import UnifiedWhiteAgent

# Auto-detects LLM mode if GEMINI_API_KEY is set
agent = UnifiedWhiteAgent(
    inputs_dir="inputs",
    results_dir="results"
)

# Process a test
results = agent.process_test(test_index=1)
print(f"Using LLM mode: {agent.is_llm_powered}")
```

See [examples/llm_mode_example.py](examples/llm_mode_example.py) for more examples.

## Data Format

**A2A Service:** Provide URLs to context and data files in the request.

**Legacy CLI:** Place files in `inputs/test_X/` directory:
- **Context file** (`.txt` or `.md`): Experiment description
- **Data file** (`.csv`, `.json`, `.parquet`, or `.xlsx`): Must contain:
  - Binary treatment variable (0/1)
  - Continuous outcome variable
  - Optional covariates

Example data:
```csv
treatment,outcome,age,gender
0,42.3,25,F
1,45.1,28,M
```

## Output Format

**A2A Service:** Results uploaded to S3 with URLs in response.

**Legacy CLI:** Results in `results/result_X_Y/`:
- `data_source/` - Copy of input data
- `code/analysis.py` - Reproducible analysis script
- `report/analysis_report.md` - Detailed findings
- `report/results.json` - Structured results
- `metadata.json` - Run metadata

## Statistical Methods

The agent performs:
- **Average Treatment Effect (ATE)**: Difference in means with confidence intervals
- **Hypothesis Testing**: t-tests and Mann-Whitney U tests
- **Regression Analysis**: Linear regression with/without covariates
- **Covariate Balance**: Randomization quality checks
- **Effect Sizes**: Cohen's d calculations
- **Report Generation**: Executive summary, findings, recommendations

See [docs/LLM_POWERED_ANALYSIS.md](docs/LLM_POWERED_ANALYSIS.md) for LLM-enhanced analysis capabilities.

## Configuration

### Environment Variables (A2A Service)
```bash
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY_ID=your-key
S3_SECRET_ACCESS_KEY=your-secret
GEMINI_API_KEY=your-gemini-key  # Optional, for LLM mode
```

### Environment Variables (Legacy CLI)
```bash
GEMINI_API_KEY=your-gemini-key  # Optional, for LLM mode
```

## Deployment

### Docker
```bash
docker build -t white-agent .
docker run -p 8000:8000 --env-file .env white-agent
```

### Cloud Platforms
See [START_HERE.md](START_HERE.md) and [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) for:
- Render, Railway, Fly.io
- AWS ECS/Fargate
- Google Cloud Run

## Troubleshooting

**"No data file found"**
- Ensure data file has correct extension (`.csv`, `.json`, `.parquet`, or `.xlsx`)

**"Could not identify treatment and outcome variables"**
- Verify binary treatment column (0/1) and continuous outcome column exist
- Check variable naming conventions

**"Storage/S3 errors"**
- Verify S3 credentials in `.env`
- Check bucket permissions and network connectivity

**"LLM mode not working"**
- Set `GEMINI_API_KEY` in environment or use `"mode": "traditional"` in requests
- Agent automatically falls back to traditional mode if LLM unavailable

## License

MIT License - Built for CS 294 (Agent-to-Agent Systems)
