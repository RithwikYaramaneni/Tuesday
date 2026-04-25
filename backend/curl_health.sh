#!/bin/bash
# curl_health.sh — Quick health check for the FastAPI server
# Usage: ./curl_health.sh

RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)

if echo "$RESPONSE" | grep -q '"ok"'; then
  echo "✅ Server is up"
  echo "   $RESPONSE"
else
  echo "❌ Server is DOWN"
  echo "   Start it with: uvicorn main:app --reload --port 8000"
fi
