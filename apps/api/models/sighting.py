"""Vehicle Sighting and AI Detection Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON
from db.session import Base


class VehicleSighting(Base):
    __tablename__ = "vehicle_sightings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    camera_id = Column(String(36), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Coordinates of sighting camera
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # ANPR Identification Data
    plate_number = Column(String(32), nullable=False)
    normalized_plate = Column(String(32), nullable=False, index=True)
    plate_confidence = Column(Float, nullable=False)
    
    # Vehicle Attributes
    vehicle_class = Column(String(32), default="car")   # car, suv, truck, bus, motorcycle, auto_rickshaw
    vehicle_color = Column(String(32), default="white")
    track_id = Column(String(64), nullable=True)
    appearance_embedding = Column(JSON, default=list)    # Feature vector
    
    # Tamper-Evident Evidence References
    frame_uri = Column(Text, nullable=True)
    plate_crop_uri = Column(Text, nullable=True)
    evidence_hash = Column(String(64), nullable=True)   # SHA-256 integrity hash
    
    created_at = Column(DateTime, default=datetime.utcnow)
