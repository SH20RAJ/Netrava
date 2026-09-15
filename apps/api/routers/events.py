"""Normalized AI Events API Router."""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.sighting import VehicleSighting
from models.camera import Camera
from schemas.vehicle import SightingOut
from core.security import get_current_user, User

router = APIRouter(prefix="/events", tags=["Normalized Events"])


@router.get("", response_model=List[SightingOut])
async def list_events(
    camera_id: Optional[str] = None,
    plate: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queries normalized vehicle and plate detection events."""
    query = (
        select(VehicleSighting, Camera.name, Camera.district, Camera.zone)
        .outerjoin(Camera, VehicleSighting.camera_id == Camera.id)
        .order_by(VehicleSighting.timestamp.desc())
    )
    if camera_id:
        query = query.where(VehicleSighting.camera_id == camera_id)
    if plate:
        normalized = plate.upper().replace(" ", "").replace("-", "")
        query = query.where(VehicleSighting.normalized_plate == normalized)
    query = query.limit(limit)

    results = (await db.execute(query)).all()
    outs = []
    for sighting, cam_name, district, zone in results:
        outs.append(SightingOut(
            id=sighting.id,
            event_id=sighting.event_id,
            camera_id=sighting.camera_id,
            camera_name=cam_name,
            district=district,
            zone=zone,
            timestamp=sighting.timestamp,
            latitude=sighting.latitude,
            longitude=sighting.longitude,
            plate_number=sighting.plate_number,
            normalized_plate=sighting.normalized_plate,
            plate_confidence=sighting.plate_confidence,
            vehicle_class=sighting.vehicle_class or "car",
            vehicle_color=sighting.vehicle_color or "white",
            track_id=sighting.track_id,
            frame_uri=sighting.frame_uri,
            plate_crop_uri=sighting.plate_crop_uri,
            evidence_hash=sighting.evidence_hash,
            created_at=sighting.created_at
        ))
    return outs
