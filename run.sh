#!/bin/bash
# AgentBeats run script for White Agent
# This script is called by the AgentBeats controller to start the agent

# Use environment variables provided by AgentBeats controller
# $HOST and $AGENT_PORT are automatically set by the controller

# Activate virtual environment if it exists
if [ -d "white_agent_venv" ]; then
    source white_agent_venv/bin/activate
fi

# Start the agent server
python -m uvicorn app.server:app --host ${HOST:-0.0.0.0} --port ${AGENT_PORT:-8000}
