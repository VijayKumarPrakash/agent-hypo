# Quick Start - A2A Service

Get the White Agent A2A service running in 5 minutes.

## Prerequisites

- Python 3.11+
- S3-compatible storage account (AWS S3, Cloudflare R2, or MinIO)
- (Optional) Gemini API key for LLM mode

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

Copy the example environment file and edit it:

```bash
cp .env.a2a.example .env
```

Edit `.env` and add your credentials:

```bash
# Minimum required configuration
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY_ID=your-key
S3_SECRET_ACCESS_KEY=your-secret

# Optional: For LLM mode
GEMINI_API_KEY=your-gemini-key
```

## Step 3: Run the Server

```bash
uvicorn app.server:app --reload
```

Server will start at `http://localhost:8000`

## Step 4: Test It

**Option 1: Interactive API Docs**

Open in browser: `http://localhost:8000/docs`

**Option 2: Test Script**

```bash
python test_a2a_service.py
```

**Option 3: cURL**

```bash
# Health check
curl http://localhost:8000/health

# Run analysis (replace with your URLs)
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "context_url": "https://example.com/context.txt",
    "data_url": "https://example.com/data.csv",
    "mode": "auto"
  }'
```

## Step 5: Deploy (Optional)

### Docker

```bash
# Build
docker build -t white-agent .

# Run
docker run -p 8000:8000 --env-file .env white-agent
```

### Cloud Platforms

See [README_A2A.md](README_A2A.md) for detailed deployment instructions for:
- AWS ECS/Fargate
- Google Cloud Run
- Render, Railway, Fly.io

## Troubleshooting

**Server won't start:**
- Check Python version: `python --version` (need 3.11+)
- Check dependencies: `pip list | grep fastapi`

**Storage errors:**
- Verify credentials in `.env`
- Test S3 access with AWS CLI: `aws s3 ls s3://your-bucket`

**LLM mode not working:**
- Set `GEMINI_API_KEY` in `.env`
- Or use `"mode": "traditional"` in requests

## Next Steps

- Read full documentation: [README_A2A.md](README_A2A.md)
- Use legacy CLI: `python legacy_main.py --help`
- Check original features: [README.md](README.md)

## Example Request/Response

**Request:**
```json
{
  "context_url": "https://example.com/context.txt",
  "data_url": "https://example.com/data.csv",
  "mode": "auto"
}
```

**Response:**
```json
{
  "status": "success",
  "run_id": "abc-123",
  "mode_used": "llm",
  "analysis_summary": {
    "sample_size": 1000,
    "treatment_effect": 0.1234,
    "p_value": 0.0023,
    "statistically_significant": true
  },
  "outputs": {
    "report_url": "https://bucket.s3.amazonaws.com/runs/abc-123/analysis_report.md",
    "results_url": "https://bucket.s3.amazonaws.com/runs/abc-123/results.json",
    "analysis_code_url": "https://bucket.s3.amazonaws.com/runs/abc-123/analysis.py",
    "data_copy_url": "https://bucket.s3.amazonaws.com/runs/abc-123/data/data.csv"
  }
}
```

Done! Your A2A service is ready to use.
