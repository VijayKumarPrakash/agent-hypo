# White Agent Architecture

## System Overview

The White Agent now supports two analysis modes with a unified interface:

```
                          ┌─────────────────────────┐
                          │   UnifiedWhiteAgent     │
                          │  (Auto-mode selection)  │
                          └────────────┬────────────┘
                                       │
                        ┌──────────────┴───────────────┐
                        │                              │
                        ▼                              ▼
            ┌───────────────────┐          ┌──────────────────────┐
            │  Traditional Mode │          │   LLM-Powered Mode   │
            │   WhiteAgent      │          │   LLMWhiteAgent      │
            └───────────────────┘          └──────────┬───────────┘
                                                      │
                                          ┌───────────┼───────────┐
                                          │           │           │
                                          ▼           ▼           ▼
                                    ┌─────────┐ ┌─────────┐ ┌─────────┐
                                    │   LLM   │ │   LLM   │ │ Report  │
                                    │  Data   │ │ Analyzer│ │   Gen   │
                                    │ Loader  │ │         │ │         │
                                    └─────────┘ └─────────┘ └─────────┘
```

## LLM-Powered Pipeline

### End-to-End Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                         INPUT: Test Directory                          │
│                    inputs/test_N/{context.txt, data.???}               │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STEP 1: DATA LOADING (LLMDataLoader)                                 │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ 1. Find context file (flexible naming)                           │ │
│  │ 2. Find data file (any format)                                   │ │
│  │ 3. Try standard pandas load (fast path)                          │ │
│  │ 4. If fails → Ask LLM how to load                                │ │
│  │ 5. Validate & fix data quality issues                            │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  Output: context (str), data (DataFrame), path (Path)                 │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STEP 2: ANALYSIS PLANNING (LLMAnalyzer)                              │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ LLM receives:                                                     │ │
│  │   - Experiment context                                            │ │
│  │   - Data sample (100 rows)                                        │ │
│  │   - Column names & types                                          │ │
│  │   - Statistical summary                                           │ │
│  │                                                                    │ │
│  │ LLM returns JSON:                                                 │ │
│  │   {                                                               │ │
│  │     "experiment_type": "RCT",                                     │ │
│  │     "treatment_variable": {                                       │ │
│  │       "column_name": "group",                                     │ │
│  │       "treatment_value": "B",                                     │ │
│  │       "control_value": "A"                                        │ │
│  │     },                                                            │ │
│  │     "outcome_variable": {...},                                    │ │
│  │     "covariates": [...],                                          │ │
│  │     "analysis_methods": ["t-test", "regression", ...]            │ │
│  │   }                                                               │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  Output: Structured analysis plan                                     │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STEP 3: STATISTICAL ANALYSIS (LLMAnalyzer)                           │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Based on analysis plan, execute:                                 │ │
│  │                                                                    │ │
│  │ 1. Treatment Effect Estimation                                    │ │
│  │    - Separate treatment/control groups                            │ │
│  │    - Calculate ATE, SE, CI                                        │ │
│  │                                                                    │ │
│  │ 2. Hypothesis Testing                                             │ │
│  │    - t-test (parametric)                                          │ │
│  │    - Mann-Whitney (non-parametric)                                │ │
│  │    - Effect size (Cohen's d)                                      │ │
│  │                                                                    │ │
│  │ 3. Regression Analysis                                            │ │
│  │    - Simple regression (outcome ~ treatment)                      │ │
│  │    - Multiple regression (with covariates)                        │ │
│  │                                                                    │ │
│  │ 4. Covariate Balance                                              │ │
│  │    - Test balance on each covariate                               │ │
│  │    - Report balance statistics                                    │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  Output: Statistical results dictionary                               │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STEP 4: RESULT INTERPRETATION (LLMAnalyzer)                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ LLM receives:                                                     │ │
│  │   - Original context                                              │ │
│  │   - Analysis plan                                                 │ │
│  │   - Statistical results                                           │ │
│  │                                                                    │ │
│  │ LLM returns:                                                      │ │
│  │   - Natural language interpretation                               │ │
│  │   - Practical implications                                        │ │
│  │   - Key limitations                                               │ │
│  │   - Actionable recommendations                                    │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  Output: Interpretation text                                          │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STEP 5: REPORT GENERATION (ReportGenerator)                          │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Generate comprehensive markdown report with:                      │ │
│  │   - Executive summary                                             │ │
│  │   - Experiment overview                                           │ │
│  │   - Data quality assessment                                       │ │
│  │   - Statistical findings                                          │ │
│  │   - Interpretation (from Step 4)                                  │ │
│  │   - Threats to validity                                           │ │
│  │   - Recommendations                                               │ │
│  │   - Technical details (including how variables were identified)   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  Output: analysis_report.md, results.json                             │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STEP 6: CODE GENERATION (LLMWhiteAgent)                              │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ Generate reproducible Python code:                                │ │
│  │   - Loads data using identified format                            │ │
│  │   - Uses identified variable names                                │ │
│  │   - Reproduces statistical analysis                               │ │
│  │   - Self-documenting with comments                                │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│  Output: analysis.py, requirements.txt                                │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     OUTPUT: Result Directory                           │
│  results/result_N_V/                                                   │
│  ├── data_source/           # Copy of original data                   │
│  ├── code/                  # Reproducible analysis code               │
│  ├── report/                # Comprehensive reports                    │
│  └── metadata.json          # Run information & summary                │
└────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### LLMDataLoader

**Responsibilities:**
- Find and load data files of any format
- Handle encoding and delimiter variations
- Validate data quality
- Fix common data issues

**Key Methods:**
```python
load_test_data(test_dir: Path) -> Tuple[str, pd.DataFrame, Path]
    ├─ _load_context(test_dir) -> str
    ├─ _find_data_file(test_dir) -> Path
    └─ _load_data_file(path, context) -> pd.DataFrame
        ├─ _try_standard_load(path) -> pd.DataFrame
        ├─ _validate_and_fix_data(df) -> pd.DataFrame  [if needed]
        └─ _llm_guided_load(path, context) -> pd.DataFrame  [fallback]
```

**Fallback Strategy:**
```
Standard Load → LLM Guidance → Error
     (fast)       (robust)      (clear message)
```

### LLMAnalyzer

**Responsibilities:**
- Create analysis plan from context + data
- Execute statistical analysis
- Interpret results in context

**Key Methods:**
```python
analyze_experiment(data, context) -> Dict[str, Any]
    ├─ _create_analysis_plan(data, context) -> Dict
    │   └─ LLM returns JSON plan
    ├─ _execute_analysis(data, plan) -> Dict
    │   ├─ _analyze_treatment_effect()
    │   ├─ _perform_hypothesis_tests()
    │   ├─ _regression_analysis()
    │   └─ _check_balance()
    └─ _interpret_results(context, plan, results) -> str
        └─ LLM provides interpretation
```

**Analysis Plan Structure:**
```json
{
  "experiment_type": "RCT | A/B test | observational study",
  "treatment_variable": {
    "column_name": "exact column name",
    "description": "what this represents",
    "type": "binary | categorical | continuous",
    "treatment_value": "value for treatment group",
    "control_value": "value for control group"
  },
  "outcome_variable": {
    "column_name": "exact column name",
    "description": "what this measures",
    "type": "continuous | binary | categorical | count"
  },
  "covariates": [
    {
      "column_name": "covariate name",
      "description": "what this represents",
      "type": "continuous | categorical | binary",
      "role": "confounder | mediator | precision variable"
    }
  ],
  "analysis_methods": ["t-test", "regression", "balance-check", ...],
  "potential_issues": ["list of data quality concerns"],
  "recommended_approach": "detailed analysis strategy"
}
```

### LLMWhiteAgent

**Responsibilities:**
- Orchestrate entire pipeline
- Manage component interactions
- Generate outputs

**Pipeline:**
```python
process_test(test_index: int) -> Dict[str, Any]
    1. Load data (LLMDataLoader)
    2. Create output directory
    3. Copy data source
    4. Analyze (LLMAnalyzer)
    5. Generate code
    6. Generate report (ReportGenerator)
    7. Save metadata
    8. Return results
```

### UnifiedWhiteAgent

**Responsibilities:**
- Auto-detect best mode
- Provide unified interface
- Handle mode switching

**Logic:**
```python
if force_mode == "llm":
    use LLMWhiteAgent
elif force_mode == "traditional":
    use WhiteAgent
else:
    if api_key_available:
        use LLMWhiteAgent
    else:
        use WhiteAgent (traditional)
```

## Data Flow Diagram

```
┌─────────┐
│  User   │
└────┬────┘
     │ process_test(1)
     ▼
┌─────────────────────┐
│ UnifiedWhiteAgent   │
└────┬────────────────┘
     │ Detect mode
     ▼
┌─────────────────────┐
│  LLMWhiteAgent      │
└────┬────────────────┘
     │
     ├─ [Data Loading] ──────────┐
     │                            │
     │  ┌──────────────────┐     │
     │  │ LLMDataLoader    │     │
     │  └────┬─────────────┘     │
     │       │                   │
     │       ├─ Find files       │
     │       ├─ Try pandas       │
     │       ├─ → Gemini (if needed)
     │       └─ Return DataFrame  │
     │                            │
     ├────────────────────────────┘
     │
     ├─ [Analysis Planning] ──────┐
     │                             │
     │  ┌──────────────────┐      │
     │  │  LLMAnalyzer     │      │
     │  └────┬─────────────┘      │
     │       │                    │
     │       ├─ → Gemini (plan)   │
     │       ├─ Parse JSON        │
     │       └─ Return plan       │
     │                             │
     ├─────────────────────────────┘
     │
     ├─ [Statistical Analysis] ────┐
     │                              │
     │  ┌──────────────────┐       │
     │  │  LLMAnalyzer     │       │
     │  └────┬─────────────┘       │
     │       │                     │
     │       ├─ Execute tests      │
     │       ├─ Calculate stats    │
     │       ├─ → Gemini (interpret)
     │       └─ Return results     │
     │                              │
     ├──────────────────────────────┘
     │
     ├─ [Report Generation] ───────┐
     │                              │
     │  ┌──────────────────┐       │
     │  │ ReportGenerator  │       │
     │  └────┬─────────────┘       │
     │       │                     │
     │       ├─ → Gemini (report)  │
     │       └─ Save markdown      │
     │                              │
     ├──────────────────────────────┘
     │
     └─ [Save Outputs]
         ├─ Code generation
         ├─ Metadata
         └─ Return results
```

## LLM Interaction Points

### 1. Data Loading (Optional)
- **When:** Standard loading fails
- **Input:** File sample (first 20 lines)
- **Output:** Loading instructions (delimiter, encoding, etc.)
- **Model:** gemini-1.5-flash (fast & cheap)
- **Cost:** ~$0.001

### 2. Analysis Planning (Required)
- **When:** Every analysis
- **Input:** Context + data sample (100 rows) + metadata
- **Output:** JSON analysis plan
- **Model:** gemini-1.5-pro (best quality)
- **Cost:** ~$0.02

### 3. Result Interpretation (Required)
- **When:** After statistical analysis
- **Input:** Context + plan + results
- **Output:** Natural language interpretation
- **Model:** gemini-1.5-pro
- **Cost:** ~$0.01

### 4. Report Generation (Required)
- **When:** Final step
- **Input:** Context + full results
- **Output:** Comprehensive markdown report
- **Model:** gemini-1.5-pro
- **Cost:** ~$0.03

**Total per analysis:** ~$0.06

## Error Handling & Fallbacks

### Multi-Level Fallback System

```
┌─────────────────────────────────────────────────────┐
│ Level 1: Data Loading                              │
│   Standard pandas → LLM guidance → Error            │
├─────────────────────────────────────────────────────┤
│ Level 2: Variable Identification                    │
│   LLM analysis plan → Heuristic fallback            │
├─────────────────────────────────────────────────────┤
│ Level 3: Statistical Analysis                       │
│   LLM-planned analysis → Traditional analyzer       │
├─────────────────────────────────────────────────────┤
│ Level 4: Report Generation                          │
│   LLM report → Template report                      │
├─────────────────────────────────────────────────────┤
│ Level 5: Mode Selection                             │
│   LLM mode → Traditional mode (no API key)          │
└─────────────────────────────────────────────────────┘
```

### Error Flow Example

```
User tries to load unusual CSV
    │
    ├─ Standard pandas.read_csv() → FAILS
    │
    ├─ Try different delimiters → FAILS
    │
    ├─ Ask LLM for guidance → SUCCESS
    │      └─ LLM: "Use ';' delimiter, skip 2 rows"
    │
    └─ Retry with LLM guidance → SUCCESS
```

## File Organization

```
src/white_agent/
├── __init__.py                 # Package exports
├── agent.py                    # Traditional WhiteAgent
├── analyzer.py                 # Traditional RCTAnalyzer
├── data_loader.py              # Traditional DataLoader
├── report_generator.py         # Enhanced ReportGenerator
├── utils.py                    # Shared utilities
│
├── llm_agent.py               # LLM-powered agent (NEW)
├── llm_analyzer.py            # LLM-powered analyzer (NEW)
├── llm_data_loader.py         # LLM-powered loader (NEW)
└── unified_agent.py           # Mode selection wrapper (NEW)
```

## Configuration Options

### Model Selection
```python
LLMWhiteAgent(
    analyzer_model="gemini-1.5-pro",    # Quality > Speed
    loader_model="gemini-1.5-flash",     # Speed > Quality
    report_model="gemini-1.5-pro"        # Quality > Speed
)
```

### Mode Forcing
```python
UnifiedWhiteAgent(
    force_mode="llm"          # Force LLM mode
    force_mode="traditional"  # Force traditional mode
    force_mode=None           # Auto-detect (default)
)
```

### Data Sampling
```python
analyzer.analyze_experiment(
    data=df,
    context=context,
    data_sample_size=100  # Rows sent to LLM (default)
)
```

## Performance Characteristics

### Latency Breakdown (LLM Mode)

```
Total: 10-30 seconds
├─ Data Loading: 1-3s
│  ├─ File I/O: 0.5s
│  └─ LLM call (if needed): 2s
│
├─ Analysis Planning: 3-5s
│  ├─ Data preparation: 0.5s
│  └─ LLM call: 3s
│
├─ Statistical Analysis: 1-2s
│  └─ Computation: 1-2s
│
├─ Result Interpretation: 2-3s
│  └─ LLM call: 2-3s
│
└─ Report Generation: 3-5s
   └─ LLM call: 3-5s
```

### Traditional Mode (Comparison)
```
Total: 2-5 seconds
├─ Data Loading: 0.5s
├─ Variable ID (heuristic): 0.1s
├─ Statistical Analysis: 1-2s
└─ Report Generation: 1-2s (template or LLM)
```

## Scalability Considerations

### Single Analysis
- Works well for individual tests
- Reasonable latency (~15s with LLM)
- Cost-effective (~$0.06)

### Batch Processing (100+ tests)
- Consider parallel processing
- May want to batch LLM calls
- Monitor API rate limits
- Consider caching analysis plans

### Future Optimizations
- Cache variable identification patterns
- Batch LLM requests
- Use cheaper models for simple decisions
- Implement result caching

## Security & Privacy

### Data Handling
- Data samples sent to Gemini API
- Only 100 rows sent for analysis planning
- Consider data sensitivity

### API Key Management
- Store in environment variables
- Never commit to version control
- Rotate keys periodically

### Best Practices
- Review LLM outputs
- Validate variable identification
- Check analysis plans
- Monitor for unexpected behavior
