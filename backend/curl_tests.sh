#!/bin/bash
# curl_tests.sh — Send all 3 demo scenarios to POST /locate
# Usage: ./curl_tests.sh  (server must be running on port 8000)

echo "=== SCENARIO 1: GREEN (high confidence) ==="
curl -s -X POST http://localhost:8000/locate \
  -H "Content-Type: application/json" \
  -d '{
    "caller_text": "I'\''m near the big clock tower",
    "signals": [
      { "type": "GPS",  "data": "$GPGGA,092311,1304.96,N,08016.24,E,1,07,1.1,14.5,M" },
      { "type": "W3W",  "data": "///fills.snap.brave" },
      { "type": "ADDRESS", "data": "Anna Salai, Chennai" }
    ]
  }' | python3 -m json.tool

echo ""
echo "=== SCENARIO 2: YELLOW (conflict / indoor GPS) ==="
curl -s -X POST http://localhost:8000/locate \
  -H "Content-Type: application/json" \
  -d '{
    "caller_text": "I'\''m inside a shopping mall, ground floor",
    "signals": [
      { "type": "GPS",  "data": "$GPGGA,092311,1304.96,N,08016.24,E,1,03,7.8,14.5,M" },
      { "type": "CELL", "data": "{ \"tower_lat\": 13.071, \"tower_lon\": 80.258, \"signal_dbm\": -102 }" }
    ]
  }' | python3 -m json.tool

echo ""
echo "=== SCENARIO 3: RED (disaster / search zone) ==="
curl -s -X POST http://localhost:8000/locate \
  -H "Content-Type: application/json" \
  -d '{
    "caller_text": "There was an explosion, I can see a red building and a petrol station",
    "signals": [
      { "type": "CELL", "data": "{ \"tower_lat\": 13.060, \"tower_lon\": 80.248, \"signal_dbm\": -110 }" }
    ],
    "disaster_mode": true
  }' | python3 -m json.tool

echo ""
echo "=== Done ==="
