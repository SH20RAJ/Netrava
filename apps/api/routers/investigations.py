"""Investigations and Case Dossier API Router."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.investigation import Investigation, InvestigationEvent
from models.sighting import VehicleSighting
from models.camera import Camera
from schemas.investigation import InvestigationOut, InvestigationCreate, InvestigationUpdate, InvestigationEventOut
from schemas.vehicle import SightingOut
from core.security import get_current_user, require_roles, User
from models.audit import AuditLog

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=List[InvestigationOut])
async def list_investigations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists formal investigation dossiers."""
    result = await db.execute(select(Investigation).order_by(Investigation.created_at.desc()))
    cases = result.scalars().all()
    
    outs = []
    for case in cases:
        outs.append(InvestigationOut(
            id=case.id,
            case_number=case.case_number,
            title=case.title,
            lead_investigator=case.lead_investigator,
            department=case.department,
            target_plate=case.target_plate,
            status=case.status,
            summary=case.summary,
            created_at=case.created_at,
            updated_at=case.updated_at,
            events=[]
        ))
    return outs


@router.post("", response_model=InvestigationOut, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    case_in: InvestigationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN", "INVESTIGATOR"]))
):
    """Opens a new investigation case dossier and logs the audit event."""
    existing = (await db.execute(select(Investigation).where(Investigation.case_number == case_in.case_number))).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Case number already exists")

    case = Investigation(**case_in.model_dump())
    db.add(case)
    await db.commit()
    await db.refresh(case)

    # Audit
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        ip_address="127.0.0.1",
        action="CREATE_INVESTIGATION",
        entity_type="DOSSIER",
        entity_id=case.id,
        details={"case_number": case.case_number, "target_plate": case.target_plate}
    )
    db.add(audit)
    await db.commit()

    return InvestigationOut(
        id=case.id,
        case_number=case.case_number,
        title=case.title,
        lead_investigator=case.lead_investigator,
        department=case.department,
        target_plate=case.target_plate,
        status=case.status,
        summary=case.summary,
        created_at=case.created_at,
        updated_at=case.updated_at,
        events=[]
    )


@router.get("/{investigation_id}", response_model=InvestigationOut)
async def get_investigation_details(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves full case dossier including pinned sighting events and evidence."""
    case = (await db.execute(select(Investigation).where(Investigation.id == investigation_id))).scalars().first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation dossier not found")

    events_q = (
        select(InvestigationEvent, VehicleSighting, Camera)
        .join(VehicleSighting, InvestigationEvent.sighting_id == VehicleSighting.id)
        .join(Camera, VehicleSighting.camera_id == Camera.id)
        .where(InvestigationEvent.investigation_id == investigation_id)
        .order_by(VehicleSighting.timestamp.asc())
    )
    event_results = (await db.execute(events_q)).all()

    events_out = []
    for inv_evt, sighting, cam in event_results:
        sighting_out = SightingOut(
            id=sighting.id,
            event_id=sighting.event_id,
            camera_id=sighting.camera_id,
            camera_name=cam.name,
            district=cam.district,
            zone=cam.zone,
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
        )
        events_out.append(InvestigationEventOut(
            sighting_id=sighting.id,
            relevance_notes=inv_evt.relevance_notes,
            added_at=inv_evt.added_at,
            sighting=sighting_out
        ))

    return InvestigationOut(
        id=case.id,
        case_number=case.case_number,
        title=case.title,
        lead_investigator=case.lead_investigator,
        department=case.department,
        target_plate=case.target_plate,
        status=case.status,
        summary=case.summary,
        created_at=case.created_at,
        updated_at=case.updated_at,
        events=events_out
    )


@router.post("/{investigation_id}/pin/{sighting_id}", status_code=status.HTTP_200_OK)
async def pin_sighting_to_investigation(
    investigation_id: str,
    sighting_id: str,
    relevance_notes: str = "Verified route waypoint",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN", "INVESTIGATOR"]))
):
    """Pins a vehicle sighting to the case dossier for court evidence submission."""
    inv = (await db.execute(select(Investigation).where(Investigation.id == investigation_id))).scalars().first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")

    sighting = (await db.execute(select(VehicleSighting).where(VehicleSighting.id == sighting_id))).scalars().first()
    if not sighting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sighting not found")

    link = InvestigationEvent(
        investigation_id=investigation_id,
        sighting_id=sighting_id,
        relevance_notes=relevance_notes
    )
    db.add(link)
    await db.commit()
    return {"status": "success", "message": f"Sighting {sighting_id} pinned to case {inv.case_number}"}
