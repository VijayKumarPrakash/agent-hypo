# LLM Models Used

## Default Configuration

The LLM-powered White Agent uses **Google Gemini** models with an optimized configuration:

### Model Selection by Component

| Component | Default Model | Purpose | Reason |
|-----------|--------------|---------|--------|
| **Data Loader** | `gemini-1.5-flash` | Load & parse data files | Fast, cheap, good enough for format detection |
| **Analyzer** | `gemini-1.5-pro` | Analysis planning & interpretation | Best quality for critical analysis decisions |
| **Report Generator** | `gemini-1.5-pro` | Generate comprehensive reports | Best quality for detailed, professional reports |

### Cost Breakdown

**Per Analysis (with default config):**

- Data loading (`flash`): ~$0.001
- Analysis planning (`pro`): ~$0.02
- Result interpretation (`pro`): ~$0.01
- Report generation (`pro`): ~$0.03

**Total: ~$0.06 per test**

## Model Details

### Gemini 1.5 Flash

**Used for:** Data loading

**Characteristics:**
- **Speed:** Very fast (~1-2 seconds per call)
- **Cost:** Low (~$0.001 per call)
- **Quality:** Good enough for format detection and data validation
- **Context window:** 1 million tokens

**Why we use it here:**
- Data loading doesn't require the highest intelligence
- Speed matters for user experience
- Significantly cheaper than Pro
- Sufficient for determining delimiters, encodings, and data structure

### Gemini 1.5 Pro

**Used for:** Analysis planning, interpretation, and report generation

**Characteristics:**
- **Speed:** Moderate (~3-5 seconds per call)
- **Cost:** Higher (~$0.01-0.03 per call)
- **Quality:** Best available for reasoning and analysis
- **Context window:** 2 million tokens

**Why we use it here:**
- Analysis planning requires sophisticated reasoning
- Statistical interpretation needs accuracy
- Report quality directly impacts user trust
- Worth the extra cost for critical components

## Customizing Models

You can customize which models to use when initializing the agent:

### Option 1: Using LLMWhiteAgent Directly

```python
from white_agent import LLMWhiteAgent

agent = LLMWhiteAgent(
    gemini_api_key="your-key",
    analyzer_model="gemini-1.5-pro",      # Best quality (default)
    loader_model="gemini-1.5-flash",       # Fast & cheap (default)
    report_model="gemini-1.5-pro"          # Best quality (default)
)
```

### Option 2: Cost-Optimized (Use Flash for Everything)

```python
from white_agent import LLMWhiteAgent

# Use flash for everything to minimize cost
agent = LLMWhiteAgent(
    gemini_api_key="your-key",
    analyzer_model="gemini-1.5-flash",     # Cheaper
    loader_model="gemini-1.5-flash",       # Cheaper
    report_model="gemini-1.5-flash"        # Cheaper
)
```

**Cost: ~$0.003 per analysis** (20x cheaper!)

**Trade-off:** Lower quality analysis and reports

### Option 3: Quality-Optimized (Use Pro for Everything)

```python
from white_agent import LLMWhiteAgent

# Use pro for everything for maximum quality
agent = LLMWhiteAgent(
    gemini_api_key="your-key",
    analyzer_model="gemini-1.5-pro",       # Best
    loader_model="gemini-1.5-pro",         # Best
    report_model="gemini-1.5-pro"          # Best
)
```

**Cost: ~$0.07 per analysis**

**Trade-off:** Slightly more expensive, slower data loading

### Option 4: Balanced (Recommended Default)

```python
from white_agent import LLMWhiteAgent

# Default configuration (already optimized)
agent = LLMWhiteAgent(
    gemini_api_key="your-key"
    # Uses: flash for loading, pro for analysis & reports
)
```

**Cost: ~$0.06 per analysis**

**Trade-off:** Best balance of cost, speed, and quality

## Model Comparison

### Performance Comparison

| Metric | Flash | Pro |
|--------|-------|-----|
| **Speed** | ~2s per call | ~4s per call |
| **Cost per 1K tokens** | $0.000075 (input) | $0.00125 (input) |
| **Quality** | Good | Excellent |
| **Reasoning** | Moderate | Strong |
| **Context window** | 1M tokens | 2M tokens |

### When to Use Which

**Use Flash for:**
- ✅ Data format detection
- ✅ Simple validation tasks
- ✅ High-volume processing
- ✅ Non-critical decisions
- ✅ Cost-sensitive scenarios

**Use Pro for:**
- ✅ Statistical analysis planning
- ✅ Complex reasoning tasks
- ✅ Report generation
- ✅ Critical interpretations
- ✅ Quality-sensitive scenarios

## Via Command Line

You cannot directly specify models via `main.py` or `launcher.py` (they use defaults), but you can:

### Option 1: Set in Code

Create a custom script:

```python
# custom_analysis.py
from white_agent import LLMWhiteAgent

agent = LLMWhiteAgent(
    analyzer_model="gemini-1.5-flash",  # Your choice
    loader_model="gemini-1.5-flash",
    report_model="gemini-1.5-flash"
)

results = agent.process_test(test_index=1)
print(f"Results: {results['output_dir']}")
```

Run it:
```bash
export GEMINI_API_KEY="your-key"
python custom_analysis.py
```

### Option 2: Environment Variables (Future Enhancement)

*Not currently implemented, but could be added:*

```bash
export GEMINI_ANALYZER_MODEL="gemini-1.5-flash"
export GEMINI_LOADER_MODEL="gemini-1.5-flash"
export GEMINI_REPORT_MODEL="gemini-1.5-flash"
python main.py
```

## Cost Estimates

### Single Analysis

| Configuration | Cost per Analysis |
|--------------|-------------------|
| **All Flash** | ~$0.003 |
| **Default (Flash + Pro)** | ~$0.06 |
| **All Pro** | ~$0.07 |

### Batch Processing

| Number of Tests | Default Config | All Flash | All Pro |
|----------------|----------------|-----------|---------|
| 10 | $0.60 | $0.03 | $0.70 |
| 100 | $6.00 | $0.30 | $7.00 |
| 1,000 | $60.00 | $3.00 | $70.00 |

## Speed Comparison

### Total Analysis Time

| Configuration | Typical Time |
|--------------|--------------|
| **Traditional mode** | 2-5 seconds |
| **LLM: All Flash** | 8-15 seconds |
| **LLM: Default (Flash + Pro)** | 10-30 seconds |
| **LLM: All Pro** | 15-40 seconds |

### Breakdown (Default Config)

```
Total: ~15-25 seconds
├─ Data loading (flash): 1-2s
├─ Analysis planning (pro): 3-5s
├─ Statistical computation: 1-2s
├─ Result interpretation (pro): 2-4s
└─ Report generation (pro): 4-8s
```

## Recommendations

### For Development/Testing
```python
# Use all flash for speed
agent = LLMWhiteAgent(
    analyzer_model="gemini-1.5-flash",
    loader_model="gemini-1.5-flash",
    report_model="gemini-1.5-flash"
)
```

### For Production (Default)
```python
# Use balanced config (default)
agent = LLMWhiteAgent()
```

### For High-Stakes Analysis
```python
# Use all pro for maximum quality
agent = LLMWhiteAgent(
    analyzer_model="gemini-1.5-pro",
    loader_model="gemini-1.5-pro",
    report_model="gemini-1.5-pro"
)
```

### For High-Volume Processing
```python
# Use all flash for cost efficiency
agent = LLMWhiteAgent(
    analyzer_model="gemini-1.5-flash",
    loader_model="gemini-1.5-flash",
    report_model="gemini-1.5-flash"
)
```

## Future Model Support

**Planned enhancements:**

1. **Anthropic Claude Support**
   - Claude 3.5 Sonnet
   - Claude 3 Opus
   - Claude 3 Haiku

2. **OpenAI GPT Support**
   - GPT-4 Turbo
   - GPT-4
   - GPT-3.5 Turbo

3. **Model Configuration via Environment Variables**
   ```bash
   export LLM_PROVIDER="anthropic"
   export LLM_ANALYZER_MODEL="claude-3-5-sonnet-20241022"
   ```

4. **Model Fallbacks**
   - Try Pro, fall back to Flash if rate limited
   - Try Gemini, fall back to Claude if unavailable

## Monitoring Model Usage

Check which models were used in the analysis:

```python
results = agent.process_test(test_index=1)

# View model information
models_used = results.get('llm_models_used', {})
print(f"Data loader: {models_used.get('data_loader')}")
print(f"Analyzer: {models_used.get('analyzer')}")
print(f"Report generator: {models_used.get('report_generator')}")
```

Example output:
```json
{
  "data_loader": "gemini-1.5-flash",
  "analyzer": "gemini-1.5-pro",
  "report_generator": "gemini-1.5-pro"
}
```

## API Key Setup

Get your Gemini API key:

1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Set it in your environment:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or in a `.env` file:
```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

## Rate Limits & Quotas

**Gemini API limits (as of 2024):**

| Model | Free Tier | Paid Tier |
|-------|-----------|-----------|
| **Flash** | 15 RPM, 1M TPM | 1000 RPM, 4M TPM |
| **Pro** | 2 RPM, 32K TPM | 360 RPM, 4M TPM |

**For high-volume processing:**
- Use paid tier
- Implement retry logic
- Add delays between requests
- Consider batching

## Summary

**Default Configuration:**
- **Data Loading:** `gemini-1.5-flash` (fast & cheap)
- **Analysis:** `gemini-1.5-pro` (best quality)
- **Reports:** `gemini-1.5-pro` (best quality)

**Cost:** ~$0.06 per analysis

**Customizable:** Yes, via `LLMWhiteAgent` initialization

**Recommendation:** Stick with defaults unless you have specific cost or quality requirements.
