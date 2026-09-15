"""Vehicle Intelligence & Route Reconstruction Router."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.camera import Camera
from models.sighting import VehicleSighting
from models.watchlist import WatchlistEntry
from models.audit import AuditLog
from schemas.vehicle import VehicleDossierOut, SightingOut
from schemas.route import RouteReconstructionOut
from services.route_reconstructor import RouteReconstructor
from core.security import get_current_user, User

router = APIRouter(prefix="/vehicles", tags=["Vehicle Intelligence"])


@router.get("/{plate}", response_model=VehicleDossierOut)
async def get_vehicle_dossier(
    plate: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves comprehensive vehicle intelligence profile, sighting history summary, and watchlist risk status."""
    normalized_plate = plate.upper().replace(" ", "").replace("-", "")

    # Audit query
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        ip_address="127.0.0.1",
        action="SEARCH_VEHICLE",
        entity_type="VEHICLE",
        entity_id=normalized_plate,
        details={"query_plate": plate}
    )
    db.add(audit)
    await db.commit()

    # Query sightings
    sightings_q = (
        select(VehicleSighting, Camera)
        .join(Camera, VehicleSighting.camera_id == Camera.id)
        .where(VehicleSighting.normalized_plate == normalized_plate)
        .order_by(VehicleSighting.timestamp.asc())
    )
    results = (await db.execute(sightings_q)).all()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sightings recorded for vehicle plate: {normalized_plate}"
        )

    first_sighting, _ = results[0]
    last_sighting, last_camera = results[-1]
    total_sightings = len(results)
    
    unique_cams = len(set(s.camera_id for s, _ in results))
    districts = list(set(c.district for _, c in results))

    # Check Watchlist
    wl_q = select(WatchlistEntry).where(
        WatchlistEntry.identifier == normalized_plate,
        WatchlistEntry.is_active == True
    )
    wl_entry = (await db.execute(wl_q)).scalars().first()

    watchlist_flagged = bool(wl_entry)
    risk_score = 95.0 if (wl_entry and wl_entry.threat_level == "CRITICAL") else (80.0 if wl_entry else 20.0)
    risk_level = wl_entry.threat_level if wl_entry else "LOW"

    latest_out = SightingOut(
        id=last_sighting.id,
        event_id=last_sighting.event_id,
        camera_id=last_sighting.camera_id,
        camera_name=last_camera.name,
        district=last_camera.district,
        zone=last_camera.zone,
        timestamp=last_sighting.timestamp,
        latitude=last_sighting.latitude,
        longitude=last_sighting.longitude,
        plate_number=last_sighting.plate_number,
        normalized_plate=last_sighting.normalized_plate,
        plate_confidence=last_sighting.plate_confidence,
        vehicle_class=last_sighting.vehicle_class or "car",
        vehicle_color=last_sighting.vehicle_color or "white",
        track_id=last_sighting.track_id,
        frame_uri=last_sighting.frame_uri,
        plate_crop_uri=last_sighting.plate_crop_uri,
        evidence_hash=last_sighting.evidence_hash,
        created_at=last_sighting.created_at
    )

    wl_details = None
    if wl_entry:
        wl_details = {
            "threat_level": wl_entry.threat_level,
            "case_reference": wl_entry.case_reference,
            "notes": wl_entry.notes
        }

    return VehicleDossierOut(
        normalized_plate=normalized_plate,
        raw_plate_sample=first_sighting.plate_number,
        vehicle_class=last_sighting.vehicle_class or "car",
        dominant_color=last_sighting.vehicle_color or "white",
        first_seen=first_sighting.timestamp,
        last_seen=last_sighting.timestamp,
        total_sightings=total_sightings,
        cameras_visited_count=unique_cams,
        districts_visited=districts,
        watchlist_flagged=watchlist_flagged,
        watchlist_details=wl_details,
        latest_sighting=latest_out,
        risk_score=risk_score,
        risk_level=risk_level
    )


@router.get("/{plate}/route", response_model=RouteReconstructionOut)
async def reconstruct_vehicle_route(
    plate: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reconstructs the full chronological route, GeoJSON polyline, and kinematic speed analysis for the target vehicle."""
    route = await RouteReconstructor.reconstruct_route(plate, db)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to reconstruct route: No surveillance points recorded for {plate}"
        )
    return route
