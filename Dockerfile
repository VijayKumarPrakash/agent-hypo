# Multi-stage Dockerfile for White Agent with AgentBeats Controller
# Optimized for production deployment

# Build stage
FROM python:3.13-slim as builder

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
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies (including bash for run.sh)
RUN apt-get update && apt-get install -y \
    curl \
    bash \
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
COPY .well-known/ ./.well-known/
COPY white_agent_card.toml ./white_agent_card.toml
COPY run.sh ./run.sh

# Make run.sh executable
RUN chmod +x run.sh

# Change ownership to agent user
RUN chown -R agent:agent /app /home/agent/.local

# AgentBeats controller needs to read the white_agent_card.toml
# Make sure it's readable
RUN chmod 644 /app/white_agent_card.toml

USER agent

# Expose port (FastAPI server port)
EXPOSE 8000

# Health check (check controller status endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/status || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the AgentBeats controller which will proxy to the agent
CMD ["agentbeats", "run_ctrl"]
