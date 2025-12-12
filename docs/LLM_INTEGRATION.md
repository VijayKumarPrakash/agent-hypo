# LLM Integration Guide

## Overview

The White Agent uses LLM (Large Language Model) integration to generate comprehensive, nuanced analysis reports. This document explains how the LLM integration works, which LLM is used, and how to configure it.

## Which LLM Does White Agent Use?

The White Agent uses **Google's Gemini API** (specifically `gemini-1.5-pro`) for generating analysis reports.

### Why Gemini?

1. **Cost-effective**: Free tier available with generous limits
2. **Long context window**: Can handle large experimental contexts
3. **High-quality output**: Excellent at analyzing statistical data
4. **Easy integration**: Simple Python SDK

## How LLM Integration Works

### Dual-Mode Operation

The White Agent operates in **two modes**:

#### 1. LLM-Powered Mode (with Gemini API key)

When a Gemini API key is provided:
- Uses `gemini-1.5-pro` to analyze results
- Generates comprehensive, contextual reports
- Provides nuanced interpretations
- Suggests specific, tailored recommendations

**Location**: [src/white_agent/report_generator.py:78-95](../src/white_agent/report_generator.py)

```python
def _generate_llm_report(self, context: str, results: Dict[str, Any]) -> str:
    """Generate report using Gemini LLM."""
    prompt = self._build_report_prompt(context, results)
    response = self.model.generate_content(prompt)
    return response.text
```

#### 2. Template-Based Mode (no API key)

When no API key is provided:
- Falls back to template-based report generation
- Uses predefined report structure
- Fills in statistical results programmatically
- Still provides comprehensive analysis

**Location**: [src/white_agent/report_generator.py:132-303](../src/white_agent/report_generator.py)

```python
def _generate_template_report(self, context: str, results: Dict[str, Any]) -> str:
    """Generate a template-based report when LLM is not available."""
    # Constructs report using Python string formatting
    # Includes all statistical findings
    # Provides standard interpretations and recommendations
```

### Fallback Mechanism

The agent automatically falls back to template mode if:
1. No API key is provided
2. `google-generativeai` package is not installed
3. API call fails (network error, rate limit, etc.)

**Location**: [src/white_agent/report_generator.py:78-95](../src/white_agent/report_generator.py)

```python
try:
    response = self.model.generate_content(prompt)
    return response.text
except Exception as e:
    logger.error(f"LLM report generation failed: {e}")
    logger.info("Falling back to template report")
    return self._generate_template_report(context, results)
```

## Setting Up Gemini API

### Step 1: Get API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### Step 2: Configure Environment Variable

**Option A: Using .env file (recommended)**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your key:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```

**Option B: Shell environment variable**

```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

**Option C: Pass directly to agent**

```python
from white_agent import WhiteAgent

agent = WhiteAgent(gemini_api_key="your_actual_api_key_here")
```

### Step 3: Verify Setup

Run the test script:

```bash
python test_agent.py
```

You should see:
```
Gemini API key found - will use LLM for report generation
```

## What Gets Sent to the LLM?

The LLM receives:

1. **Experiment Context** (from `context.txt`):
   - Research question
   - Study design
   - Treatment details
   - Hypothesis

2. **Statistical Results** (from analysis):
   - Sample sizes
   - Treatment effects
   - p-values
   - Confidence intervals
   - Effect sizes
   - Regression coefficients
   - Balance checks

**Full Prompt Template**: [src/white_agent/report_generator.py:97-130](../src/white_agent/report_generator.py)

### Privacy Considerations

⚠️ **Important**: The experiment context and statistical results are sent to Google's servers when using Gemini API.

If you're working with sensitive data:
- Use template-based mode (don't set API key)
- Or redact sensitive information from context files
- Or set `DISABLE_LLM=true` in `.env`

## LLM Prompt Structure

The prompt instructs Gemini to generate a report with:

1. **Executive Summary**: Key findings (2-3 sentences)
2. **Experiment Overview**: Research question, design, sample
3. **Data Quality Assessment**: Sample size, balance, issues
4. **Statistical Findings**: All test results with interpretations
5. **Interpretation**: Practical meaning of results
6. **Threats to Validity**: Confounders, bias, assumptions
7. **Recommendations**: Actions, improvements, future studies
8. **Technical Details**: Methods, assumptions, sensitivity

**View full prompt**: [src/white_agent/report_generator.py:97-130](../src/white_agent/report_generator.py)

## Example: LLM vs Template Reports

### LLM-Generated Report (with Gemini)

```markdown
## Executive Summary

The online tutoring intervention demonstrated a statistically significant
positive effect on student test scores (ATE = 8.92, p < 0.001). Students
with access to the tutoring platform scored approximately 9 points higher
on average than control students, representing a meaningful improvement
in academic performance. Given the strong effect size (Cohen's d = 1.24)
and high statistical confidence, this intervention shows promise for
broader implementation.

## Experiment Overview

This randomized controlled trial examined whether providing high school
students with access to an adaptive online tutoring platform would improve
their standardized test scores compared to students receiving standard
instruction alone...

[Continues with detailed, contextual analysis]
```

### Template-Generated Report (without API key)

```markdown
## Executive Summary

This analysis examines the treatment effect in a randomized controlled
experiment. The average treatment effect (ATE) is 8.92 with a p-value
of 0.0001. The results are statistically significant at the α=0.05 level.

## Experiment Overview

### Context
[Full context from context.txt inserted here]

### Study Design
- Total Sample Size: 200
- Treatment Variable: treatment
- Outcome Variable: test_score
- Design Type: Randomized Controlled Trial

[Continues with structured analysis]
```

## Cost Considerations

### Gemini API Pricing (as of 2024)

**Free Tier**:
- 60 requests per minute
- 1,500 requests per day
- Sufficient for most research use cases

**Paid Tier** (if needed):
- Input: $0.00025 per 1K characters
- Output: $0.0005 per 1K characters
- Typical report costs: $0.01-0.02 per analysis

**Note**: Pricing may change. Check [Google AI Pricing](https://ai.google.dev/pricing)

### Template Mode (Free)

No costs - uses local string formatting only.

## Customizing LLM Behavior

### Change Model

Edit [src/white_agent/report_generator.py:25](../src/white_agent/report_generator.py):

```python
def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
    # Use gemini-1.5-flash for faster, cheaper responses
    # Use gemini-1.5-pro for more detailed analysis (default)
```

### Modify Prompt

Edit the prompt in `_build_report_prompt()` to change:
- Report structure
- Level of detail
- Tone and style
- Specific analyses to emphasize

**Location**: [src/white_agent/report_generator.py:97-130](../src/white_agent/report_generator.py)

### Temperature and Parameters

Add generation configuration:

```python
response = self.model.generate_content(
    prompt,
    generation_config={
        'temperature': 0.7,  # Lower = more focused, Higher = more creative
        'top_p': 0.95,
        'max_output_tokens': 4096,
    }
)
```

## Switching to Other LLMs

### Using OpenAI Instead

1. Install OpenAI SDK:
   ```bash
   pip install openai
   ```

2. Modify `report_generator.py`:
   ```python
   import openai

   def _generate_llm_report(self, context, results):
       response = openai.ChatCompletion.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": "You are an expert statistician..."},
               {"role": "user", "content": self._build_report_prompt(context, results)}
           ]
       )
       return response.choices[0].message.content
   ```

3. Set `OPENAI_API_KEY` in `.env`

### Using Claude (Anthropic)

1. Install Anthropic SDK:
   ```bash
   pip install anthropic
   ```

2. Modify to use Claude API (similar pattern)

### Using Local LLM (Ollama)

1. Install Ollama
2. Use Ollama Python client
3. No API key needed - fully local

## Debugging LLM Integration

### Check if LLM is being used

Look for log messages:

```
INFO - Gemini API key found - will use LLM for report generation
```

or

```
WARNING - No Gemini API key found - will use template-based reports
```

### Enable verbose logging

```bash
python main.py --verbose
```

### Test LLM directly

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content("Test: Write a summary of RCT analysis")
print(response.text)
```

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'google.generativeai'`

**Solution**:
```bash
pip install google-generativeai
```

**Issue**: `API key not valid`

**Solution**:
- Check your API key is correct
- Verify it's properly set in `.env` or environment
- Get a new key from Google AI Studio

**Issue**: `Rate limit exceeded`

**Solution**:
- Wait a minute and retry
- Reduce analysis frequency
- Upgrade to paid tier if needed

## Summary

| Feature | LLM Mode | Template Mode |
|---------|----------|---------------|
| **Requires API Key** | ✓ Yes | ✗ No |
| **Cost** | Free tier or $0.01-0.02/report | Free |
| **Quality** | Contextual, nuanced | Structured, comprehensive |
| **Privacy** | Sends to Google | Fully local |
| **Reliability** | Network dependent | Always works |
| **Customization** | Prompt engineering | Code modification |

**Recommendation**:
- Use LLM mode for exploratory analysis and stakeholder reports
- Use template mode for automated pipelines and sensitive data
- The agent seamlessly handles both modes with automatic fallback

## Further Reading

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google AI Studio](https://makersuite.google.com/)
- [Report Generator Source Code](../src/white_agent/report_generator.py)
- [Example Reports](../results/) (after running analysis)
