"""Route Reconstruction and Kinematic Assessment Schemas."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class KinematicAssessment(BaseModel):
    is_plausible: bool
    implied_speed_kmh: float
    distance_traveled_km: float
    transit_duration_minutes: float
    assessment_narrative: str
    anomaly_detected: bool
    anomaly_type: Optional[str] = None  # e.g., "IMPOSSIBLE_SPEED_CLONED_PLATE", "BACKTRACKING"


class RouteWaypoint(BaseModel):
    step_number: int
    sighting_id: str
    camera_id: str
    camera_name: str
    district: str
    zone: str
    latitude: float
    longitude: float
    timestamp: datetime
    plate_confidence: float
    vehicle_class: str
    vehicle_color: str
    frame_uri: Optional[str] = None
    plate_crop_uri: Optional[str] = None
    evidence_hash: Optional[str] = None
    kinematic_from_prev: Optional[KinematicAssessment] = None


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class RouteReconstructionOut(BaseModel):
    normalized_plate: str
    total_waypoints: int
    start_time: datetime
    end_time: datetime
    total_distance_km: float
    total_duration_minutes: float
    average_speed_kmh: float
    waypoints: List[RouteWaypoint]
    geojson_polyline: GeoJSONFeatureCollection
    overall_confidence: float
    is_watchlist_hit: bool
    watchlist_severity: Optional[str] = None
    kinematic_summary: str
