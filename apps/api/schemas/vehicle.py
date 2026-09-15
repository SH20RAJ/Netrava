"""Vehicle Intelligence & Sighting Schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SightingBase(BaseModel):
    event_id: str
    camera_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    plate_number: str
    normalized_plate: str
    plate_confidence: float = Field(..., ge=0.0, le=1.0)
    vehicle_class: str = "car"
    vehicle_color: str = "white"
    track_id: Optional[str] = None
    frame_uri: Optional[str] = None
    plate_crop_uri: Optional[str] = None
    evidence_hash: Optional[str] = None


class SightingCreate(SightingBase):
    appearance_embedding: Optional[List[float]] = []


class SightingOut(SightingBase):
    id: str
    camera_name: Optional[str] = None
    district: Optional[str] = None
    zone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VehicleDossierOut(BaseModel):
    normalized_plate: str
    raw_plate_sample: str
    vehicle_class: str
    dominant_color: str
    first_seen: datetime
    last_seen: datetime
    total_sightings: int
    cameras_visited_count: int
    districts_visited: List[str]
    watchlist_flagged: bool
    watchlist_details: Optional[Dict[str, Any]] = None
    latest_sighting: Optional[SightingOut] = None
    risk_score: float  # 0 to 100
    risk_level: str    # LOW, MEDIUM, HIGH, CRITICAL
