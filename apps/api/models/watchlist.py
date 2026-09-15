"""Watchlist and Watchlist Entries Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    # Categories: STOLEN_VEHICLE, WANTED_VEHICLE, MISSING_PERSON, PERSON_OF_INTEREST, TRAFFIC_VIOLATOR, CUSTOM_OPERATION
    category = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    department = Column(String(128), nullable=False, default="Gujarat Police")
    is_active = Column(Boolean, default=True)
    created_by = Column(String(64), default="SYSTEM")
    created_at = Column(DateTime, default=datetime.utcnow)

    entries = relationship("WatchlistEntry", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    watchlist_id = Column(String(36), ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(32), default="vehicle")
    identifier = Column(String(64), nullable=False, index=True)  # Normalized plate e.g. GJ01AB1234
    secondary_identifier = Column(String(64), nullable=True)     # Make / Model or Chassis
    # Threat levels: INFO, LOW, MEDIUM, HIGH, CRITICAL
    threat_level = Column(String(32), default="HIGH")
    case_reference = Column(String(128), nullable=True)          # e.g., "FIR 142/2026 Vastrapur PS"
    notes = Column(Text, nullable=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    watchlist = relationship("Watchlist", back_populates="entries")
