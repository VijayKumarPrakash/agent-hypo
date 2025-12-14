# White Agent - A2A Deployment Guide

This guide explains how to deploy and use the White Agent as an A2A-compliant HTTP service.

## Overview

The White Agent has been refactored from a file-based CLI tool into a production-ready HTTP service that:
- Accepts JSON requests with URLs to input files
- Processes RCT analysis in-memory (fully stateless)
- Uploads outputs to S3-compatible cloud storage
- Returns URLs to generated reports and analysis results
- Supports both LLM-powered and traditional analysis modes

## Architecture

```
app/
├── __init__.py          # Package initialization
├── models.py            # Pydantic request/response schemas
├── storage.py           # S3-compatible cloud storage utility
├── agent.py             # Core agent logic (pure function)
└── server.py            # FastAPI HTTP server

src/white_agent/         # Original agent implementation (preserved)
legacy_main.py           # Original CLI tool (for backward compatibility)
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file or export these variables:

```bash
# Required: S3-compatible storage configuration
export S3_BUCKET=your-bucket-name
export S3_ACCESS_KEY_ID=your-access-key
export S3_SECRET_ACCESS_KEY=your-secret-key

# Optional: For LLM-powered analysis
export GEMINI_API_KEY=your-gemini-api-key

# Optional: For custom S3 endpoints (Cloudflare R2, MinIO, etc.)
export S3_ENDPOINT_URL=https://your-endpoint.com
export S3_PUBLIC_URL_BASE=https://your-bucket.r2.cloudflarestorage.com

# Optional: Custom region (default: us-east-1)
export S3_REGION=us-east-1

# Optional: Custom port (default: 8000)
export PORT=8000
```

### 3. Run the Server Locally

```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

Or use the convenience script:

```bash
python -m app.server
```

The server will be available at `http://localhost:8000`

### 4. Test the API

**Check health:**
```bash
curl http://localhost:8000/health
```

**Run analysis:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "context_url": "https://example.com/experiment_context.txt",
    "data_url": "https://example.com/experiment_data.csv",
    "mode": "auto"
  }'
```

**View interactive API docs:**
Open `http://localhost:8000/docs` in your browser

## Cloud Storage Setup

### Option 1: AWS S3 (Recommended for AWS deployments)

1. Create an S3 bucket:
```bash
aws s3 mb s3://your-bucket-name
```

2. Configure bucket for public read access (optional):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

3. Set environment variables:
```bash
export S3_BUCKET=your-bucket-name
export S3_ACCESS_KEY_ID=your-aws-access-key
export S3_SECRET_ACCESS_KEY=your-aws-secret-key
export S3_REGION=us-east-1
```

### Option 2: Cloudflare R2 (Recommended for cost efficiency)

**Benefits:**
- More generous free tier (10GB storage, 1M operations/month)
- No egress fees
- S3-compatible API

**Setup:**
1. Create an R2 bucket in Cloudflare dashboard
2. Generate API tokens (Access Key ID and Secret)
3. Set environment variables:

```bash
export S3_BUCKET=your-bucket-name
export S3_ACCESS_KEY_ID=your-r2-access-key
export S3_SECRET_ACCESS_KEY=your-r2-secret-key
export S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
export S3_PUBLIC_URL_BASE=https://your-bucket.r2.dev
```

### Option 3: MinIO (Self-hosted)

Great for local testing or private clouds:

```bash
# Run MinIO locally
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"

# Configure
export S3_BUCKET=white-agent
export S3_ACCESS_KEY_ID=minioadmin
export S3_SECRET_ACCESS_KEY=minioadmin
export S3_ENDPOINT_URL=http://localhost:9000
export S3_PUBLIC_URL_BASE=http://localhost:9000/white-agent
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t white-agent:latest .
```

### Run Container Locally

```bash
docker run -p 8000:8000 \
  -e S3_BUCKET=your-bucket \
  -e S3_ACCESS_KEY_ID=your-key \
  -e S3_SECRET_ACCESS_KEY=your-secret \
  -e GEMINI_API_KEY=your-gemini-key \
  white-agent:latest
```

### Deploy to Cloud Platforms

#### AWS ECS/Fargate

```bash
# Push to ECR
aws ecr create-repository --repository-name white-agent
docker tag white-agent:latest <account-id>.dkr.ecr.<region>.amazonaws.com/white-agent:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/white-agent:latest

# Deploy via ECS (configure task definition with environment variables)
```

#### Google Cloud Run

```bash
# Push to Google Container Registry
docker tag white-agent:latest gcr.io/<project-id>/white-agent:latest
docker push gcr.io/<project-id>/white-agent:latest

# Deploy
gcloud run deploy white-agent \
  --image gcr.io/<project-id>/white-agent:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars S3_BUCKET=your-bucket,GEMINI_API_KEY=your-key
```

#### Render, Railway, Fly.io

These platforms support direct Dockerfile deployment. Simply:
1. Connect your Git repository
2. Configure environment variables in their dashboard
3. Deploy

## API Reference

### POST /run

Run RCT analysis on experimental data.

**Request:**
```json
{
  "context_url": "https://example.com/context.txt",
  "data_url": "https://example.com/data.csv",
  "mode": "auto"  // "auto", "llm", or "traditional"
}
```

**Response:**
```json
{
  "status": "success",
  "run_id": "abc-123-def-456",
  "analysis_type": "RCT",
  "experiment_type": "parallel",
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
    "data_copy_url": "https://bucket.s3.amazonaws.com/runs/abc-123/data/data.csv",
    "context_copy_url": "https://bucket.s3.amazonaws.com/runs/abc-123/context/context.txt"
  }
}
```

**Supported Data Formats:**
- CSV (`.csv`)
- JSON (`.json`)
- Parquet (`.parquet`)
- Excel (`.xlsx`, `.xls`)

**Analysis Modes:**
- `auto`: Uses LLM mode if `GEMINI_API_KEY` is set, otherwise traditional mode
- `llm`: Forces LLM-powered analysis (requires API key)
- `traditional`: Forces traditional statistical analysis (no LLM)

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_available": true,
  "storage_configured": true
}
```

## A2A Controller Integration

To register this agent with an A2A controller (like AgentBeats):

1. Deploy the service and get its public URL
2. Register the endpoint: `POST https://your-service.com/run`
3. Use the `/health` endpoint for availability checks

Example integration:
```python
import requests

# Register with controller
controller_url = "https://agentbeats.example.com/register"
agent_config = {
    "agent_name": "white-agent",
    "agent_type": "rct-analyzer",
    "endpoint": "https://your-white-agent.com/run",
    "health_check": "https://your-white-agent.com/health"
}
requests.post(controller_url, json=agent_config)
```

## Cost Estimation

### LLM Mode (with Gemini API)
- **Per analysis**: ~$0.06
- **Time**: 10-30 seconds
- Includes: intelligent data loading, variable identification, statistical analysis, report generation

### Traditional Mode (no LLM)
- **Cost**: Free (no API calls)
- **Time**: 2-5 seconds
- Best for: standardized, well-formatted data

### Storage Costs

**Cloudflare R2 (Free Tier):**
- 10GB storage
- 1M Class A operations/month
- 10M Class B operations/month
- No egress fees

**AWS S3 (Free Tier):**
- 5GB storage
- 20K GET requests
- 2K PUT requests
- Egress charges apply

Each analysis run produces ~50-200KB of outputs (reports, code, data copies).

## Monitoring and Logs

View logs:
```bash
# Docker
docker logs <container-id>

# Cloud platforms provide log viewers in their dashboards
```

Monitor with health checks:
```bash
# Add to your monitoring system
curl https://your-service.com/health
```

## Troubleshooting

### Issue: Storage not configured error

**Solution:** Ensure all required S3 environment variables are set:
```bash
S3_BUCKET
S3_ACCESS_KEY_ID
S3_SECRET_ACCESS_KEY
```

### Issue: LLM mode not working

**Solution:** Set `GEMINI_API_KEY` environment variable or use `"mode": "traditional"`

### Issue: File download fails

**Solution:** Ensure the URLs are publicly accessible and return the correct content type

### Issue: Permission denied on S3 upload

**Solution:** Verify your S3 credentials have `PutObject` permissions on the bucket

## Legacy CLI

The original file-based CLI is preserved as `legacy_main.py`:

```bash
python legacy_main.py --test-index 1
```

See the original README.md for CLI usage instructions.

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/ src/
```

Lint:
```bash
flake8 app/ src/
```

## Security Notes

- Never commit `.env` files or secrets to Git
- Use IAM roles/service accounts in production instead of access keys when possible
- Configure CORS appropriately in `app/server.py` for your use case
- Consider adding authentication/authorization for production deployments
- Keep dependencies updated: `pip install -U -r requirements.txt`

## Support

For issues or questions:
- Check logs for detailed error messages
- Verify environment variables are set correctly
- Test with `/health` endpoint first
- Review API docs at `/docs`

## License

See LICENSE file for details.
