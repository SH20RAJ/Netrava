"""Camera Pydantic Schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CameraBase(BaseModel):
    name: str
    external_id: str
    department: str = "Gujarat Police"
    district: str
    zone: str
    sub_district: Optional[str] = None
    police_station: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    elevation_m: Optional[float] = 0.0
    camera_type: str = "FIXED_IP"
    manufacturer: str
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    protocol: str = "RTSP"
    rtsp_url: str
    data_classification: str = "INTERNAL"
    retention_days: int = 30
    tags: List[str] = []
    analytics_config: Dict[str, Any] = {
        "anpr_enabled": True,
        "sampling_fps": 5,
        "vehicle_detection": True
    }


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    district: Optional[str] = None
    zone: Optional[str] = None
    police_station: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rtsp_url: Optional[str] = None
    status: Optional[str] = None
    data_classification: Optional[str] = None
    retention_days: Optional[int] = None
    analytics_config: Optional[Dict[str, Any]] = None


class CameraOut(CameraBase):
    id: str
    status: str
    health_score: float
    stream_relay_url: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CameraHealthOut(BaseModel):
    camera_id: str
    external_id: str
    name: str
    status: str
    health_score: float
    last_ping_latency_ms: float
    packet_loss_pct: float
    fps_measured: float
    bitrate_kbps: float
    last_seen_at: datetime


class CameraClusterOut(BaseModel):
    district: str
    total_cameras: int
    online_cameras: int
    degraded_cameras: int
    offline_cameras: int
    centroid_lat: float
    centroid_lon: float
