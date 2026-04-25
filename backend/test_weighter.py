import sys
import os

# Add backend root to sys.path so we can import models.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import LocationPoint
from fusion.weighter import assign_weights

def run_tests():
    # Mock data representing different scenarios
    points = [
        # 1. Good Outdoor GPS (Expected base = 0.90, penalty = 0)
        LocationPoint(
            signal_id="1", latitude=13.0, longitude=80.0, timestamp_utc="NOW",
            source="GPS", raw_input="demo", accuracy_radius_m=10.0, raw_confidence=0.0,
            is_indoor=False, hdop=1.2, signal_strength_dbm=None
        ),
        # 2. Indoor GPS with very poor HDOP (Expected base = 0.30, penalty = 0.40 -> Final 0.0)
        LocationPoint(
            signal_id="2", latitude=13.0, longitude=80.0, timestamp_utc="NOW",
            source="GPS", raw_input="demo", accuracy_radius_m=10.0, raw_confidence=0.0,
            is_indoor=True, hdop=6.4, signal_strength_dbm=None
        ),
        # 3. Cell tower with very weak signal strength (Base = 0.55, penalty = 0.20 -> Final 0.35)
        LocationPoint(
            signal_id="3", latitude=13.0, longitude=80.0, timestamp_utc="NOW",
            source="CELL", raw_input="demo", accuracy_radius_m=500.0, raw_confidence=0.0,
            is_indoor=None, hdop=None, signal_strength_dbm=-115
        ),
        # 4. What3Words signal (Base = 0.85, no penalties applicable -> Final 0.85)
        LocationPoint(
            signal_id="4", latitude=13.0, longitude=80.0, timestamp_utc="NOW",
            source="W3W", raw_input="demo", accuracy_radius_m=3.0, raw_confidence=0.0,
            is_indoor=False, hdop=None, signal_strength_dbm=None
        )
    ]
    
    print("=== RAW CONFIDENCE (BEFORE ENGINE) ===")
    for p in points:
         print(f"{p.source:<5} | Indoor: {str(p.is_indoor):<5} | HDOP: {str(p.hdop):<4} | dBm: {str(p.signal_strength_dbm):<4} --> Confidence: {p.raw_confidence}")

    weighted_points = assign_weights(points)

    print("\n=== ASSIGNED WEIGHTS (AFTER ENGINE)  ===")
    for p in weighted_points:
         print(f"{p.source:<5} --> Output Confidence: {p.raw_confidence}")

if __name__ == "__main__":
    run_tests()
