import pynmea2
import uuid
from datetime import datetime, timezone


def parse_gps(nmea_sentence: str) -> dict:

    try:
        msg = pynmea2.parse(nmea_sentence.strip())
    except pynmea2.ParseError as e:
        raise ValueError(f"Failed to parse NMEA sentence: {e}")

    # pynmea2 gives lat/lon as decimal degrees directly
    latitude  = msg.latitude
    longitude = msg.longitude

    if latitude == 0.0 and longitude == 0.0:
        raise ValueError("GPS returned 0,0 — likely no satellite fix.")

    # HDOP (horizontal dilution of precision) — lower is better
    try:
        hdop = float(msg.horizontal_dil) if msg.horizontal_dil else None
    except (ValueError, AttributeError):
        hdop = None

    # Satellite count
    try:
        satellite_count = int(msg.num_sats) if msg.num_sats else None
    except (ValueError, AttributeError):
        satellite_count = None

    # Altitude in metres
    try:
        altitude_m = float(msg.altitude) if msg.altitude else None
    except (ValueError, AttributeError):
        altitude_m = None

    # Accuracy radius: tighter when more satellites & better HDOP
    # Base GPS accuracy ~15 m; degrade if HDOP is high or satellites are few
    accuracy_radius_m = _estimate_accuracy(hdop, satellite_count)

    # Raw confidence: GPS default is 0.9, lower if HDOP is poor
    raw_confidence = _estimate_confidence(hdop, satellite_count)

    # Build the timestamp — NMEA gives time only (HHMMSS), use today's UTC date
    try:
        time_str = msg.timestamp.strftime("%H:%M:%S") if msg.timestamp else "00:00:00"
    except AttributeError:
        time_str = "00:00:00"

    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    timestamp_utc = f"{today_utc}T{time_str}Z"

    location_point = {
        "signal_id":          str(uuid.uuid4()),
        "latitude":           round(latitude, 6),
        "longitude":          round(longitude, 6),
        "altitude_m":         altitude_m,
        "timestamp_utc":      timestamp_utc,
        "source":             "GPS",
        "raw_input":          nmea_sentence.strip(),
        "accuracy_radius_m":  accuracy_radius_m,
        "raw_confidence":     raw_confidence,
        "hdop":               hdop,
        "satellite_count":    satellite_count,
        "signal_strength_dbm": None,      # GPS doesn't have this
        "is_indoor":          False,
        "floor_estimate":     None,
        "environment_mode":   "NORMAL",
        "is_outlier":         False,
        "outlier_reason":     None,
    }

    return location_point


# ── Helper functions ──────────────────────────────────────────────────────────

def _estimate_accuracy(hdop, satellite_count) -> float:
    """
    Estimate accuracy radius in metres.
    GPS base accuracy is ~15 m. Degrades with high HDOP or few satellites.
    """
    base = 15.0

    if hdop is not None:
        if hdop < 1.5:
            base = 10.0       # Excellent
        elif hdop < 3.0:
            base = 15.0       # Good
        elif hdop < 6.0:
            base = 30.0       # Moderate
        else:
            base = 80.0       # Poor

    if satellite_count is not None and satellite_count < 4:
        base *= 2.0           # Very few satellites = much less reliable

    return round(base, 1)


def _estimate_confidence(hdop, satellite_count) -> float:
    confidence = 0.9

    if hdop is not None:
        if hdop < 1.5:
            confidence = 0.95
        elif hdop < 3.0:
            confidence = 0.90
        elif hdop < 6.0:
            confidence = 0.75
        else:
            confidence = 0.55

    if satellite_count is not None and satellite_count < 4:
        confidence -= 0.15

    return round(max(0.0, min(1.0, confidence)), 2)


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with the demo scenario from the project spec
    test_sentence = "$GPGGA,092311,1304.96,N,08016.24,E,1,07,1.2,14.5,M,,,,"

    print("Input NMEA sentence:")
    print(f"  {test_sentence}\n")

    result = parse_gps(test_sentence)

    print("Parsed LocationPoint:")
    for key, value in result.items():
        print(f"  {key:<22} : {value}")
