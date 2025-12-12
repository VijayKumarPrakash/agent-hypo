# LLM-Powered Analysis Mode

The White Agent now includes a powerful LLM-powered analysis mode that can robustly handle diverse data formats and structures without manual configuration.

## Overview

The LLM-powered mode uses Google's Gemini API throughout the entire analysis pipeline:

1. **Intelligent Data Loading** - Automatically detects and parses various file formats
2. **Context-Aware Variable Identification** - Uses experiment context to identify treatment and outcome variables
3. **Adaptive Statistical Analysis** - Selects appropriate methods based on data structure
4. **Comprehensive Reporting** - Generates detailed, context-specific reports

## Why LLM-Powered Mode?

Traditional statistical analysis tools require:
- Consistent data formats
- Pre-defined variable names
- Manual configuration for each dataset
- Assumptions about data structure

The LLM-powered mode handles:
- **Varying file formats** (CSV, JSON, Excel, Parquet, TSV, etc.)
- **Different delimiters and encodings**
- **Inconsistent variable naming** (treatment vs. group vs. condition)
- **Different treatment encodings** (0/1, True/False, "control"/"treatment")
- **Multiple experimental designs** (RCT, A/B tests, observational studies)
- **Missing or incomplete context information**

## Architecture

### 1. LLMDataLoader
**File**: [llm_data_loader.py](../src/white_agent/llm_data_loader.py)

Intelligently loads data files:
- Tries standard pandas methods first (fast path)
- Uses LLM to understand unusual formats if standard loading fails
- Validates data quality and fixes issues
- Adapts to different file structures

```python
from white_agent import LLMDataLoader

loader = LLMDataLoader(api_key="your-gemini-key")
context, data_df, data_path = loader.load_test_data(test_dir)
```

### 2. LLMAnalyzer
**File**: [llm_analyzer.py](../src/white_agent/llm_analyzer.py)

Performs context-aware analysis:
- Creates analysis plan based on context and data structure
- Identifies treatment, outcome, and covariate variables
- Selects appropriate statistical methods
- Executes analysis and interprets results

```python
from white_agent import LLMAnalyzer

analyzer = LLMAnalyzer(api_key="your-gemini-key")
results = analyzer.analyze_experiment(data_df, context)
```

### 3. Enhanced ReportGenerator
**File**: [report_generator.py](../src/white_agent/report_generator.py)

Generates reports with awareness of LLM analysis:
- Includes information about how variables were identified
- Explains the adaptive analysis approach
- Provides context-specific interpretations

### 4. LLMWhiteAgent
**File**: [llm_agent.py](../src/white_agent/llm_agent.py)

Unified LLM-powered agent:
- Orchestrates the entire pipeline
- Maintains consistency with original WhiteAgent API
- Provides enhanced metadata about analysis

## Usage

### Quick Start

```python
from white_agent import LLMWhiteAgent

# Initialize with API key
agent = LLMWhiteAgent(
    inputs_dir="inputs",
    results_dir="results",
    gemini_api_key="your-gemini-api-key"
)

# Process a test
results = agent.process_test(test_index=1)
```

### Using UnifiedWhiteAgent (Recommended)

The `UnifiedWhiteAgent` automatically selects the best mode:

```python
from white_agent.unified_agent import UnifiedWhiteAgent

# Auto-detects mode based on API key availability
agent = UnifiedWhiteAgent(
    inputs_dir="inputs",
    results_dir="results"
)

# Will use LLM mode if GEMINI_API_KEY is set, traditional mode otherwise
results = agent.process_test(test_index=1)

# Check which mode is being used
print(f"Using LLM mode: {agent.is_llm_powered}")
```

### Force Specific Mode

```python
# Force LLM mode
agent = UnifiedWhiteAgent(
    inputs_dir="inputs",
    results_dir="results",
    gemini_api_key="your-key",
    force_mode="llm"
)

# Force traditional mode
agent = UnifiedWhiteAgent(
    inputs_dir="inputs",
    results_dir="results",
    force_mode="traditional"
)
```

## Configuration

### Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### Model Selection

You can customize which Gemini models to use:

```python
agent = LLMWhiteAgent(
    gemini_api_key="your-key",
    analyzer_model="gemini-1.5-pro",      # Best quality for analysis
    loader_model="gemini-1.5-flash",       # Fast for data loading
    report_model="gemini-1.5-pro"          # Best quality for reports
)
```

**Model Recommendations**:
- `gemini-1.5-pro` - Best quality, slower, more expensive (recommended for analysis & reports)
- `gemini-1.5-flash` - Fast, cheaper, good quality (recommended for data loading)

## Supported Data Formats

The LLM-powered mode can handle:

### File Formats
- CSV (with various delimiters: `,`, `;`, `\t`, `|`)
- TSV (tab-separated values)
- JSON (various orientations: records, columns, index)
- Excel (.xlsx, .xls)
- Parquet
- Feather
- HDF5 (.h5, .hdf5)
- Plain text with custom delimiters

### Data Structures
- Binary treatment (0/1, True/False, "control"/"treatment")
- Multi-arm experiments (multiple treatment levels)
- Different outcome types (continuous, binary, count)
- Various covariate structures

### Variable Naming
The LLM can identify variables regardless of naming:
- Treatment: `treatment`, `group`, `condition`, `arm`, `assigned`, etc.
- Outcome: `outcome`, `result`, `y`, `response`, `score`, `value`, etc.
- Can handle non-standard names with context clues

## How It Works

### Analysis Pipeline

```
1. Data Loading
   ├─ Find data file in test directory
   ├─ Try standard pandas methods
   ├─ If fails → Ask LLM how to load
   └─ Validate and fix data issues

2. Analysis Planning
   ├─ Send data sample + context to LLM
   ├─ LLM identifies:
   │  ├─ Experiment type (RCT, A/B test, etc.)
   │  ├─ Treatment variable and values
   │  ├─ Outcome variable
   │  ├─ Covariates and their roles
   │  └─ Appropriate statistical methods
   └─ Create structured analysis plan

3. Statistical Analysis
   ├─ Execute analysis based on LLM plan
   ├─ Calculate treatment effects
   ├─ Perform hypothesis tests
   ├─ Run regression analyses
   └─ Check covariate balance

4. Result Interpretation
   ├─ Send results back to LLM
   ├─ LLM provides context-aware interpretation
   └─ Generate actionable recommendations

5. Report Generation
   ├─ Create comprehensive markdown report
   ├─ Include analysis plan details
   └─ Explain adaptive approach
```

### Example: Variable Identification

Given this data with unusual naming:

```csv
user_segment,conversion_rate,age,country
A,0.045,25,US
B,0.052,28,UK
A,0.041,22,US
B,0.058,30,FR
```

And this context:

```
We ran an experiment where users were randomly assigned to segment A (control)
or segment B (new feature). We measured conversion rates.
```

The LLM will:
1. Identify `user_segment` as the treatment variable (from context clues)
2. Identify `conversion_rate` as the outcome (from context + variable name)
3. Identify `A` as control and `B` as treatment
4. Recognize `age` and `country` as covariates
5. Select appropriate methods for continuous outcome

## Benefits

### 1. Robustness
- Works with messy, real-world data
- Handles format inconsistencies
- Adapts to different experimental designs

### 2. Flexibility
- No need to standardize data formats
- Works with various naming conventions
- Supports multiple experimental paradigms

### 3. Intelligence
- Context-aware variable identification
- Appropriate method selection
- Meaningful interpretations

### 4. Ease of Use
- No manual configuration required
- No data preprocessing needed
- Just provide context and data

## Limitations

### 1. Requires API Key
- Needs Gemini API access
- Incurs API costs
- Requires internet connection

### 2. LLM Accuracy
- LLM may occasionally misidentify variables
- Important to review analysis plan in results
- Can fall back to heuristics if needed

### 3. Cost Considerations
- API calls can add up with large datasets
- Using `gemini-1.5-flash` for data loading reduces costs
- Consider traditional mode for simple, standardized datasets

### 4. Speed
- Slower than traditional mode (LLM calls take time)
- Can be optimized with model selection
- Trade-off between speed and flexibility

## Cost Estimation

Approximate costs per analysis (as of 2024):

**Using gemini-1.5-pro for all steps:**
- Data loading: ~$0.01
- Analysis planning: ~$0.02
- Result interpretation: ~$0.01
- Report generation: ~$0.03
- **Total: ~$0.07 per test**

**Using optimized configuration:**
- Data loading (flash): ~$0.001
- Analysis planning (pro): ~$0.02
- Result interpretation (pro): ~$0.01
- Report generation (pro): ~$0.03
- **Total: ~$0.06 per test**

For large-scale analysis (100+ tests), consider:
- Batch processing
- Caching common patterns
- Using traditional mode for standardized datasets

## Comparison: Traditional vs LLM-Powered

| Feature | Traditional Mode | LLM-Powered Mode |
|---------|-----------------|------------------|
| **Data Format** | Must be standardized | Any format |
| **Variable Names** | Must match patterns | Any naming |
| **Configuration** | Manual setup | Automatic |
| **Speed** | Fast | Slower (LLM calls) |
| **Cost** | Free | ~$0.06 per test |
| **Flexibility** | Limited | High |
| **Robustness** | Requires clean data | Handles messy data |
| **API Key Required** | No (optional) | Yes |

## Best Practices

### 1. Provide Good Context
The more context you provide, the better the LLM can understand your experiment:

```text
GOOD CONTEXT:
We ran a randomized controlled trial where customers were randomly assigned
to receive either the standard checkout flow (control) or a new one-click
checkout option (treatment). We measured conversion rate as the primary
outcome. The experiment ran for 2 weeks with 10,000 users.

POOR CONTEXT:
Experiment data.
```

### 2. Review Analysis Plans
Check the `analysis_plan` in results to ensure variables were identified correctly:

```python
results = agent.process_test(test_index=1)
print(json.dumps(results['analysis_plan'], indent=2))
```

### 3. Start with Small Tests
Test the LLM mode with a small dataset first to ensure it works correctly.

### 4. Use Appropriate Models
- Use `flash` for data loading (fast, cheap)
- Use `pro` for analysis and reports (better quality)

### 5. Monitor Costs
Keep track of API usage, especially with large datasets.

## Troubleshooting

### Issue: "LLM analyzer requires Gemini API key"
**Solution**: Set the `GEMINI_API_KEY` environment variable or pass `gemini_api_key` parameter.

### Issue: LLM misidentifies variables
**Solution**:
1. Improve context description
2. Use more descriptive variable names
3. Check analysis plan in results
4. Fall back to traditional mode if needed

### Issue: Analysis is too slow
**Solution**:
1. Use `gemini-1.5-flash` for faster processing
2. Consider traditional mode for simple datasets
3. Reduce data sample size sent to LLM

### Issue: High API costs
**Solution**:
1. Use optimized model configuration
2. Use traditional mode for standardized datasets
3. Batch process multiple tests
4. Reduce context length if very long

## Migration Guide

### From Traditional to LLM-Powered

**Before:**
```python
from white_agent import WhiteAgent

agent = WhiteAgent()
results = agent.process_test(1)
```

**After:**
```python
from white_agent.unified_agent import UnifiedWhiteAgent

# Automatically uses LLM mode if API key is available
agent = UnifiedWhiteAgent()
results = agent.process_test(1)
```

### Gradual Migration

You can run both modes side-by-side:

```python
from white_agent import WhiteAgent, LLMWhiteAgent

# Traditional mode
traditional_agent = WhiteAgent()
traditional_results = traditional_agent.process_test(1)

# LLM mode
llm_agent = LLMWhiteAgent(gemini_api_key="your-key")
llm_results = llm_agent.process_test(1)

# Compare results
print("Traditional ATE:", traditional_results['analysis_summary']['treatment_effect'])
print("LLM ATE:", llm_results['analysis_summary']['treatment_effect'])
```

## Future Enhancements

Planned improvements:
- Support for additional LLM providers (Anthropic Claude, OpenAI GPT)
- Caching and optimization for repeated analyses
- Interactive mode for ambiguous datasets
- Multi-modal analysis (handling images, documents)
- Advanced causal inference methods
- Automated sensitivity analysis

## Getting Help

- Check [main README](../README.md) for general setup
- See [examples](../examples/) for usage examples
- Review generated reports for analysis details
- Check `metadata.json` for analysis information

## API Reference

See inline documentation in:
- [llm_data_loader.py](../src/white_agent/llm_data_loader.py)
- [llm_analyzer.py](../src/white_agent/llm_analyzer.py)
- [llm_agent.py](../src/white_agent/llm_agent.py)
- [unified_agent.py](../src/white_agent/unified_agent.py)
