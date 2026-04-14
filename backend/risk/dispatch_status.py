"""
Dispatch status logic for the Emergency Location Fusion System.

Maps a fused confidence score to a GREEN / YELLOW / RED dispatch decision
and generates context-aware followup questions for the dispatcher when
the confidence is not high enough to dispatch immediately.
"""

from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models import DispatchStatus, EnvMode


def get_dispatch_status(confidence_score: float, disaster_mode: bool = False) -> DispatchStatus:
    """
    Determine the dispatch status from the fused confidence score.

    Rules (evaluated in order):
      1. disaster_mode is True  → always "RED" regardless of score
      2. confidence_score > 0.75 → "GREEN"  — Dispatch Now
      3. 0.4 <= confidence_score <= 0.75 → "YELLOW" — Verify via Caller
      4. confidence_score < 0.4  → "RED"    — Search Zone Mode

    Args:
        confidence_score: 0.0–1.0 fused confidence from the fusion engine.
        disaster_mode:    True when the API request includes disaster_mode=True.

    Returns:
        One of "GREEN", "YELLOW", or "RED".
    """
    if disaster_mode:
        return "RED"

    if confidence_score > 0.75:
        return "GREEN"
    elif confidence_score >= 0.4:
        return "YELLOW"
    else:
        return "RED"


def get_followup_question(
    status: DispatchStatus,
    environment: EnvMode,
    sources_ignored: List[str],
) -> Optional[str]:
    """
    Generate a context-aware followup question for the dispatcher.

    Returns None when status is GREEN (no followup needed).
    Otherwise selects the most relevant question based on ignored sources
    and the detected environment mode.

    Evaluation order (first match wins):
      1. GPS in sources_ignored → indoor/underground question
      2. URBAN_CANYON environment → street-sign/landmark question
      3. DISASTER environment   → large-structure question
      4. RURAL environment      → road-junction/farm question
      5. Default fallback       → shop-name/bus-stop question

    Args:
        status:          The dispatch status ("GREEN", "YELLOW", or "RED").
        environment:     The detected environment mode.
        sources_ignored: List of source type strings that were excluded.

    Returns:
        A followup question string, or None if status is GREEN.
    """
    if status == "GREEN":
        return None

    # --- Check conditions in specified priority order ---

    if "GPS" in sources_ignored:
        return (
            "Ask the caller: are you currently inside a building "
            "or underground car park?"
        )

    if environment == "URBAN_CANYON":
        return (
            "Ask the caller: can you see any street signs, large buildings, "
            "or landmarks directly above you?"
        )

    if environment == "DISASTER":
        return (
            "Ask the caller: can you describe any large structures, "
            "coloured buildings, or road markings visible from where you are?"
        )

    if environment == "RURAL":
        return (
            "Ask the caller: are you near any road junctions, bridges, "
            "farms, or water features?"
        )

    # Default fallback
    return (
        "Ask the caller: can you read out any nearby shop names, "
        "bus stop numbers, or street signs?"
    )


# ---------------------------------------------------------------------------
# Self-tests — run with:  python -m risk.dispatch_status
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("Dispatch Status — Demo Scenario Tests")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # Scenario 1 — GREEN (high confidence)
    #   GPS + W3W agree, confidence ~0.88
    # -----------------------------------------------------------------------
    score_1 = 0.88
    status_1 = get_dispatch_status(score_1, disaster_mode=False)
    question_1 = get_followup_question(status_1, "NORMAL", sources_ignored=["CELL"])

    print(f"\n🟢  Scenario 1 — GREEN")
    print(f"    confidence_score = {score_1}")
    print(f"    disaster_mode    = False")
    print(f"    dispatch_status  = {status_1}")
    print(f"    followup_question = {question_1}")
    assert status_1 == "GREEN", f"FAILED: expected GREEN, got {status_1}"
    assert question_1 is None, f"FAILED: expected None, got {question_1}"
    print("    ✅ PASSED")

    # -----------------------------------------------------------------------
    # Scenario 2 — YELLOW (conflict, indoor GPS ignored)
    #   GPS indoor + high HDOP, confidence ~0.55
    # -----------------------------------------------------------------------
    score_2 = 0.55
    status_2 = get_dispatch_status(score_2, disaster_mode=False)
    question_2 = get_followup_question(status_2, "URBAN_CANYON", sources_ignored=["GPS"])

    print(f"\n🟡  Scenario 2 — YELLOW")
    print(f"    confidence_score = {score_2}")
    print(f"    disaster_mode    = False")
    print(f"    dispatch_status  = {status_2}")
    print(f"    followup_question = {question_2}")
    assert status_2 == "YELLOW", f"FAILED: expected YELLOW, got {status_2}"
    assert question_2 is not None, "FAILED: expected a followup question"
    assert "inside a building" in question_2, f"FAILED: expected indoor question, got {question_2}"
    print("    ✅ PASSED")

    # -----------------------------------------------------------------------
    # Scenario 3 — RED (disaster, minimal signals)
    #   Single weak cell tower, confidence ~0.30, disaster implied
    # -----------------------------------------------------------------------
    score_3 = 0.30
    status_3 = get_dispatch_status(score_3, disaster_mode=True)
    question_3 = get_followup_question(status_3, "DISASTER", sources_ignored=[])

    print(f"\n🔴  Scenario 3 — RED (disaster)")
    print(f"    confidence_score = {score_3}")
    print(f"    disaster_mode    = True")
    print(f"    dispatch_status  = {status_3}")
    print(f"    followup_question = {question_3}")
    assert status_3 == "RED", f"FAILED: expected RED, got {status_3}"
    assert question_3 is not None, "FAILED: expected a followup question"
    assert "large structures" in question_3, f"FAILED: expected disaster question, got {question_3}"
    print("    ✅ PASSED")

    # -----------------------------------------------------------------------
    # Extra edge-case: disaster_mode overrides a high confidence score
    # -----------------------------------------------------------------------
    status_override = get_dispatch_status(0.95, disaster_mode=True)
    assert status_override == "RED", f"FAILED: disaster_mode should force RED, got {status_override}"
    print(f"\n⚠️  Edge case — disaster_mode=True overrides score 0.95 → {status_override}  ✅")

    print("\n" + "=" * 60)
    print("🎉 All dispatch status tests passed!")
    print("=" * 60)
