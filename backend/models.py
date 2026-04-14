from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
import uuid

SourceType = Literal["GPS", "CELL", "W3W", "ADDRESS", "LANDMARK", "WIFI"]
EnvMode = Literal["URBAN_CANYON", "RURAL", "DISASTER", "NORMAL"]
DispatchStatus = Literal["GREEN", "YELLOW", "RED"]


class LocationPoint(BaseModel):
    signal_id: str = str(uuid.uuid4())
    latitude: float
    longitude: float
    altitude_m: Optional[float] = None
    timestamp_utc: str
    source: SourceType
    raw_input: str
    accuracy_radius_m: float
    raw_confidence: float
    hdop: Optional[float] = None
    satellite_count: Optional[int] = None
    signal_strength_dbm: Optional[int] = None
    is_indoor: Optional[bool] = None
    floor_estimate: Optional[int] = None
    environment_mode: Optional[EnvMode] = "NORMAL"
    is_outlier: bool = False
    outlier_reason: Optional[str] = None


class FusedLocation(BaseModel):
    fused_lat: float
    fused_lon: float
    confidence_score: float
    uncertainty_radius_m: float
    dispatch_status: DispatchStatus
    sources_used: List[str]
    sources_ignored: List[str]
    explanation: str
    followup_question: Optional[str] = None
    input_signals: List[LocationPoint]


class LocateRequest(BaseModel):
    caller_text: Optional[str] = None
    signals: List[dict]
    disaster_mode: bool = False
