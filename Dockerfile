# Multi-stage Dockerfile for White Agent A2A service
# Optimized for production deployment

# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (do this BEFORE copying files)
RUN useradd -m -u 1000 agent

# Copy Python packages from builder to the agent user's home
COPY --from=builder /root/.local /home/agent/.local

# Make sure scripts in .local are usable
ENV PATH=/home/agent/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY src/ ./src/

# Change ownership to agent user
RUN chown -R agent:agent /app /home/agent/.local

USER agent

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the FastAPI server
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
