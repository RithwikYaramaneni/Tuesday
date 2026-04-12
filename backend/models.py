from pydantic import BaseModel
from typing import Optional, List

class LocationPoint(BaseModel):
    signal_id: str
    latitude: float
    longitude: float
    altitude_m: Optional[float] = None
    timestamp_utc: str
    source: str
    raw_input: str
    accuracy_radius_m: float
    raw_confidence: float
    hdop: Optional[float] = None
    satellite_count: Optional[int] = None
    signal_strength_dbm: Optional[float] = None
    is_indoor: Optional[bool] = None
    floor_estimate: Optional[int] = None
    environment_mode: Optional[str] = "NORMAL"
    is_outlier: Optional[bool] = False
    outlier_reason: Optional[str] = None

class FusedLocation(BaseModel):
    latitude: float
    longitude: float
    confidence_score: float
    explanation: str
    uncertainty_radius_m: Optional[float] = None
    sources_used: List[str]
    sources_ignored: List[str]
    dispatch_status: Optional[str] = None
