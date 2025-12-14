#!/bin/bash
# Keep-alive script for Render free tier
# Pings the health endpoint every 10 minutes to prevent cold starts

SERVICE_URL="${SERVICE_URL:-http://localhost:8000}"

echo "White Agent Keep-Alive Monitor"
echo "Pinging: $SERVICE_URL/health"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # Ping health endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" 2>&1)

    if [ "$RESPONSE" = "200" ]; then
        echo "[$TIMESTAMP] ✓ Service is alive (HTTP 200)"
    else
        echo "[$TIMESTAMP] ✗ Service not responding (HTTP $RESPONSE)"
    fi

    # Wait 10 minutes (600 seconds)
    sleep 600
done
