import uuid
import os
import requests
from datetime import datetime, timezone



# ── Main function ─────────────────────────────────────────────────────────────

def geocode_address(address: str) -> dict:
    google_key = os.getenv("GOOGLE_GEO_KEY")
    opencage_key = os.getenv("OPENCAGE_KEY")

    lat, lon, display_address = None, None, None

    # Try Google Geocoding API first
    if google_key:
        lat, lon, display_address = _google_geocode(address, google_key)

    # Fall back to OpenCage if Google failed or no key provided
    if lat is None and opencage_key:
        print("  [INFO] Falling back to OpenCage geocoder...")
        lat, lon, display_address = _opencage_geocode(address, opencage_key)

    if lat is None or lon is None:
        raise ValueError(
            f"Could not geocode address: '{address}'. "
            "Check your API keys or try a more specific address."
        )

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    location_point = {
        "signal_id":           str(uuid.uuid4()),
        "latitude":            round(lat, 6),
        "longitude":           round(lon, 6),
        "altitude_m":          None,          # Geocoding APIs don't give altitude
        "timestamp_utc":       timestamp_utc,
        "source":              "ADDRESS",
        "raw_input":           address.strip(),
        "accuracy_radius_m":   100.0,         # ADDRESS default from schema
        "raw_confidence":      0.7,           # ADDRESS default from schema
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


# ── Provider functions ────────────────────────────────────────────────────────

def _google_geocode(address: str, api_key: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("status") == "OK":
            result   = data["results"][0]
            location = result["geometry"]["location"]
            formatted = result.get("formatted_address", address)
            print(f"  [Google] Geocoded: {formatted}")
            return location["lat"], location["lng"], formatted

        else:
            print(f"  [Google] API error: {data.get('status')} — {data.get('error_message', '')}")
            return None, None, None

    except requests.RequestException as e:
        print(f"  [Google] Request failed: {e}")
        return None, None, None


def _opencage_geocode(address: str, api_key: str):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {"q": address, "key": api_key, "limit": 1, "no_annotations": 1}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("results"):
            result    = data["results"][0]
            geometry  = result["geometry"]
            formatted = result.get("formatted", address)
            print(f"  [OpenCage] Geocoded: {formatted}")
            return geometry["lat"], geometry["lng"], formatted

        else:
            print(f"  [OpenCage] No results found for: '{address}'")
            return None, None, None

    except requests.RequestException as e:
        print(f"  [OpenCage] Request failed: {e}")
        return None, None, None


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with the demo address from the project spec
    test_address = "Anna Salai, Chennai"

    print("Input address:")
    print(f"  {test_address}\n")

    try:
        result = geocode_address(test_address)

        print("\nParsed LocationPoint:")
        for key, value in result.items():
            print(f"  {key:<22} : {value}")

    except ValueError as e:
        print(f"\n[ERROR] {e}")
        print("\nMake sure you have set GOOGLE_GEO_KEY or OPENCAGE_KEY as environment variables.")
        print("  export GOOGLE_GEO_KEY=your_key_here")
        print("  export OPENCAGE_KEY=your_key_here   ← free, no credit card needed")
