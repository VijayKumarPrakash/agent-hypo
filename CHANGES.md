# Recent Updates

## New Features

### 1. Main Entry Point Script ([main.py](main.py))

Added a simple, user-friendly entry point that:
- **Auto-detects latest test**: No need to specify test index
- **Lists available tests**: `python main.py --list`
- **Analyzes specific tests**: `python main.py --test-index 1`
- **Shows clear output**: Formatted summary of results
- **Loads .env automatically**: Seamless environment variable management

**Usage**:
```bash
# Analyze the latest test
python main.py

# Analyze a specific test
python main.py --test-index 1

# List all available tests
python main.py --list
```

### 2. Environment Variable Management

#### .env File Support
- **[.env.example](.env.example)**: Template with all available environment variables
- **[.env](.env)**: Your local configuration (git-ignored)
- **Auto-loading**: Both `main.py` and `launcher.py` load .env automatically

#### Configuration Options
- `GEMINI_API_KEY`: API key for LLM-powered reports
- `WHITE_AGENT_INPUTS_DIR`: Custom inputs directory
- `WHITE_AGENT_RESULTS_DIR`: Custom results directory
- `WHITE_AGENT_HOST`: Server host for A2A mode
- `WHITE_AGENT_PORT`: Server port for A2A mode
- `LOG_LEVEL`: Logging verbosity

**Setup**:
```bash
cp .env.example .env
# Edit .env and add your API key
```

### 3. Comprehensive LLM Documentation

Added [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) explaining:
- **Which LLM is used**: Gemini 1.5 Pro
- **How it works**: Dual-mode operation (LLM vs template)
- **Setup instructions**: Getting and configuring API key
- **Privacy considerations**: What gets sent to the API
- **Cost information**: Free tier limits and pricing
- **Customization**: How to modify prompts and switch LLMs
- **Debugging**: Common issues and solutions

### 4. Updated Dependencies

Added to [requirements.txt](requirements.txt):
- `python-dotenv>=1.0.0` - For .env file support

## How LLM Integration Works

### Without API Key (Default)
The agent uses **template-based report generation**:
- ✓ Fully local - no external API calls
- ✓ Always works - no network dependencies
- ✓ Free - no costs
- ✓ Comprehensive - includes all statistical findings
- Uses Python string formatting to create structured reports

### With Gemini API Key (Optional)
The agent uses **Gemini LLM** for enhanced reports:
- ✓ Contextual - understands your experiment
- ✓ Nuanced - provides deeper insights
- ✓ Tailored - specific recommendations
- ✓ Natural language - easier to read
- Requires: Google AI API key (free tier available)

### Automatic Fallback
If LLM generation fails (network error, rate limit, etc.), the agent automatically falls back to template-based reports. You always get a report.

## File Structure Changes

```
agent-hypo/
├── main.py                    # NEW: Simple entry point
├── .env.example               # NEW: Environment variable template
├── .env                       # NEW: Your local config (git-ignored)
├── docs/
│   └── LLM_INTEGRATION.md     # NEW: LLM documentation
├── requirements.txt           # UPDATED: Added python-dotenv
├── README.md                  # UPDATED: New quick start section
├── QUICKSTART.md              # UPDATED: Uses main.py
└── src/launcher.py            # UPDATED: Loads .env
```

## Migration Guide

### If You Were Using Environment Variables

**Before**:
```bash
export GEMINI_API_KEY="your-key"
python src/launcher.py --mode standalone
```

**Now** (recommended):
```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your-key
python main.py
```

**Still works**:
```bash
export GEMINI_API_KEY="your-key"
python main.py  # Will use shell environment variable
```

### If You Were Using launcher.py

**Before**:
```bash
python src/launcher.py --mode standalone
> analyze 1
```

**Now** (simpler):
```bash
python main.py --test-index 1
```

**launcher.py still works** for:
- Interactive mode
- Server mode (A2A protocol)
- Advanced configuration

## Breaking Changes

None! All existing functionality is preserved:
- `launcher.py` still works exactly as before
- Environment variables still work
- Programmatic API unchanged
- A2A protocol unchanged

## Quick Commands Reference

### Analysis
```bash
# Simplest - analyze latest test
python main.py

# Specific test
python main.py --test-index 1

# List tests
python main.py --list

# Verbose output
python main.py --verbose
```

### Configuration
```bash
# Setup environment
cp .env.example .env

# Check what will be analyzed
python main.py --list

# Use custom directories
python main.py --inputs-dir my_inputs --results-dir my_results
```

### Interactive Mode
```bash
python src/launcher.py --mode standalone
```

### Server Mode (A2A)
```bash
python src/launcher.py --mode server --agent-port 8001
```

## What Hasn't Changed

- Core analysis functionality: Still performs the same comprehensive statistical analysis
- Output format: Same directory structure and file formats
- A2A protocol: Same message format and endpoints
- AgentBeats compatibility: Fully compatible with platform
- Report quality: Template reports are just as comprehensive

## Learn More

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Full Documentation**: [README.md](README.md)
- **LLM Details**: [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md)
- **Project Overview**: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **A2A Example**: [examples/green_agent_integration.py](examples/green_agent_integration.py)

## Feedback

If you encounter any issues with the new features, please:
1. Check [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) for LLM-related questions
2. Run with `--verbose` flag for detailed logging
3. Fall back to previous method if needed (everything still works)

---

**Version**: 1.0.0
**Updated**: 2025-12-11
