"""Investigation and Case Dossier Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    lead_investigator = Column(String(64), nullable=False)
    department = Column(String(128), default="Gujarat Police CID Crime")
    target_plate = Column(String(32), nullable=True, index=True)
    status = Column(String(32), default="OPEN")  # OPEN, IN_PROGRESS, CLOSED, ARCHIVED
    summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("InvestigationEvent", back_populates="investigation", cascade="all, delete-orphan")


class InvestigationEvent(Base):
    __tablename__ = "investigation_events"

    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), primary_key=True)
    sighting_id = Column(String(36), ForeignKey("vehicle_sightings.id", ondelete="CASCADE"), primary_key=True)
    relevance_notes = Column(Text, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="events")
