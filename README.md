# White Agent - RCT Analysis

An autonomous agent for analyzing randomized controlled trials (RCTs) and A/B tests, built for CS 294 and compatible with the AgentBeats platform.

## Overview

The White Agent is an A2A (Agent-to-Agent) compatible system that performs comprehensive statistical analysis on experimental data. It can be triggered by a Green Agent orchestrator and autonomously analyzes RCT data, generates reports, and provides actionable insights.

### Key Features

- **Automated Data Analysis**: Processes CSV, JSON, Parquet, and Excel data files
- **Comprehensive Statistics**: Calculates ATE, p-values, confidence intervals, effect sizes, and regression models
- **Covariate Balance Checking**: Verifies randomization quality
- **LLM-Powered Reports**: Uses Gemini API to generate detailed analysis reports
- **Reproducible Code**: Automatically generates Python code to reproduce analyses
- **A2A Compatible**: Integrates with AgentBeats platform for multi-agent workflows
- **Version Control**: Maintains multiple analysis versions for the same dataset

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd agent-hypo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install with development tools:
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

3. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env and add your Gemini API key if you want LLM-powered reports
```

**Note**: The agent works without an API key - it will use template-based reports instead of LLM-generated ones. See [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) for details.

## Project Structure

```
agent-hypo/
├── inputs/                    # Input test directories
│   ├── test_1/
│   │   ├── context.txt       # Experiment description
│   │   └── data.csv          # Experimental data
│   ├── test_2/
│   └── ...
├── results/                   # Analysis results
│   ├── result_1_1/
│   │   ├── data_source/      # Copy of input data
│   │   ├── code/             # Reproducible analysis code
│   │   ├── report/           # Analysis reports (MD + JSON)
│   │   └── metadata.json     # Run metadata
│   └── ...
├── src/
│   ├── white_agent/          # Core agent implementation
│   │   ├── agent.py          # Main WhiteAgent class
│   │   ├── analyzer.py       # Statistical analysis
│   │   ├── data_loader.py    # Data file parsing
│   │   ├── report_generator.py  # LLM report generation
│   │   └── utils.py          # Utility functions
│   └── launcher.py           # AgentBeats launcher
├── white_agent_card.toml     # AgentBeats configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Usage

### Quick Start (Recommended)

Run analysis on the latest test or a specific test:

```bash
# Analyze the latest test automatically
python main.py

# Analyze a specific test
python main.py --test-index 1

# List available tests
python main.py --list
```

### Standalone Mode (Interactive)

Run the agent in standalone mode for development and testing:

```bash
python src/launcher.py --mode standalone
```

Commands:
- `analyze <test_index>` - Analyze a specific test
- `status` - Check agent status
- `reset` - Reset agent state
- `quit` - Exit

Example:
```
> analyze 1
Analyzing test_1...
Analysis complete!
{
  "test_index": 1,
  "result_version": 1,
  "output_dir": "results/result_1_1",
  ...
}
```

### Server Mode (A2A Protocol)

Run as an A2A server for AgentBeats integration:

```bash
python src/launcher.py --mode server --agent-port 8001
```

This starts a FastAPI server with the following endpoints:
- `POST /a2a/analyze` - Process analysis requests
- `GET /a2a/status` - Check agent status
- `POST /a2a/reset` - Reset agent state
- `GET /health` - Health check

### Programmatic Usage

```python
from white_agent import WhiteAgent

# Initialize agent
agent = WhiteAgent(
    inputs_dir="inputs",
    results_dir="results"
)

# Process a test
results = agent.process_test(test_index=1)

print(f"Analysis saved to: {results['output_dir']}")
print(f"ATE: {results['analysis_summary']['treatment_effect']}")
print(f"p-value: {results['analysis_summary']['p_value']}")
```

### A2A Message Protocol

Send A2A messages to the agent:

```python
# Analyze a test
response = agent.handle_a2a_message({
    "action": "analyze_test",
    "params": {
        "test_index": 1
    }
})

# Check status
response = agent.handle_a2a_message({
    "action": "get_status"
})
```

## Input Format

Each test should be in a directory named `test_X` (e.g., `test_1`, `test_12`) containing:

1. **Context File** (`.txt` or `.md`):
   - Description of the experiment
   - Research question and objectives
   - Study design details
   - Treatment and control definitions
   - Data collection methodology

2. **Data File** (`.csv`, `.json`, `.parquet`, or `.xlsx`):
   - Must contain a binary treatment variable (0/1)
   - Must contain a continuous outcome variable
   - Can include additional covariates
   - Each row represents one experimental unit

Example data structure:
```csv
treatment,outcome,age,gender
0,42.3,25,F
1,45.1,28,M
0,41.8,22,F
1,48.2,30,M
...
```

## Output Format

Results are saved in `results/result_X_Y/` where:
- `X` is the test index
- `Y` is the version number (auto-incremented)

Each result directory contains:

### 1. `data_source/`
Copy of the original data file for reproducibility

### 2. `code/`
- `analysis.py` - Reproducible Python script
- `requirements.txt` - Dependencies for the analysis code

### 3. `report/`
- `analysis_report.md` - Comprehensive analysis report
- `results.json` - Structured results data

### 4. `metadata.json`
Run information and summary statistics

## Statistical Analysis

The agent performs the following analyses:

### 1. Average Treatment Effect (ATE)
- Difference in means between treatment and control
- Standard errors and confidence intervals
- Effect size (Cohen's d)

### 2. Hypothesis Testing
- Two-sample t-test
- Mann-Whitney U test (non-parametric)
- Statistical significance at α=0.05

### 3. Regression Analysis
- Simple linear regression (outcome ~ treatment)
- Multiple regression with covariates (if available)
- R² and coefficient estimates

### 4. Covariate Balance
- Tests whether randomization achieved balance
- Reports p-values for each covariate
- Identifies potential imbalances

### 5. Report Generation
- Executive summary
- Detailed findings
- Threats to validity
- Practical recommendations
- Future improvements

## AgentBeats Integration

The White Agent is designed for the AgentBeats platform:

### Configuration

The agent is configured via [white_agent_card.toml](white_agent_card.toml) which specifies:
- Agent capabilities and role
- Network endpoints
- I/O structure
- LLM settings
- Analysis parameters

### Running with AgentBeats

```bash
# Using agentbeats CLI (if installed)
agentbeats run white_agent_card.toml \
  --launcher_host 0.0.0.0 \
  --launcher_port 8000 \
  --agent_host 0.0.0.0 \
  --agent_port 8001
```

### A2A Protocol

The agent implements standard A2A message handling:

**Request:**
```json
{
  "action": "analyze_test",
  "params": {
    "test_index": 12
  }
}
```

**Response:**
```json
{
  "status": "success",
  "results": {
    "test_index": 12,
    "result_version": 1,
    "analysis_summary": {
      "sample_size": 1000,
      "treatment_effect": 3.45,
      "p_value": 0.001,
      "statistically_significant": true
    }
  }
}
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY` - API key for Gemini LLM (optional)

### Agent Parameters

When initializing the WhiteAgent:
- `inputs_dir` - Path to inputs directory (default: "inputs")
- `results_dir` - Path to results directory (default: "results")
- `gemini_api_key` - Gemini API key (defaults to env var)

### Analysis Parameters

In the RCTAnalyzer:
- `alpha` - Significance level (default: 0.05)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
flake8 src/
```

## Example Workflow

1. **Prepare Input Data**:
   ```bash
   mkdir -p inputs/test_1
   # Add context.txt and data.csv to inputs/test_1/
   ```

2. **Run Analysis**:
   ```bash
   python src/launcher.py --mode standalone
   > analyze 1
   ```

3. **Review Results**:
   ```bash
   cat results/result_1_1/report/analysis_report.md
   python results/result_1_1/code/analysis.py
   ```

4. **Run Again** (creates result_1_2):
   ```
   > analyze 1
   ```

## Troubleshooting

### Issue: "No data file found"
- Ensure your test directory contains a `.csv`, `.json`, `.parquet`, or `.xlsx` file
- Check that the file has the correct extension

### Issue: "Could not identify treatment and outcome variables"
- Verify your data has a binary treatment column (0/1 values)
- Ensure you have a continuous numeric outcome column
- Check variable names for keywords like "treatment", "outcome", etc.

### Issue: "Gemini API error"
- Verify `GEMINI_API_KEY` environment variable is set
- Agent will fall back to template-based reports if LLM is unavailable

### Issue: "Multiple data files found"
- Each test directory should contain only one data file
- Remove or move extra data files

## License

MIT License

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

## Acknowledgments

Built for CS 294 - Agent-to-Agent Systems
Compatible with the AgentBeats platform (https://agentbeats.org)
