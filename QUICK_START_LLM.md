# Quick Start: LLM-Powered White Agent

## 🚀 Get Started in 3 Steps

### 1. Set Your API Key
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

Get your key at: https://makersuite.google.com/app/apikey

### 2. Run Analysis
```bash
python main.py --test-index 1
```

That's it! The agent will:
- ✅ Automatically detect your data format
- ✅ Identify treatment and outcome variables
- ✅ Run appropriate statistical tests
- ✅ Generate a comprehensive report

### 3. Check Results
```bash
cat results/result_1_1/report/analysis_report.md
```

## 📝 Code Examples

### Basic Usage
```python
from white_agent.unified_agent import UnifiedWhiteAgent

agent = UnifiedWhiteAgent()
results = agent.process_test(test_index=1)
print(f"Treatment effect: {results['analysis_summary']['treatment_effect']:.4f}")
```

### Check Which Mode is Active
```python
agent = UnifiedWhiteAgent()
print(f"LLM mode: {agent.is_llm_powered}")
```

### Force Specific Mode
```python
# Force LLM mode
agent = UnifiedWhiteAgent(force_mode="llm", gemini_api_key="your-key")

# Force traditional mode
agent = UnifiedWhiteAgent(force_mode="traditional")
```

### Optimize for Cost/Speed
```python
from white_agent import LLMWhiteAgent

agent = LLMWhiteAgent(
    gemini_api_key="your-key",
    loader_model="gemini-1.5-flash",    # Fast & cheap for loading
    analyzer_model="gemini-1.5-pro",     # Best quality for analysis
    report_model="gemini-1.5-pro"        # Best quality for reports
)
```

## 📊 What Data Formats Work?

**Everything!**

- ✅ CSV (any delimiter: `,` `;` `\t` `|`)
- ✅ JSON (any structure)
- ✅ Excel (.xlsx, .xls)
- ✅ Parquet
- ✅ TSV
- ✅ And more...

No preprocessing needed!

## 🎯 How It Handles Different Variable Names

Your variables can be named **anything**. The LLM will identify them from context:

| Your Variable | LLM Identifies As |
|---------------|-------------------|
| `group`, `condition`, `arm` | Treatment |
| `outcome`, `metric`, `score`, `value` | Outcome |
| `age`, `gender`, `location` | Covariates |

**Treatment values** can be:
- 0/1
- True/False
- "control"/"treatment"
- "A"/"B"
- Anything! The LLM figures it out.

## 📁 Input File Structure

Your test directory should have:

```
inputs/test_1/
├── context.txt      # Experiment description (flexible naming)
└── data.csv         # Your data (any format!)
```

**Context file can be named:**
- `context.txt`, `context.md`
- `README.md`, `readme.txt`
- `description.txt`, `experiment.txt`
- Etc.

**Data file can be:**
- Any supported format
- Any reasonable filename

## 💰 Cost

Approximately **$0.06 per test** with optimized configuration.

For 100 tests: ~$6

## ⚡ Speed

- **Traditional mode**: 2-5 seconds
- **LLM mode**: 10-30 seconds

Trade-off: Slower but works with **any data format**.

## 🔄 Fallback Behavior

**No API key?** → Automatically uses traditional mode

**LLM fails?** → Falls back to heuristic analysis

**Can't load file?** → Clear error message

The system is designed to be robust!

## 📖 Full Documentation

- **[LLM-Powered Analysis Guide](docs/LLM_POWERED_ANALYSIS.md)** - Complete documentation
- **[Examples](examples/llm_mode_example.py)** - Code examples
- **[Summary](REVAMP_SUMMARY.md)** - Technical details

## 🐛 Troubleshooting

### "LLM analyzer requires Gemini API key"
**Solution:** Set `GEMINI_API_KEY` environment variable

### Analysis is slow
**Solution:** Use `gemini-1.5-flash` for data loading:
```python
agent = LLMWhiteAgent(loader_model="gemini-1.5-flash")
```

### High API costs
**Solution:** Use traditional mode for standardized data:
```python
agent = UnifiedWhiteAgent(force_mode="traditional")
```

### LLM misidentified variables
**Solution:**
1. Add more detail to your context file
2. Use more descriptive variable names
3. Check `analysis_plan` in results to verify

## 🎓 Learn More

### Compare Modes
```python
# Run both modes on same data
traditional = UnifiedWhiteAgent(force_mode="traditional")
llm = UnifiedWhiteAgent(force_mode="llm")

t_results = traditional.process_test(1)
l_results = llm.process_test(1)

print(f"Traditional ATE: {t_results['analysis_summary']['treatment_effect']}")
print(f"LLM ATE: {l_results['analysis_summary']['treatment_effect']}")
```

### Run Examples
```bash
python examples/llm_mode_example.py
```

## 💡 Best Practices

### 1. Write Good Context
```text
GOOD:
"Randomized trial where customers were assigned to standard checkout (control)
or one-click checkout (treatment). Measured conversion rate over 2 weeks
with 10,000 users."

POOR:
"Experiment data"
```

### 2. Review Analysis Plans
```python
results = agent.process_test(1)
print(json.dumps(results.get('analysis_plan'), indent=2))
```

### 3. Start Small
Test with a small dataset first to verify everything works.

### 4. Monitor Costs
Keep track of API usage if running many analyses.

## ✅ What's Different from Traditional Mode?

| Feature | Traditional | LLM-Powered |
|---------|------------|-------------|
| Data Format | CSV only | Any format |
| Variable Names | Must match patterns | Any naming |
| Setup | Some config needed | Zero config |
| Speed | Fast (2-5s) | Slower (10-30s) |
| Cost | Free | ~$0.06/test |
| Robustness | Medium | High |

## 🎉 You're Ready!

```bash
export GEMINI_API_KEY="your-key"
python main.py --test-index 1
```

Check `results/result_1_1/report/analysis_report.md` for your analysis!

---

**Need help?** See [docs/LLM_POWERED_ANALYSIS.md](docs/LLM_POWERED_ANALYSIS.md)
