"""Audit Log Schemas."""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel


class AuditLogBase(BaseModel):
    user_id: str
    user_name: str
    user_role: str
    ip_address: str
    action: str
    entity_type: str
    entity_id: str
    details: Dict[str, Any] = {}


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogOut(AuditLogBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True
