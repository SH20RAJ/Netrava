"""Camera Registry Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text
from db.session import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    department = Column(String(128), nullable=False, default="Gujarat Police", index=True)
    district = Column(String(128), nullable=False, index=True)
    zone = Column(String(128), nullable=False)
    sub_district = Column(String(128), nullable=True)
    police_station = Column(String(128), nullable=True)
    
    # Geospatial Coordinates (WGS84 EPSG:4326)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    elevation_m = Column(Float, nullable=True, default=0.0)
    
    # Hardware & Protocol Metadata
    camera_type = Column(String(64), default="FIXED_IP")
    manufacturer = Column(String(64), nullable=False)
    model = Column(String(128), nullable=True)
    firmware_version = Column(String(64), nullable=True)
    protocol = Column(String(32), default="RTSP")  # RTSP, ONVIF, WEBRTC, SYNTHETIC
    rtsp_url = Column(Text, nullable=False)
    stream_relay_url = Column(Text, nullable=True)
    
    # Lifecycle & Telemetry
    # States: REGISTERED, CONNECTING, ONLINE, DEGRADED, OFFLINE, MAINTENANCE, DISABLED
    status = Column(String(32), default="ONLINE", index=True)
    health_score = Column(Float, default=98.5)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    
    # Data Governance
    data_classification = Column(String(32), default="INTERNAL")
    retention_days = Column(Integer, default=30)
    tags = Column(JSON, default=list)
    analytics_config = Column(JSON, default=lambda: {
        "anpr_enabled": True,
        "sampling_fps": 5,
        "vehicle_detection": True,
        "motion_sensitivity": 0.8
    })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
