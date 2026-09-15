"""System Health & 80,000-Camera Capacity Calculator Schemas."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ServiceComponentHealth(BaseModel):
    name: str
    status: str  # OPERATIONAL, DEGRADED, OFFLINE
    latency_ms: float
    details: Dict[str, Any] = {}


class SystemHealthOut(BaseModel):
    overall_status: str
    environment: str
    uptime_seconds: float
    connected_cameras: int
    online_cameras: int
    degraded_cameras: int
    offline_cameras: int
    active_alerts: int
    events_per_minute: float
    components: List[ServiceComponentHealth]


class ScalabilityCalculationRequest(BaseModel):
    camera_count: int = Field(default=80000, ge=1, le=500000, description="Total state cameras")
    stream_resolution: str = Field(default="1080p", description="720p, 1080p, 4K")
    average_bitrate_mbps: float = Field(default=2.5, ge=0.5, le=25.0)
    analytics_fps: float = Field(default=5.0, ge=1.0, le=30.0)
    hot_storage_days: int = Field(default=7, ge=1, le=90)
    warm_storage_days: int = Field(default=365, ge=30, le=3650)
    regional_hubs_count: int = Field(default=34, ge=1, le=100)
    gpu_inference_rate_fps: float = Field(default=350.0, description="FPS per GPU (e.g. NVIDIA L4 INT8)")


class ScalabilityCalculationResult(BaseModel):
    camera_count: int
    # Bandwidth Analysis
    centralized_raw_video_bandwidth_gbps: float
    netrava_edge_to_cloud_bandwidth_mbps: float
    bandwidth_reduction_pct: float
    
    # Compute & Inference Requirements
    total_statewide_inferences_per_sec: float
    cameras_per_regional_hub: int
    inferences_per_sec_per_hub: float
    gpus_required_per_hub: int
    total_statewide_gpus_required: int
    gpu_hardware_recommendation: str
    
    # Tiered Storage Architecture
    hot_storage_petabytes: float
    hot_storage_per_hub_terabytes: float
    warm_metadata_evidence_terabytes: float
    storage_architecture_recommendation: str
    
    # Formula & Assumptions Traceability
    assumptions: List[Dict[str, str]]
