# How to Run the White Agent

## Quick Start (3 Commands)

### 1. Set Your API Key (Optional but Recommended)
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

**Get a key:** https://makersuite.google.com/app/apikey

**Note:** Without an API key, the agent uses traditional mode (works fine for standardized CSV data).

### 2. Run the Analysis
```bash
python main.py
```

This analyzes the latest test in `inputs/` directory.

### 3. View Results
```bash
cat results/result_1_1/report/analysis_report.md
```

That's it! 🎉

---

## Command Line Options

### Basic Usage

```bash
# Analyze latest test (auto-detects mode)
python main.py

# Analyze specific test
python main.py --test-index 1

# List available tests
python main.py --list

# Show help
python main.py --help
```

### Mode Selection

```bash
# Auto mode (default) - uses LLM if API key available
python main.py --mode auto

# Force LLM mode (requires API key)
python main.py --mode llm

# Force traditional mode (no API key needed)
python main.py --mode traditional
```

### Custom Directories

```bash
python main.py --inputs-dir my_inputs --results-dir my_results
```

### Verbose Output

```bash
python main.py --verbose
python main.py -v  # short form
```

---

## Analysis Modes

### 🤖 LLM-Powered Mode (Recommended)

**When to use:**
- Working with diverse data formats
- Variable names are inconsistent
- Experimental design varies
- Want maximum flexibility

**Requires:**
- GEMINI_API_KEY environment variable

**Benefits:**
- ✅ Works with ANY file format (CSV, JSON, Excel, Parquet, TSV, etc.)
- ✅ Handles ANY variable naming
- ✅ Auto-identifies treatment/outcome/covariates
- ✅ Adapts to your experiment type
- ✅ Zero configuration needed

**Cost:** ~$0.06 per analysis
**Speed:** 10-30 seconds

**Example:**
```bash
export GEMINI_API_KEY="your-key"
python main.py --test-index 1
```

### 📊 Traditional Mode

**When to use:**
- Data is standardized CSV format
- Variable names follow conventions
- Want faster analysis
- Don't want to use API

**Benefits:**
- ✅ Fast (2-5 seconds)
- ✅ Free (no API costs)
- ✅ No internet required
- ✅ Reliable for standard data

**Limitations:**
- ❌ Only works with standard CSV
- ❌ Requires specific variable naming
- ❌ Less flexible with data structure

**Example:**
```bash
python main.py --mode traditional --test-index 1
```

---

## Input File Structure

Your test directory should look like:

```
inputs/test_1/
├── context.txt      # Experiment description
└── data.csv         # Your data (or .json, .xlsx, .parquet, etc.)
```

### Context File

Can be named:
- `context.txt`, `context.md`
- `README.md`, `readme.txt`
- `description.txt`, `experiment.txt`

Should contain:
- What the experiment is about
- What the treatment was
- What you measured
- Any relevant details

**Example:**
```text
We ran a randomized trial where customers were randomly assigned to either
the standard checkout flow (control) or a new one-click checkout (treatment).
We measured conversion rate as the primary outcome. The experiment ran for
2 weeks with 10,000 users.
```

### Data File

**LLM mode accepts:**
- CSV (any delimiter)
- JSON (any structure)
- Excel (.xlsx, .xls)
- Parquet
- TSV
- And more...

**Traditional mode requires:**
- CSV format
- Standard delimiters
- Clear variable names

---

## Output Structure

Results are saved to `results/result_N_V/` where:
- `N` = test index
- `V` = version number (auto-incremented)

```
results/result_1_1/
├── data_source/
│   └── data.csv              # Copy of original data
├── code/
│   ├── analysis.py           # Reproducible Python code
│   └── requirements.txt      # Dependencies
├── report/
│   ├── analysis_report.md    # Main report
│   └── results.json          # Structured results
└── metadata.json             # Run information
```

---

## Environment Variables

Set in your shell or `.env` file:

```bash
# Required for LLM mode
export GEMINI_API_KEY="your-api-key"

# Optional: Custom directories
export WHITE_AGENT_INPUTS_DIR="my_inputs"
export WHITE_AGENT_RESULTS_DIR="my_results"
```

**Using .env file:**
```bash
# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your-api-key
EOF

# Install python-dotenv (if not already installed)
pip install python-dotenv

# Run (automatically loads .env)
python main.py
```

---

## Example Workflows

### Workflow 1: Quick Analysis with LLM Mode

```bash
# Set API key once
export GEMINI_API_KEY="your-key"

# Run analysis
python main.py --test-index 1

# View report
cat results/result_1_1/report/analysis_report.md

# Run reproducible code
python results/result_1_1/code/analysis.py
```

### Workflow 2: Traditional Mode (No API Key)

```bash
# Run analysis
python main.py --mode traditional --test-index 1

# View results
cat results/result_1_1/report/analysis_report.md
```

### Workflow 3: Batch Processing

```bash
# List all tests
python main.py --list

# Process each test
for i in 1 2 3 4 5; do
    python main.py --test-index $i
done

# Compare results
ls -la results/
```

### Workflow 4: Compare Modes

```bash
export GEMINI_API_KEY="your-key"

# Run LLM mode
python main.py --mode llm --test-index 1

# Run traditional mode
python main.py --mode traditional --test-index 1

# Compare results
diff results/result_1_1/report/results.json results/result_1_2/report/results.json
```

---

## Troubleshooting

### "No test directories found"

**Problem:** No tests in inputs directory

**Solution:**
```bash
mkdir -p inputs/test_1
# Add context.txt and data.csv to inputs/test_1/
python main.py --test-index 1
```

### "GEMINI_API_KEY not set" (when using --mode llm)

**Problem:** Trying to force LLM mode without API key

**Solution:**
```bash
export GEMINI_API_KEY="your-key"
python main.py --mode llm --test-index 1
```

Or use auto mode:
```bash
python main.py --test-index 1  # Falls back to traditional
```

### "Could not identify treatment and outcome variables"

**Problem:** Traditional mode can't find variables

**Solution 1 - Use LLM mode:**
```bash
export GEMINI_API_KEY="your-key"
python main.py --test-index 1
```

**Solution 2 - Fix variable names:**
- Rename treatment column to include "treatment", "group", or "condition"
- Rename outcome column to include "outcome", "result", or "value"

### Analysis is slow

**Problem:** LLM mode takes 10-30 seconds

**Solutions:**
- Use traditional mode for faster analysis: `--mode traditional`
- Accept the trade-off (flexibility vs speed)
- Use flash model for data loading (requires code change)

---

## Programmatic Usage

Instead of using `main.py`, you can import and use directly:

```python
from white_agent.unified_agent import UnifiedWhiteAgent

# Initialize (auto-detects mode)
agent = UnifiedWhiteAgent(
    inputs_dir="inputs",
    results_dir="results"
)

# Check mode
print(f"Using LLM mode: {agent.is_llm_powered}")

# Process test
results = agent.process_test(test_index=1)

# Access results
print(f"ATE: {results['analysis_summary']['treatment_effect']:.4f}")
print(f"p-value: {results['analysis_summary']['p_value']:.4f}")
print(f"Output: {results['output_dir']}")
```

**Force specific mode:**
```python
# Force LLM mode
agent = UnifiedWhiteAgent(
    force_mode="llm",
    gemini_api_key="your-key"
)

# Force traditional mode
agent = UnifiedWhiteAgent(
    force_mode="traditional"
)
```

---

## What Happens When You Run?

### LLM Mode

```
1. Find test directory → inputs/test_1/
2. Load context file → context.txt
3. Load data file → Uses LLM if format is unusual
4. Create analysis plan → LLM analyzes context + data
5. Identify variables → Treatment, outcome, covariates
6. Run statistical tests → ATE, t-test, regression, etc.
7. Interpret results → LLM provides interpretation
8. Generate report → Comprehensive markdown report
9. Save outputs → Code, data, metadata, report
10. Display summary → Show key results
```

### Traditional Mode

```
1. Find test directory → inputs/test_1/
2. Load context file → context.txt
3. Load data file → Standard pandas CSV loading
4. Identify variables → Heuristic-based search
5. Run statistical tests → ATE, t-test, regression, etc.
6. Generate report → Template or LLM-based
7. Save outputs → Code, data, metadata, report
8. Display summary → Show key results
```

---

## Next Steps After Running

1. **Read the report:**
   ```bash
   cat results/result_1_1/report/analysis_report.md
   ```

2. **Check the results JSON:**
   ```bash
   cat results/result_1_1/report/results.json | jq .
   ```

3. **Run the analysis code:**
   ```bash
   cd results/result_1_1/code
   pip install -r requirements.txt
   python analysis.py
   ```

4. **Review metadata:**
   ```bash
   cat results/result_1_1/metadata.json | jq .
   ```

---

## Getting Help

```bash
# Show all options
python main.py --help

# Check documentation
cat README.md
cat docs/LLM_POWERED_ANALYSIS.md
cat QUICK_START_LLM.md

# Run examples
python examples/llm_mode_example.py
```

---

## Summary of Commands

| Task | Command |
|------|---------|
| **Quick run** | `python main.py` |
| **Specific test** | `python main.py --test-index 1` |
| **List tests** | `python main.py --list` |
| **Force LLM mode** | `python main.py --mode llm` |
| **Force traditional** | `python main.py --mode traditional` |
| **Verbose output** | `python main.py -v` |
| **Custom dirs** | `python main.py --inputs-dir X --results-dir Y` |
| **Help** | `python main.py --help` |

---

**You're all set!** 🚀

Run `python main.py` to analyze your experimental data.
