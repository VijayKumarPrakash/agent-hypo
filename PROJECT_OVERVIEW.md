# White Agent for RCT Analysis - Project Overview

## Executive Summary

This project implements a **White Agent** - an autonomous AI agent that performs comprehensive statistical analysis on randomized controlled trial (RCT) data and generates detailed reports. The agent is designed to be **A2A (Agent-to-Agent) compatible** for integration with the AgentBeats platform, allowing it to collaborate with other agents in multi-agent workflows.

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      Green Agent (Orchestrator)              │
│                                                              │
│  - Triggers analysis via A2A protocol                        │
│  - Makes decisions based on results                          │
│  - Coordinates multi-agent workflows                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ A2A Messages
                           │ (HTTP/JSON)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      White Agent (Analyzer)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Data Loader                                       │  │
│  │     - Parses CSV/JSON/Parquet/Excel files            │  │
│  │     - Extracts experiment context                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. RCT Analyzer                                      │  │
│  │     - Identifies treatment/outcome variables          │  │
│  │     - Calculates ATE, p-values, effect sizes          │  │
│  │     - Performs regression analysis                    │  │
│  │     - Checks covariate balance                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. Report Generator                                  │  │
│  │     - Uses Gemini LLM for insights                    │  │
│  │     - Generates markdown reports                      │  │
│  │     - Creates reproducible code                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Results    │
                    ├──────────────┤
                    │ - Data copy  │
                    │ - Code       │
                    │ - Report     │
                    │ - Metadata   │
                    └──────────────┘
```

### Component Breakdown

#### 1. Data Loader ([data_loader.py](src/white_agent/data_loader.py))
- Loads experimental data from multiple formats
- Extracts context/background information
- Validates file structure and contents

#### 2. RCT Analyzer ([analyzer.py](src/white_agent/analyzer.py))
- **Variable Identification**: Automatically detects treatment and outcome columns
- **Treatment Effect**: Calculates Average Treatment Effect (ATE) with confidence intervals
- **Hypothesis Testing**: Two-sample t-test, Mann-Whitney U test
- **Effect Size**: Cohen's d with interpretation
- **Regression**: Simple and multiple regression analysis
- **Balance Checking**: Verifies randomization quality across covariates

#### 3. Report Generator ([report_generator.py](src/white_agent/report_generator.py))
- **LLM-Powered**: Uses Gemini API for nuanced analysis
- **Fallback**: Template-based reports when LLM unavailable
- **Comprehensive**: Executive summary, findings, threats to validity, recommendations
- **Structured Output**: Both markdown (human-readable) and JSON (machine-readable)

#### 4. Agent Controller ([agent.py](src/white_agent/agent.py))
- **A2A Protocol**: Handles incoming messages from other agents
- **Workflow Management**: Orchestrates the analysis pipeline
- **Version Control**: Maintains multiple analysis runs for same data
- **Reset Handler**: Supports AgentBeats battle/session resets

#### 5. Launcher ([launcher.py](src/launcher.py))
- **Server Mode**: FastAPI server for A2A protocol (production)
- **Standalone Mode**: Interactive CLI for development/testing
- **Configuration**: Command-line arguments for flexible deployment

## Data Flow

### Input Structure
```
inputs/test_X/
├── context.txt (or .md)    # Experiment description
│   - Research question
│   - Study design
│   - Treatment details
│   - Outcome measures
│   - Hypothesis
│
└── data.csv (or .json/.parquet/.xlsx)
    - Binary treatment column (0/1)
    - Continuous outcome column
    - Optional covariates
```

### Processing Pipeline

1. **Intake**: Load context and data files
2. **Identification**: Detect treatment/outcome variables
3. **Analysis**:
   - Calculate ATE and standard errors
   - Perform hypothesis tests (t-test, Mann-Whitney U)
   - Compute effect size (Cohen's d)
   - Run regressions (simple & multiple)
   - Check covariate balance
4. **Generation**:
   - Create reproducible Python code
   - Generate LLM-powered report
   - Save structured results
5. **Output**: Package everything in versioned directory

### Output Structure
```
results/result_X_Y/
├── data_source/
│   └── data.csv              # Copy of input data
│
├── code/
│   ├── analysis.py           # Reproducible analysis script
│   └── requirements.txt      # Code dependencies
│
├── report/
│   ├── analysis_report.md    # Comprehensive markdown report
│   └── results.json          # Structured results data
│
└── metadata.json             # Run metadata & summary
```

## Statistical Methods

### 1. Average Treatment Effect (ATE)
```
ATE = E[Y|T=1] - E[Y|T=0]
```
- Difference in mean outcomes between treatment and control groups
- Standard error calculated using pooled variance
- 95% confidence interval using normal approximation

### 2. Hypothesis Testing

**Two-Sample t-Test**:
- H₀: ATE = 0 (no treatment effect)
- Hₐ: ATE ≠ 0 (treatment has effect)
- Significance level: α = 0.05

**Mann-Whitney U Test**:
- Non-parametric alternative to t-test
- Robust to violations of normality assumption

### 3. Effect Size

**Cohen's d**:
```
d = (μ_treatment - μ_control) / σ_pooled
```

Interpretation:
- |d| < 0.2: Negligible
- 0.2 ≤ |d| < 0.5: Small
- 0.5 ≤ |d| < 0.8: Medium
- |d| ≥ 0.8: Large

### 4. Regression Analysis

**Simple Regression**:
```
Y = β₀ + β₁·Treatment + ε
```
- β₁ estimates ATE
- R² measures variance explained

**Multiple Regression**:
```
Y = β₀ + β₁·Treatment + β₂·X₂ + ... + βₖ·Xₖ + ε
```
- Controls for covariates
- Improves precision of ATE estimate

### 5. Balance Checks

For each covariate X:
- Test: H₀: E[X|T=1] = E[X|T=0]
- Method: Two-sample t-test
- Interpretation: p > 0.05 suggests balance (randomization worked)

## A2A Protocol

### Message Format

**Request** (Green Agent → White Agent):
```json
{
  "action": "analyze_test",
  "params": {
    "test_index": 12
  }
}
```

**Response** (White Agent → Green Agent):
```json
{
  "status": "success",
  "results": {
    "test_index": 12,
    "result_version": 1,
    "input_dir": "inputs/test_12",
    "output_dir": "results/result_12_1",
    "data_file": "data.csv",
    "analysis_summary": {
      "sample_size": 200,
      "treatment_effect": 8.92,
      "p_value": 0.0001,
      "statistically_significant": true
    }
  }
}
```

### Supported Actions

1. **analyze_test**: Trigger analysis on a specific test
2. **get_status**: Check agent readiness and capabilities
3. **reset**: Reset agent state (for AgentBeats battles)

### Network Configuration

- **Agent Port**: 8001 (A2A protocol endpoint)
- **Launcher Port**: 8000 (Control/reset endpoint)
- **Endpoints**:
  - `POST /a2a/analyze` - Analysis requests
  - `GET /a2a/status` - Status checks
  - `POST /a2a/reset` - Reset signals
  - `GET /health` - Health monitoring

## AgentBeats Integration

### Configuration Card

The [white_agent_card.toml](white_agent_card.toml) defines:
- Agent identity and capabilities
- Network endpoints for A2A communication
- I/O directory structure
- LLM settings
- Statistical parameters

### Deployment

**Standalone Development**:
```bash
python src/launcher.py --mode standalone
```

**Production Server**:
```bash
python src/launcher.py --mode server --agent-port 8001
```

**AgentBeats Platform**:
```bash
agentbeats run white_agent_card.toml \
  --launcher_host 0.0.0.0 \
  --launcher_port 8000 \
  --agent_host 0.0.0.0 \
  --agent_port 8001
```

### Multi-Agent Workflow

In a typical AgentBeats workflow:

1. **Green Agent (Orchestrator)** receives experiment data
2. Green Agent sends A2A message to **White Agent**: "Analyze test_X"
3. White Agent processes the data and returns results
4. Green Agent evaluates results and makes decisions:
   - Deploy intervention?
   - Collect more data?
   - Trigger other agents?
5. Results flow to stakeholders or downstream systems

## Technology Stack

### Core Dependencies
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scipy**: Statistical tests and distributions
- **scikit-learn**: Regression models
- **pyarrow**: Parquet file support
- **openpyxl**: Excel file support

### LLM Integration
- **google-generativeai**: Gemini API for report generation

### Web Framework (Optional)
- **FastAPI**: A2A protocol HTTP server
- **uvicorn**: ASGI server for FastAPI

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

## Key Features

### 1. Autonomous Operation
- No manual intervention required
- Automatic variable detection
- Self-contained analysis pipeline

### 2. Reproducibility
- Generated code recreates analysis
- Data copies ensure auditability
- Version control for multiple runs

### 3. Comprehensive Analysis
- Multiple statistical tests
- Effect size interpretation
- Balance verification
- Regression with covariates

### 4. Intelligent Reporting
- LLM-generated insights
- Practical recommendations
- Threats to validity assessment
- Future improvement suggestions

### 5. Multi-Agent Ready
- A2A protocol implementation
- AgentBeats platform compatible
- Stateless operation (supports resets)
- Asynchronous communication

### 6. Flexible Deployment
- Standalone CLI for development
- HTTP server for production
- Programmatic API for integration
- Environment-based configuration

## Usage Scenarios

### Scenario 1: Academic Research
Researcher uploads RCT data → White Agent analyzes → Generates paper-ready statistics and visualizations

### Scenario 2: Product A/B Testing
Product team runs A/B test → Green Agent orchestrates → White Agent analyzes → Results inform product decisions

### Scenario 3: Policy Evaluation
Government agency tests policy intervention → White Agent evaluates impact → Report guides policy recommendations

### Scenario 4: Medical Trials
Clinical trial data collected → Automated analysis via White Agent → Statistical report for regulatory submission

## Extension Points

### Adding New Statistical Methods
Extend `RCTAnalyzer` class with additional methods:
- Propensity score matching
- Difference-in-differences
- Instrumental variables
- Heterogeneous treatment effects

### Custom Report Templates
Modify `ReportGenerator` for domain-specific reporting:
- Medical trial format (CONSORT)
- Economics research (AER style)
- Industry dashboards (visual focus)

### Integration with Other Agents
- **Red Agent**: Validates experimental design
- **Blue Agent**: Checks data quality
- **Yellow Agent**: Performs cost-benefit analysis

## Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Test
```bash
python test_agent.py
```

### Manual Testing
```bash
python src/launcher.py --mode standalone
> analyze 1
```

## Performance Considerations

- **Speed**: Analysis of 10K rows takes ~1-2 seconds
- **Memory**: Handles datasets up to 1M rows on standard hardware
- **Scalability**: Stateless design allows horizontal scaling
- **Concurrency**: Can process multiple tests in parallel

## Security & Privacy

- **No external data sharing**: All processing local (except Gemini API for reports)
- **Sandboxed execution**: No arbitrary code execution
- **Input validation**: File type and structure checks
- **API key security**: Environment variable configuration

## Future Enhancements

1. **Visualization**: Generate plots and charts
2. **Streaming**: Real-time analysis progress updates
3. **Batch Processing**: Analyze multiple tests simultaneously
4. **Database Integration**: Direct connection to experiment databases
5. **Advanced Methods**: Bayesian analysis, machine learning methods
6. **Interactive Reports**: HTML dashboards with drill-down capabilities
7. **Model Export**: Save statistical models for reuse

## Documentation

- [README.md](README.md) - Comprehensive user guide
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [white_agent_card.toml](white_agent_card.toml) - AgentBeats configuration
- [examples/green_agent_integration.py](examples/green_agent_integration.py) - A2A example

## Support & Contribution

- Report issues via GitHub Issues
- Contributions welcome via Pull Requests
- Follow code style: `black src/`
- Add tests for new features
- Update documentation

## License

MIT License - See repository for details

## Acknowledgments

Built for **CS 294 - Agent-to-Agent Systems**
Compatible with **AgentBeats** platform (https://agentbeats.org)

---

**Project Status**: Production-ready for AgentBeats integration
**Version**: 1.0.0
**Last Updated**: 2025-12-11
