"""
test_person_c.py — Integration test for Person C's Risk Context + API Layer

Part 1: Direct unit tests (no server needed)
  - Calls detect_environment() and get_dispatch_status() / get_followup_question()
    with LocationPoint objects matching the 3 demo scenarios.

Part 2: HTTP integration tests (requires uvicorn running on :8000)
  - Sends the exact demo scenario JSON payloads to POST /locate
    and prints the full response.

Run:
    python test_person_c.py
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List

from models import LocationPoint, FusedLocation
from risk.environment import detect_environment
from risk.dispatch_status import get_dispatch_status, get_followup_question


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _sig(**overrides) -> LocationPoint:
    """Build a LocationPoint with sensible defaults, overridden by kwargs."""
    defaults = {
        "signal_id": str(uuid.uuid4()),
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": "GPS",
        "raw_input": "test",
        "accuracy_radius_m": 15.0,
        "raw_confidence": 0.9,
    }
    defaults.update(overrides)
    return LocationPoint(**defaults)


# ===================================================================
# PART 1 — Direct unit tests (no HTTP, no server)
# ===================================================================
print("=" * 65)
print("PART 1 — Unit tests (direct function calls)")
print("=" * 65)

passed = 0
total = 3


# -------------------------------------------------------------------
# Scenario 1 — GREEN  (GPS + W3W + ADDRESS agree, confidence ~0.88)
# -------------------------------------------------------------------
print("\n--- Scenario 1: GREEN (high confidence) ---")

signals_1: List[LocationPoint] = [
    _sig(
        source="GPS",
        latitude=13.0827,
        longitude=80.2707,
        hdop=1.1,
        satellite_count=7,
        is_indoor=False,
        raw_confidence=0.90,
        accuracy_radius_m=15.0,
        raw_input="$GPGGA,092311,1304.96,N,08016.24,E,1,07,1.1,14.5,M",
    ),
    _sig(
        source="W3W",
        latitude=13.0830,
        longitude=80.2712,
        raw_confidence=0.85,
        accuracy_radius_m=3.0,
        raw_input="///fills.snap.brave",
    ),
    _sig(
        source="ADDRESS",
        latitude=13.0835,
        longitude=80.2700,
        raw_confidence=0.70,
        accuracy_radius_m=100.0,
        raw_input="Anna Salai, Chennai",
    ),
]

env_1 = detect_environment(signals_1)
confidence_1 = 0.88  # simulated fused confidence from Person B
status_1 = get_dispatch_status(confidence_1, disaster_mode=False)
question_1 = get_followup_question(status_1, env_1, sources_ignored=["CELL"])

print(f"  Environment : {env_1}")
print(f"  Confidence  : {confidence_1}")
print(f"  Status      : {status_1}")
print(f"  Followup    : {question_1}")

s1_pass = status_1 == "GREEN" and question_1 is None
print(f"  Result      : {'✅ PASS' if s1_pass else '❌ FAIL'}")
if s1_pass:
    passed += 1


# -------------------------------------------------------------------
# Scenario 2 — YELLOW  (indoor GPS hdop=7.8, weak cell, confidence ~0.55)
# -------------------------------------------------------------------
print("\n--- Scenario 2: YELLOW (conflict / indoor) ---")

signals_2: List[LocationPoint] = [
    _sig(
        source="GPS",
        latitude=13.0827,
        longitude=80.2707,
        hdop=7.8,
        satellite_count=3,
        is_indoor=True,
        raw_confidence=0.30,
        accuracy_radius_m=150.0,
        raw_input="$GPGGA,092311,1304.96,N,08016.24,E,1,03,7.8,14.5,M",
    ),
    _sig(
        source="CELL",
        latitude=13.071,
        longitude=80.258,
        raw_confidence=0.55,
        accuracy_radius_m=500.0,
        signal_strength_dbm=-102,
        raw_input='{"tower_lat":13.071,"tower_lon":80.258,"signal_dbm":-102}',
    ),
]

env_2 = detect_environment(signals_2)
confidence_2 = 0.55
status_2 = get_dispatch_status(confidence_2, disaster_mode=False)
question_2 = get_followup_question(status_2, env_2, sources_ignored=["GPS"])

print(f"  Environment : {env_2}")
print(f"  Confidence  : {confidence_2}")
print(f"  Status      : {status_2}")
print(f"  Followup    : {question_2}")

s2_pass = status_2 == "YELLOW" and question_2 is not None
print(f"  Result      : {'✅ PASS' if s2_pass else '❌ FAIL'}")
if s2_pass:
    passed += 1


# -------------------------------------------------------------------
# Scenario 3 — RED  (disaster mode, single weak cell tower)
# -------------------------------------------------------------------
print("\n--- Scenario 3: RED (disaster / search zone) ---")

signals_3: List[LocationPoint] = [
    _sig(
        source="CELL",
        latitude=13.060,
        longitude=80.248,
        raw_confidence=0.55,
        accuracy_radius_m=500.0,
        signal_strength_dbm=-110,
        environment_mode="DISASTER",
        raw_input='{"tower_lat":13.060,"tower_lon":80.248,"signal_dbm":-110}',
    ),
]

env_3 = detect_environment(signals_3)
confidence_3 = 0.30
status_3 = get_dispatch_status(confidence_3, disaster_mode=True)
question_3 = get_followup_question(status_3, env_3, sources_ignored=[])

print(f"  Environment : {env_3}")
print(f"  Confidence  : {confidence_3}")
print(f"  Status      : {status_3}")
print(f"  Followup    : {question_3}")

s3_pass = status_3 == "RED" and question_3 is not None
print(f"  Result      : {'✅ PASS' if s3_pass else '❌ FAIL'}")
if s3_pass:
    passed += 1


# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
print("\n" + "=" * 65)
print(f"  ▸ {passed}/{total} scenarios passed")
print("=" * 65)


# ===================================================================
# PART 2 — HTTP integration tests (server must be running on :8000)
# ===================================================================
print("\n\n" + "=" * 65)
print("PART 2 — HTTP integration tests (POST /locate)")
print("=" * 65)

try:
    import requests
except ImportError:
    print("\n⚠️  'requests' library not installed. Run: pip install requests")
    print("   Skipping HTTP tests.\n")
    exit(0)

BASE_URL = "http://localhost:8000"

scenarios = [
    {
        "name": "Scenario 1 — GREEN",
        "payload": {
            "caller_text": "I'm near the big clock tower",
            "signals": [
                {"type": "GPS", "data": "$GPGGA,092311,1304.96,N,08016.24,E,1,07,1.1,14.5,M"},
                {"type": "W3W", "data": "///fills.snap.brave"},
                {"type": "ADDRESS", "data": "Anna Salai, Chennai"},
            ],
        },
    },
    {
        "name": "Scenario 2 — YELLOW",
        "payload": {
            "caller_text": "I'm inside a shopping mall, ground floor",
            "signals": [
                {"type": "GPS", "data": "$GPGGA,092311,1304.96,N,08016.24,E,1,03,7.8,14.5,M"},
                {"type": "CELL", "data": '{"tower_lat":13.071,"tower_lon":80.258,"signal_dbm":-102}'},
            ],
        },
    },
    {
        "name": "Scenario 3 — RED",
        "payload": {
            "caller_text": "There was an explosion, I can see a red building and a petrol station",
            "signals": [
                {"type": "CELL", "data": '{"tower_lat":13.060,"tower_lon":80.248,"signal_dbm":-110}'},
            ],
            "disaster_mode": True,
        },
    },
]

for sc in scenarios:
    print(f"\n--- {sc['name']} ---")
    try:
        resp = requests.post(f"{BASE_URL}/locate", json=sc["payload"], timeout=5)
        resp.raise_for_status()
        data = resp.json()
        print(f"  HTTP {resp.status_code}")
        print(f"  dispatch_status   : {data['dispatch_status']}")
        print(f"  confidence_score  : {data['confidence_score']}")
        print(f"  fused_lat/lon     : {data['fused_lat']}, {data['fused_lon']}")
        print(f"  uncertainty_radius: {data['uncertainty_radius_m']} m")
        print(f"  sources_used      : {data['sources_used']}")
        print(f"  sources_ignored   : {data['sources_ignored']}")
        print(f"  explanation       : {data['explanation']}")
        print(f"  followup_question : {data['followup_question']}")
    except requests.ConnectionError:
        print("  ⚠️  Connection refused — is the server running?")
        print("     Start it with: uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 65)
print("Done.")
print("=" * 65)
