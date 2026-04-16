from pydantic import BaseModel
from typing import Optional, List, Literal
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
    signal_strength_dbm: Optional[float] = None
    is_indoor: Optional[bool] = None
    floor_estimate: Optional[int] = None
    environment_mode: Optional[EnvMode] = "NORMAL"
    is_outlier: bool = False
    outlier_reason: Optional[str] = None


class FusedLocation(BaseModel):
    fused_lat: Optional[float] = None
    fused_lon: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence_score: float
    uncertainty_radius_m: Optional[float] = None
    dispatch_status: Optional[DispatchStatus] = None
    sources_used: List[str]
    sources_ignored: List[str]
    explanation: str
    followup_question: Optional[str] = None
    input_signals: Optional[List[LocationPoint]] = None


class LocateRequest(BaseModel):
    caller_text: Optional[str] = None
    signals: List[dict]
    disaster_mode: bool = False
