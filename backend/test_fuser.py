import sys
import os

# Put backend root on the path so Python finds models.py & fusion module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import LocationPoint
from fusion.fuser import fuse_locations

def run_tests():
    # ── Scenario 1: Outdoors ── 
    # GPS is good, W3W perfect, CELL decent. All agree closely.
    scenario_1 = [
        {"signal_id": "1", "latitude": 13.0100, "longitude": 80.0100, "timestamp_utc": "Z", "source": "GPS", "raw_input": "-", "accuracy_radius_m": 10.0, "raw_confidence": 0.0, "is_indoor": False, "hdop": 1.2, "signal_strength_dbm": None},
        {"signal_id": "2", "latitude": 13.0102, "longitude": 80.0102, "timestamp_utc": "Z", "source": "W3W", "raw_input": "-", "accuracy_radius_m": 3.0, "raw_confidence": 0.0, "is_indoor": False, "hdop": None, "signal_strength_dbm": None},
        {"signal_id": "3", "latitude": 13.0105, "longitude": 80.0105, "timestamp_utc": "Z", "source": "CELL", "raw_input": "-", "accuracy_radius_m": 500.0, "raw_confidence": 0.0, "is_indoor": False, "hdop": None, "signal_strength_dbm": -85}
    ]

    # ── Scenario 2: Indoors ── 
    # GPS is highly imprecise and > 2km away from the cluster. WIFI and CELL are clustered.
    scenario_2 = [
        {"signal_id": "4", "latitude": 13.0500, "longitude": 80.0500, "timestamp_utc": "Z", "source": "GPS", "raw_input": "-", "accuracy_radius_m": 10.0, "raw_confidence": 0.0, "is_indoor": True, "hdop": 6.8, "signal_strength_dbm": None},  # Distant outlier, bad indoor HDOP
        {"signal_id": "5", "latitude": 13.0100, "longitude": 80.0100, "timestamp_utc": "Z", "source": "WIFI", "raw_input": "-", "accuracy_radius_m": 50.0, "raw_confidence": 0.0, "is_indoor": True, "hdop": None, "signal_strength_dbm": -60},
        {"signal_id": "6", "latitude": 13.0101, "longitude": 80.0101, "timestamp_utc": "Z", "source": "CELL", "raw_input": "-", "accuracy_radius_m": 500.0, "raw_confidence": 0.0, "is_indoor": True, "hdop": None, "signal_strength_dbm": -90}
    ]

    # ── Scenario 3: Disaster Mode ── 
    # Only 2 weak sources, too far for consensus, no outliers possible because it's only 2 nodes.
    scenario_3 = [
        {"signal_id": "7", "latitude": 13.0100, "longitude": 80.0100, "timestamp_utc": "Z", "source": "CELL", "raw_input": "-", "accuracy_radius_m": 500.0, "raw_confidence": 0.0, "is_indoor": False, "hdop": None, "signal_strength_dbm": -115}, # Severely degraded
        {"signal_id": "8", "latitude": 13.0300, "longitude": 80.0300, "timestamp_utc": "Z", "source": "LANDMARK", "raw_input": "-", "accuracy_radius_m": 1000.0, "raw_confidence": 0.0, "is_indoor": False, "hdop": None, "signal_strength_dbm": None}
    ]

    scenarios = [
        ("SCENARIO 1: OUTDOORS (High Confidence, Consensus)", scenario_1),
        ("SCENARIO 2: INDOORS (GPS Outlier, Ignored)", scenario_2),
        ("SCENARIO 3: DISASTER (Low Confidence, No Consensus)", scenario_3)
    ]

    for title, mock_dicts in scenarios:
        print(f"\n{title}\n{'-'*55}")
        
        # Hydrate dictionaries into LocationPoint objects as instructed
        points = [LocationPoint(**d) for d in mock_dicts]
        
        # Execute the Fuser pipeline
        result = fuse_locations(points)
        
        # Print the FusedLocation response exactly as requested
        print(f"Fused Latitude  : {result.latitude}")
        print(f"Fused Longitude : {result.longitude}")
        print(f"Confidence Rate : {result.confidence_score} (Status: {result.dispatch_status})")
        print(f"Certainty Radius: {result.uncertainty_radius_m} meters")
        print(f"Sources Ignored : {result.sources_ignored}")
        print(f"Explainable UI  : {result.explanation}")

if __name__ == "__main__":
    run_tests()
