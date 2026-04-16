import uuid
import re
from datetime import datetime, timezone

try:
    from openlocationcode import openlocationcode as olc
except ImportError:
    raise ImportError(
        "openlocationcode library not installed.\n"
        "Run: pip install openlocationcode"
    )


# -- Main function -------------------------------------------------------------

def convert_plus_code(plus_code: str) -> dict:

    cleaned = plus_code.strip()

    # Validate it looks like a Plus Code before decoding
    if not _is_valid_plus_code(cleaned):
        raise ValueError(
            f"Invalid Plus Code format: '{plus_code}'. "
            "Expected format like '7J4VQJJ3+MH' or 'VQJ3+MH Chennai'."
        )

    # Short codes need a reference location to decode
    # Extract just the code part if there's a city name attached
    code_part = cleaned.split()[0]

    try:
        decoded = olc.decode(code_part)
    except Exception as e:
        raise ValueError(f"Could not decode Plus Code '{code_part}': {e}")

    lat = decoded.latitudeCenter
    lon = decoded.longitudeCenter

    # Plus Code accuracy depends on code length
    accuracy_m = _estimate_accuracy(code_part)

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"  [Plus Code] Converted '{code_part}' -> lat: {round(lat,6)}, lon: {round(lon,6)}")

    location_point = {
        "signal_id":           str(uuid.uuid4()),
        "latitude":            round(lat, 6),
        "longitude":           round(lon, 6),
        "altitude_m":          None,
        "timestamp_utc":       timestamp_utc,
        "source":              "W3W",         # Keep source as W3W for schema compatibility
        "raw_input":           cleaned,
        "accuracy_radius_m":   accuracy_m,
        "raw_confidence":      0.85,          # Same confidence as W3W in original schema
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


# -- Helper functions ---------------------------------------------------------

def _is_valid_plus_code(code: str) -> bool:
    # Extract just the code part (before any space/city name)
    code_part = code.split()[0]
    # Must contain a + sign and only valid OLC characters
    pattern = r'^[23456789CFGHJMPQRVWX]{2,8}\+[23456789CFGHJMPQRVWX]{0,2}$'
    return bool(re.match(pattern, code_part, re.IGNORECASE))


def _estimate_accuracy(code: str) -> float:
    # Count chars before the + sign
    before_plus = code.split("+")[0]
    length = len(before_plus)

    if length >= 8:
        return 3.0    # Very precise -- same as W3W
    elif length >= 6:
        return 14.0   # Good precision
    else:
        return 100.0  # Approximate


# -- Quick test ---------------------------------------------------------------

if __name__ == "__main__":
    # Test with real Plus Codes around Chennai
    test_inputs = [
        "7J4VQJJ3+MH",       # Full code -- Chennai area
        "7J4V+MH",            # Short full code
        "INVALID+CODE",       # Should raise error gracefully
    ]

    print("=" * 50)
    print("  PLUS CODE CONVERTER TEST")
    print("=" * 50)

    for test in test_inputs:
        print(f"\nInput: '{test}'")

        try:
            result = convert_plus_code(test)
            print("Parsed LocationPoint:")
            for key, value in result.items():
                print(f"  {key:<22} : {value}")

        except ValueError as e:
            print(f"  [ERROR] {e}")

        print("\n" + "-" * 50)
