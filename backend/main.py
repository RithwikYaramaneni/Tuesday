"""
FastAPI entry point for the Emergency Location Fusion System.

Person C — Risk Context + API Layer

This server accepts raw location signals via POST /locate, runs them through
the ingestion → fusion → risk pipeline, and returns a FusedLocation object
with dispatch status and an optional followup question for the dispatcher.

If Person A's ingestion or Person B's fusion modules are not yet available,
the server falls back to inline mock implementations so Person D can test
the UI immediately.

Run:
    uvicorn main:app --reload --port 8000
    Docs:  http://localhost:8000/docs
"""

import traceback
import json
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import LocationPoint, FusedLocation, LocateRequest
from risk.environment import detect_environment
from risk.dispatch_status import get_dispatch_status, get_followup_question

# ---------------------------------------------------------------------------
# Try to import Person A's normalizer.  Fall back to a mock if not ready yet.
# ---------------------------------------------------------------------------
try:
    from ingestion.normalizer import normalize_signals

    print("✅ Loaded Person A's ingestion/normalizer module")
except ImportError:
    print("⚠️  ingestion/normalizer not found — using built-in mock normalizer")

    def normalize(signal_type: str, signal_data: str) -> LocationPoint:
        """
        Mock normalizer: converts raw signal dicts into LocationPoints with
        sensible default coordinates so the pipeline can run end-to-end.
        """
        now = datetime.now(timezone.utc).isoformat()

        if signal_type == "GPS":
            # Try to extract lat/lon from NMEA $GPGGA sentence or raw lat/lon
            lat, lon, hdop, sat, alt = 13.0827, 80.2707, 1.2, 7, 14.5
            if signal_data.startswith("$"):
                try:
                    import pynmea2

                    msg = pynmea2.parse(signal_data)
                    lat = msg.latitude
                    lon = msg.longitude
                    hdop = float(msg.horizontal_dil) if msg.horizontal_dil else 1.2
                    sat = int(msg.num_sats) if msg.num_sats else 7
                    alt = float(msg.altitude) if msg.altitude else 14.5
                except Exception:
                    pass  # fall through to defaults
            else:
                try:
                    parts = signal_data.split(",")
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                except Exception:
                    pass

            is_indoor = hdop > 4 or sat < 4
            confidence = 0.30 if is_indoor else 0.90

            return LocationPoint(
                signal_id=str(uuid.uuid4()),
                latitude=lat,
                longitude=lon,
                altitude_m=alt,
                timestamp_utc=now,
                source="GPS",
                raw_input=signal_data,
                accuracy_radius_m=15.0 if not is_indoor else 150.0,
                raw_confidence=confidence,
                hdop=hdop,
                satellite_count=sat,
                is_indoor=is_indoor,
            )

        elif signal_type == "CELL":
            # Parse JSON cell tower data
            tower_lat, tower_lon, signal_dbm = 13.0827, 80.2707, -85
            try:
                cell = json.loads(signal_data)
                tower_lat = cell.get("tower_lat", tower_lat)
                tower_lon = cell.get("tower_lon", tower_lon)
                signal_dbm = cell.get("signal_dbm", signal_dbm)
            except Exception:
                pass

            return LocationPoint(
                signal_id=str(uuid.uuid4()),
                latitude=tower_lat,
                longitude=tower_lon,
                timestamp_utc=now,
                source="CELL",
                raw_input=signal_data,
                accuracy_radius_m=500.0,
                raw_confidence=0.55,
                signal_strength_dbm=signal_dbm,
            )

        elif signal_type == "W3W":
            # Mock: What3Words — use a pseudo-random Chennai coordinate based on input
            offset = (hash(signal_data) % 1000) / 100000.0 if signal_data else 0
            return LocationPoint(
                signal_id=str(uuid.uuid4()),
                latitude=13.0830 + offset,
                longitude=80.2712 - offset,
                timestamp_utc=now,
                source="W3W",
                raw_input=signal_data,
                accuracy_radius_m=3.0,
                raw_confidence=0.85,
            )

        elif signal_type == "ADDRESS":
            # Mock: geocoded address — use a pseudo-random Chennai coordinate based on input
            offset = (hash(signal_data) % 1000) / 100000.0 if signal_data else 0
            return LocationPoint(
                signal_id=str(uuid.uuid4()),
                latitude=13.0835 - offset,
                longitude=80.2700 + offset,
                timestamp_utc=now,
                source="ADDRESS",
                raw_input=signal_data,
                accuracy_radius_m=100.0,
                raw_confidence=0.70,
            )

        else:
            # Fallback for LANDMARK, WIFI, or unknown types
            return LocationPoint(
                signal_id=str(uuid.uuid4()),
                latitude=13.0827,
                longitude=80.2707,
                timestamp_utc=now,
                source="LANDMARK",
                raw_input=signal_data,
                accuracy_radius_m=200.0,
                raw_confidence=0.40,
            )

    def normalize_signals(signals: List[dict]) -> List[LocationPoint]:
        """Mock the real batch normalizer with the same request shape."""
        return [
            normalize(signal.get("type", "LANDMARK"), signal.get("data", ""))
            for signal in signals
        ]


# ---------------------------------------------------------------------------
# Try to import Person B's fuser.  Fall back to a mock if not ready yet.
# ---------------------------------------------------------------------------
try:
    from fusion.fuser import fuse_locations

    print("✅ Loaded Person B's fusion/fuser module")
except ImportError:
    print("⚠️  fusion/fuser not found — using built-in mock fuser")

    def fuse_locations(signals: List[LocationPoint]) -> FusedLocation:
        """
        Mock fuser: computes a simple weighted-average of all non-outlier
        signals and returns a valid FusedLocation.
        """
        # Separate usable signals from outliers
        usable = [s for s in signals if not s.is_outlier]
        if not usable:
            usable = signals  # use all if everything is flagged

        # --- Weighted average position ---
        total_weight = 0.0
        weighted_lat = 0.0
        weighted_lon = 0.0

        for s in usable:
            w = s.raw_confidence
            weighted_lat += s.latitude * w
            weighted_lon += s.longitude * w
            total_weight += w

        if total_weight > 0:
            fused_lat = weighted_lat / total_weight
            fused_lon = weighted_lon / total_weight
        else:
            fused_lat = usable[0].latitude
            fused_lon = usable[0].longitude

        # --- Confidence score ---
        avg_confidence = total_weight / len(usable) if usable else 0.3

        # Consensus boost: if multiple sources agree, bump confidence
        source_types = set(s.source for s in usable)
        if len(source_types) >= 2:
            avg_confidence = min(avg_confidence * 1.3, 1.0)

        # --- Uncertainty radius ---
        if usable:
            avg_radius = sum(s.accuracy_radius_m for s in usable) / len(usable)
        else:
            avg_radius = 500.0
        uncertainty = avg_radius * (1.0 - avg_confidence + 0.1)

        # --- Sources bookkeeping ---
        sources_used = sorted(set(s.source for s in usable))
        sources_ignored = sorted(
            set(s.source for s in signals if s.is_outlier)
        )

        # --- Explanation ---
        if len(sources_used) >= 2:
            explanation = (
                f"{' and '.join(sources_used)} signals agree; "
                f"merged with confidence {avg_confidence:.0%}."
            )
        elif len(sources_used) == 1:
            explanation = (
                f"Only {sources_used[0]} signal available; "
                f"confidence {avg_confidence:.0%}."
            )
        else:
            explanation = "No usable signals available."

        if sources_ignored:
            explanation += (
                f" Ignored: {', '.join(sources_ignored)}."
            )

        return FusedLocation(
            fused_lat=round(fused_lat, 6),
            fused_lon=round(fused_lon, 6),
            confidence_score=round(avg_confidence, 2),
            uncertainty_radius_m=round(uncertainty, 1),
            dispatch_status="GREEN",       # placeholder — overridden below
            sources_used=sources_used,
            sources_ignored=sources_ignored,
            explanation=explanation,
            followup_question=None,        # placeholder — overridden below
            input_signals=signals,
        )


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Emergency Location Fusion API",
    description=(
        "Fuses conflicting location signals (GPS, cell, W3W, address, landmarks) "
        "into a single high-confidence dispatch location with confidence rings "
        "and an Explainable Decision Panel."
    ),
    version="1.0",
)

# --- CORS — allow all origins so the React frontend can connect ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup event
# ---------------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    print("\n" + "=" * 60)
    print("🚨  Emergency Location Fusion API — v1.0")
    print("     Docs:   http://localhost:8000/docs")
    print("     Health: http://localhost:8000/health")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Simple health-check endpoint for monitoring."""
    return {"status": "ok", "version": "1.0"}


# ---------------------------------------------------------------------------
# POST /locate — main pipeline
# ---------------------------------------------------------------------------
@app.post("/locate", response_model=FusedLocation)
def locate(request: LocateRequest):
    """
    Accept raw location signals, fuse them, apply risk context, and return
    a FusedLocation with dispatch status and (optional) followup question.
    """
    try:
        # ==================================================================
        # Step 1 — Normalize each raw signal into a LocationPoint
        #          Uses Person A's normalizer (or mock fallback)
        # ==================================================================
        normalized_points = normalize_signals(request.signals)
        location_points: List[LocationPoint] = [
            point if isinstance(point, LocationPoint) else LocationPoint(**point)
            for point in normalized_points
        ]

        if not location_points:
            raise ValueError("No signals provided in the request.")

        # ==================================================================
        # Step 2 — Apply disaster_mode flag to every signal if set
        #          This ensures detect_environment returns DISASTER
        # ==================================================================
        if request.disaster_mode:
            for pt in location_points:
                pt.environment_mode = "DISASTER"

        # ==================================================================
        # Step 3 — Detect environment mode (URBAN_CANYON / RURAL / DISASTER / NORMAL)
        #          Uses Person C's environment.py
        # ==================================================================
        environment = detect_environment(location_points)

        # Tag each signal with the detected environment for audit trail
        for pt in location_points:
            if pt.environment_mode != "DISASTER":
                pt.environment_mode = environment

        # ==================================================================
        # Step 4 — Fuse signals into a single location
        #          Uses Person B's fuser (or mock fallback)
        # ==================================================================
        fused: FusedLocation = fuse_locations(location_points)

        if fused.fused_lat is None and fused.latitude is not None:
            fused.fused_lat = fused.latitude
        if fused.fused_lon is None and fused.longitude is not None:
            fused.fused_lon = fused.longitude
        if fused.latitude is None and fused.fused_lat is not None:
            fused.latitude = fused.fused_lat
        if fused.longitude is None and fused.fused_lon is not None:
            fused.longitude = fused.fused_lon

        # ==================================================================
        # Step 5 — Override dispatch_status using Person C's dispatch logic
        # ==================================================================
        status = get_dispatch_status(fused.confidence_score, request.disaster_mode)

        # ==================================================================
        # Step 6 — Generate a followup question if status is YELLOW or RED
        # ==================================================================
        question = get_followup_question(status, environment, fused.sources_ignored)

        # ==================================================================
        # Step 7 — Patch the FusedLocation and return
        # ==================================================================
        fused.dispatch_status = status
        fused.followup_question = question

        return fused

    except Exception as e:
        # Print full traceback to the terminal for debugging
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
