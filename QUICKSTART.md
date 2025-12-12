# Quick Start Guide

Get the White Agent up and running in 5 minutes.

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Test with Example Data

The repository includes example test data in `inputs/test_1/`.

Run the analysis:

```bash
python main.py
```

This will automatically analyze the latest test (test_1 in this case).

You should see output like:

```
======================================================================
White Agent - RCT Analysis
======================================================================

Configuration:
  Inputs directory:  inputs
  Results directory: results
  Test index:        1
  LLM mode:          Template-based

Processing test_1...

======================================================================
Analysis Complete!
======================================================================

Results saved to: results/result_1_1
Test index: 1
Result version: 1

Quick Summary:
  Sample size:               200
  Average Treatment Effect:  8.9200
  p-value:                   0.0001
  Statistically significant: True
```

## 3. View the Results

Check the generated report:

```bash
cat results/result_1_1/report/analysis_report.md
```

Or view the structured results:

```bash
cat results/result_1_1/report/results.json
```

Run the generated analysis code:

```bash
cd results/result_1_1/code
python analysis.py
```

## 4. View Metadata

```bash
cat results/result_1_1/metadata.json
```

This shows a summary including:
- Test index
- Result version
- Sample size
- Treatment effect
- p-value
- Statistical significance

## What Just Happened?

The White Agent:
1. Read the experiment context from `inputs/test_1/context.txt`
2. Loaded the data from `inputs/test_1/data.csv`
3. Automatically identified the treatment (`treatment`) and outcome (`test_score`) variables
4. Calculated the Average Treatment Effect (ATE)
5. Performed hypothesis testing (t-test)
6. Calculated effect size (Cohen's d)
7. Ran regression analysis
8. Checked covariate balance
9. Generated a comprehensive markdown report
10. Created reproducible Python code
11. Saved everything to `results/result_1_1/`

## Next Steps

### Add Your Own Data

1. Create a new test directory:
```bash
mkdir -p inputs/test_2
```

2. Add your files:
   - `context.txt` - Description of your experiment
   - `data.csv` - Your experimental data (must have treatment column and outcome column)

3. Analyze:
```
> analyze 2
```

### Run in Server Mode (A2A)

For AgentBeats integration:

```bash
python src/launcher.py --mode server --agent-port 8001
```

Then send A2A requests to `http://localhost:8001/a2a/analyze`

### Use Gemini for Better Reports

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Add it to your `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and set: GEMINI_API_KEY=your_actual_key_here
   ```

3. Run the analysis again:
   ```bash
   python main.py
   ```

The agent will now use Gemini to generate more detailed, nuanced reports. See [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) for details.

### Programmatic Usage

```python
from white_agent import WhiteAgent

agent = WhiteAgent()
results = agent.process_test(1)
print(results)
```

## Common Commands

Using main.py:

- `python main.py` - Analyze latest test
- `python main.py --test-index 1` - Analyze specific test
- `python main.py --list` - List all available tests
- `python main.py --help` - Show all options

Using interactive mode:

```bash
python src/launcher.py --mode standalone
```

Then:
- `analyze <N>` - Analyze test_N
- `status` - Check agent status
- `reset` - Reset agent
- `quit` - Exit

## Troubleshooting

If you get import errors:
```bash
pip install -r requirements.txt
```

If you get "No module named 'white_agent'":
```bash
# Make sure you're in the project root
cd /path/to/agent-hypo
python src/launcher.py --mode standalone
```

## File Structure After Running

```
agent-hypo/
├── inputs/
│   └── test_1/
│       ├── context.txt
│       └── data.csv
└── results/
    └── result_1_1/
        ├── data_source/
        │   └── data.csv
        ├── code/
        │   ├── analysis.py
        │   └── requirements.txt
        ├── report/
        │   ├── analysis_report.md
        │   └── results.json
        └── metadata.json
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check the [white_agent_card.toml](white_agent_card.toml) for AgentBeats configuration
- Review the analysis code to understand the statistical methods
- Integrate with a Green Agent for automated A2A workflows
