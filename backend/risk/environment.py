"""
Environment mode detection for emergency location fusion.

Determines the operating environment from signal characteristics so that
downstream weight adjustments and dispatch logic can adapt accordingly.

Priority order:
  1. DISASTER  — any signal already tagged environment_mode="DISASTER"
  2. URBAN_CANYON — GPS hdop > 4 AND cell signal_strength_dbm < -100
  3. RURAL    — fewer than 2 CELL signals present
  4. NORMAL   — default
"""

from typing import List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models import LocationPoint, EnvMode


def detect_environment(signals: List[LocationPoint]) -> EnvMode:
    """
    Analyse incoming LocationPoint signals and return the environment mode.

    Rules (evaluated in priority order — first match wins):

    1. DISASTER : If ANY signal has environment_mode == "DISASTER", return
       immediately.  This is set externally when disaster_mode=True is
       passed in the API request.

    2. URBAN_CANYON : ANY GPS signal has hdop > 4  **AND**  ANY CELL signal
       has signal_strength_dbm < -100.  Both conditions must be true at
       the same time.

    3. RURAL : Fewer than 2 CELL-type signals are present in the list.

    4. NORMAL : None of the above conditions matched.

    Edge-case handling:
      - hdop is None  → treated as 0 (not high)
      - signal_strength_dbm is None → treated as 0 (not weak)
    """

    # --- 1. DISASTER -----------------------------------------------------------
    for sig in signals:
        if sig.environment_mode == "DISASTER":
            return "DISASTER"

    # --- 2. URBAN_CANYON -------------------------------------------------------
    gps_high_hdop = any(
        (sig.hdop if sig.hdop is not None else 0) > 4
        for sig in signals
        if sig.source == "GPS"
    )
    cell_weak_signal = any(
        (sig.signal_strength_dbm if sig.signal_strength_dbm is not None else 0) < -100
        for sig in signals
        if sig.source == "CELL"
    )
    if gps_high_hdop and cell_weak_signal:
        return "URBAN_CANYON"

    # --- 3. RURAL --------------------------------------------------------------
    cell_count = sum(1 for sig in signals if sig.source == "CELL")
    if cell_count < 2:
        return "RURAL"

    # --- 4. NORMAL (default) ---------------------------------------------------
    return "NORMAL"


# ---------------------------------------------------------------------------
# Quick self-tests — run with:  python -m risk.environment
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from datetime import datetime, timezone

    def _make_signal(**overrides) -> LocationPoint:
        """Helper to build a LocationPoint with sensible defaults."""
        defaults = {
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

    # Test 1 — DISASTER: any signal tagged DISASTER → immediate return
    signals_disaster = [
        _make_signal(source="GPS", environment_mode="DISASTER"),
        _make_signal(source="CELL", signal_strength_dbm=-80),
    ]
    result = detect_environment(signals_disaster)
    assert result == "DISASTER", f"Test 1 FAILED: expected DISASTER, got {result}"
    print("✅ Test 1 passed — DISASTER mode detected")

    # Test 2 — URBAN_CANYON: GPS hdop > 4 AND CELL signal < -100
    signals_urban = [
        _make_signal(source="GPS", hdop=7.8),
        _make_signal(source="CELL", signal_strength_dbm=-105),
        _make_signal(source="CELL", signal_strength_dbm=-95),
    ]
    result = detect_environment(signals_urban)
    assert result == "URBAN_CANYON", f"Test 2 FAILED: expected URBAN_CANYON, got {result}"
    print("✅ Test 2 passed — URBAN_CANYON mode detected")

    # Test 3 — RURAL: fewer than 2 CELL signals
    signals_rural = [
        _make_signal(source="GPS", hdop=1.2),
        _make_signal(source="CELL", signal_strength_dbm=-80),
    ]
    result = detect_environment(signals_rural)
    assert result == "RURAL", f"Test 3 FAILED: expected RURAL, got {result}"
    print("✅ Test 3 passed — RURAL mode detected")

    # Test 4 — NORMAL: 2+ CELL signals, no high hdop, no disaster
    signals_normal = [
        _make_signal(source="GPS", hdop=1.1),
        _make_signal(source="CELL", signal_strength_dbm=-80),
        _make_signal(source="CELL", signal_strength_dbm=-75),
    ]
    result = detect_environment(signals_normal)
    assert result == "NORMAL", f"Test 4 FAILED: expected NORMAL, got {result}"
    print("✅ Test 4 passed — NORMAL mode detected")

    print("\n🎉 All 4 environment detection tests passed!")
