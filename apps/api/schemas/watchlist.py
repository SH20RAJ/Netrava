"""Watchlist and Entry Schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class WatchlistEntryBase(BaseModel):
    identifier: str  # Normalized plate or person ID
    secondary_identifier: Optional[str] = None
    threat_level: str = "HIGH"  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    case_reference: Optional[str] = None
    notes: Optional[str] = None
    effective_from: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True


class WatchlistEntryCreate(WatchlistEntryBase):
    pass


class WatchlistEntryOut(WatchlistEntryBase):
    id: str
    watchlist_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class WatchlistBase(BaseModel):
    name: str
    category: str  # STOLEN_VEHICLE, WANTED_VEHICLE, MISSING_PERSON, etc.
    description: Optional[str] = None
    department: str = "Gujarat Police"
    is_active: bool = True


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistOut(WatchlistBase):
    id: str
    created_by: str
    created_at: datetime
    entries: List[WatchlistEntryOut] = []

    class Config:
        from_attributes = True
