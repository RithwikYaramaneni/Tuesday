import json
from gps_parser       import parse_gps
from address_geocoder import geocode_address
from w3w_converter    import convert_w3w


# ── Main entry point ──────────────────────────────────────────────────────────

def normalize_signals(signals: list) -> list:
    location_points = []

    for i, signal in enumerate(signals):
        signal_type = signal.get("type", "").upper()
        data        = signal.get("data", "")

        print(f"\n[Normalizer] Processing signal {i+1}/{len(signals)} — type: {signal_type}")

        try:
            point = _parse_one(signal_type, data)
            location_points.append(point)
            print(f"  ✅ Success — lat: {point['latitude']}, lon: {point['longitude']}")

        except Exception as e:
            # Don't crash the whole request if one signal fails
            print(f"  ⚠️  Skipped signal [{signal_type}]: {e}")
            continue

    print(f"\n[Normalizer] Done. {len(location_points)}/{len(signals)} signals parsed successfully.")
    return location_points


# ── Router ────────────────────────────────────────────────────────────────────

def _parse_one(signal_type: str, data: str) -> dict:
    if signal_type == "GPS":
        return parse_gps(data)

    elif signal_type == "W3W":
        return convert_w3w(data)

    elif signal_type == "ADDRESS":
        return geocode_address(data)

    elif signal_type == "CELL":
        return _parse_cell(data)

    elif signal_type == "LANDMARK":
        return _parse_landmark(data)

    elif signal_type == "WIFI":
        return _parse_wifi(data)

    else:
        raise ValueError(f"Unsupported signal type: '{signal_type}'")


# ── Built-in parsers for simpler signal types ─────────────────────────────────

def _parse_cell(data: str) -> dict:
    import uuid
    from datetime import datetime, timezone

    try:
        cell = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError(f"CELL data is not valid JSON: '{data}'")

    tower_lat = cell.get("tower_lat")
    tower_lon = cell.get("tower_lon")
    signal_dbm = cell.get("signal_dbm", None)

    if tower_lat is None or tower_lon is None:
        raise ValueError("CELL data missing 'tower_lat' or 'tower_lon'")

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "signal_id":           str(uuid.uuid4()),
        "latitude":            round(float(tower_lat), 6),
        "longitude":           round(float(tower_lon), 6),
        "altitude_m":          None,
        "timestamp_utc":       timestamp_utc,
        "source":              "CELL",
        "raw_input":           data.strip(),
        "accuracy_radius_m":   500.0,    # CELL default from schema
        "raw_confidence":      0.55,     # CELL default from schema
        "hdop":                None,
        "satellite_count":     None,
        "signal_strength_dbm": int(signal_dbm) if signal_dbm is not None else None,
        "is_indoor":           None,
        "floor_estimate":      None,
        "environment_mode":    "NORMAL",
        "is_outlier":          False,
        "outlier_reason":      None,
    }


def _parse_landmark(data: str) -> dict:
    raise NotImplementedError(
        "LANDMARK NLP parsing is not implemented yet. "
        "Pass this text in the 'caller_text' field instead — "
        "Person B/C will handle context extraction."
    )


def _parse_wifi(data: str) -> dict:
    import uuid
    from datetime import datetime, timezone

    try:
        wifi = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError(f"WIFI data is not valid JSON: '{data}'")

    lat = wifi.get("lat")
    lon = wifi.get("lon")
    accuracy = wifi.get("accuracy_m", 50.0)

    if lat is None or lon is None:
        raise ValueError("WIFI data missing 'lat' or 'lon'")

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "signal_id":           str(uuid.uuid4()),
        "latitude":            round(float(lat), 6),
        "longitude":           round(float(lon), 6),
        "altitude_m":          None,
        "timestamp_utc":       timestamp_utc,
        "source":              "WIFI",
        "raw_input":           data.strip(),
        "accuracy_radius_m":   float(accuracy),
        "raw_confidence":      0.65,
        "hdop":                None,
        "satellite_count":     None,
        "signal_strength_dbm": None,
        "is_indoor":           True,     # WiFi usually means indoors
        "floor_estimate":      None,
        "environment_mode":    "NORMAL",
        "is_outlier":          False,
        "outlier_reason":      None,
    }


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simulates the exact request body from the POST /locate API contract
    test_signals = [
        {
            "type": "GPS",
            "data": "$GPGGA,092311,1304.96,N,08016.24,E,1,07,1.2,14.5,M,,,,"
        },
        {
            "type": "W3W",
            "data": "///fills.snap.brave"
        },
        {
            "type": "ADDRESS",
            "data": "Anna Salai, Chennai"
        },
        {
            "type": "CELL",
            "data": '{"tower_lat": 13.071, "tower_lon": 80.258, "signal_dbm": -102}'
        },
    ]

    print("=" * 55)
    print("  NORMALIZER TEST — All signal types")
    print("=" * 55)

    results = normalize_signals(test_signals)

    print("\n" + "=" * 55)
    print(f"  OUTPUT — {len(results)} LocationPoint(s)")
    print("=" * 55)

    for idx, point in enumerate(results):
        print(f"\n--- Signal {idx + 1}: {point['source']} ---")
        for key, value in point.items():
            print(f"  {key:<22} : {value}")
