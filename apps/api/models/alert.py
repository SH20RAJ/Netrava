"""Alert Model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from db.session import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(64), nullable=False, index=True)
    camera_id = Column(String(36), ForeignKey("cameras.id"), nullable=False, index=True)
    watchlist_entry_id = Column(String(36), ForeignKey("watchlist_entries.id"), nullable=True)
    
    # Severity: INFO, LOW, MEDIUM, HIGH, CRITICAL
    severity = Column(String(32), nullable=False, default="HIGH", index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    matched_entity = Column(String(64), nullable=False, index=True)  # Plate or Entity ID
    match_confidence = Column(Float, nullable=False)
    
    # Sighting Coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Evidence snapshots
    evidence_frame_uri = Column(Text, nullable=True)
    evidence_crop_uri = Column(Text, nullable=True)
    
    # Status: NEW, ACKNOWLEDGED, ESCALATED, RESOLVED, FALSE_POSITIVE
    status = Column(String(32), default="NEW", index=True)
    assigned_to = Column(String(64), nullable=True)
    acknowledged_by = Column(String(64), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
