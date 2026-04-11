import uuid
import os
import re
import requests
from datetime import datetime, timezone


# ── Main function ─────────────────────────────────────────────────────────────

def convert_w3w(w3w_address: str) -> dict:
    api_key = os.getenv("W3W_KEY")
    if not api_key:
        raise EnvironmentError(
            "W3W_KEY environment variable not set.\n"
            "Sign up free at https://developer.what3words.com and then run:\n"
            "  export W3W_KEY=your_key_here"
        )

    # Clean the input — strip leading slashes and whitespace
    cleaned = _clean_w3w(w3w_address)

    # Validate format before hitting the API
    if not _is_valid_w3w(cleaned):
        raise ValueError(
            f"Invalid What3Words format: '{w3w_address}'. "
            "Expected 3 words separated by dots, e.g. 'fills.snap.brave'"
        )

    lat, lon = _call_w3w_api(cleaned, api_key)

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    location_point = {
        "signal_id":           str(uuid.uuid4()),
        "latitude":            round(lat, 6),
        "longitude":           round(lon, 6),
        "altitude_m":          None,       # W3W doesn't provide altitude
        "timestamp_utc":       timestamp_utc,
        "source":              "W3W",
        "raw_input":           w3w_address.strip(),
        "accuracy_radius_m":   3.0,        # W3W squares are ~3m x 3m
        "raw_confidence":      0.85,       # W3W default from schema
        "hdop":                None,
        "satellite_count":     None,
        "signal_strength_dbm": None,
        "is_indoor":           None,
        "floor_estimate":      None,
        "environment_mode":    "NORMAL",
        "is_outlier":          False,
        "outlier_reason":      None,
    }

    return location_point


# ── API call ──────────────────────────────────────────────────────────────────

def _call_w3w_api(words: str, api_key: str):
    url = "https://api.what3words.com/v3/convert-to-coordinates"
    params = {
        "words":  words,
        "key":    api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        # W3W returns an error block if something went wrong
        if "error" in data:
            code    = data["error"].get("code", "UNKNOWN")
            message = data["error"].get("message", "Unknown error")
            raise ValueError(f"What3Words API error [{code}]: {message}")

        coordinates = data["coordinates"]
        lat = coordinates["lat"]
        lon = coordinates["lng"]

        print(f"  [W3W] Converted '///{words}' → lat: {lat}, lon: {lon}")
        return lat, lon

    except requests.RequestException as e:
        raise ConnectionError(f"W3W API request failed: {e}")


# ── Helper functions ──────────────────────────────────────────────────────────

def _clean_w3w(raw: str) -> str:
    return raw.strip().lstrip("/").lower()


def _is_valid_w3w(words: str) -> bool:
    pattern = r'^[a-z]+\.[a-z]+\.[a-z]+$'
    return bool(re.match(pattern, words))


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with the demo W3W address from the project spec (Scenario 1)
    test_inputs = [
        "///fills.snap.brave",    # Scenario 1 — GREEN
        "///index.home.raft",     # From API contract example
    ]

    for test in test_inputs:
        print(f"Input W3W address:")
        print(f"  {test}\n")

        try:
            result = convert_w3w(test)

            print("Parsed LocationPoint:")
            for key, value in result.items():
                print(f"  {key:<22} : {value}")

        except (ValueError, EnvironmentError, ConnectionError) as e:
            print(f"[ERROR] {e}")

        print("\n" + "-" * 50 + "\n")
