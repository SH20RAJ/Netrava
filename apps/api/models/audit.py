"""Immutable Security Audit Log Model."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), nullable=False, index=True)
    user_name = Column(String(128), nullable=False)
    user_role = Column(String(32), nullable=False)
    ip_address = Column(String(45), nullable=False)
    action = Column(String(64), nullable=False, index=True)  # VIEW_STREAM, SEARCH_VEHICLE, EXPORT_REPORT
    entity_type = Column(String(64), nullable=False)         # CAMERA, VEHICLE, DOSSIER, WATCHLIST
    entity_id = Column(String(128), nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
