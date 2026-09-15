"""Alerts API Router & WebSocket Dispatcher."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.alert import Alert
from models.camera import Camera
from schemas.alert import AlertOut, AlertUpdate, AlertStatsOut
from services.alert_service import ws_manager
from core.security import get_current_user, User

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertOut])
async def list_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists real-time surveillance alerts with severity and status filters."""
    query = (
        select(Alert, Camera.name, Camera.district)
        .outerjoin(Camera, Alert.camera_id == Camera.id)
        .order_by(Alert.created_at.desc())
    )
    if severity:
        query = query.where(Alert.severity == severity.upper())
    if status:
        query = query.where(Alert.status == status.upper())
    query = query.limit(limit)

    results = (await db.execute(query)).all()
    outs = []
    for alert, cam_name, district in results:
        out = AlertOut(
            id=alert.id,
            event_id=alert.event_id,
            camera_id=alert.camera_id,
            camera_name=cam_name,
            district=district,
            watchlist_entry_id=alert.watchlist_entry_id,
            severity=alert.severity,
            title=alert.title,
            description=alert.description,
            matched_entity=alert.matched_entity,
            match_confidence=alert.match_confidence,
            latitude=alert.latitude,
            longitude=alert.longitude,
            evidence_frame_uri=alert.evidence_frame_uri,
            evidence_crop_uri=alert.evidence_crop_uri,
            status=alert.status,
            assigned_to=alert.assigned_to,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at,
            notes=alert.notes,
            created_at=alert.created_at
        )
        outs.append(out)
    return outs


@router.get("/stats", response_model=AlertStatsOut)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculates active alert statistics and severity distribution for the command dashboard."""
    query = select(Alert.severity, func.count(Alert.id)).where(Alert.status.in_(["NEW", "ACKNOWLEDGED"])).group_by(Alert.severity)
    results = (await db.execute(query)).all()
    
    breakdown = {sev: 0 for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]}
    total_active = 0
    for sev, count in results:
        if sev in breakdown:
            breakdown[sev] = count
            total_active += count

    ack_q = select(func.count(Alert.id)).where(Alert.status == "ACKNOWLEDGED")
    acknowledged_count = (await db.execute(ack_q)).scalar() or 0

    return AlertStatsOut(
        total_active=total_active,
        critical_count=breakdown["CRITICAL"],
        high_count=breakdown["HIGH"],
        medium_count=breakdown["MEDIUM"],
        low_count=breakdown["LOW"],
        acknowledged_count=acknowledged_count,
        severity_breakdown=breakdown
    )


@router.patch("/{alert_id}", response_model=AlertOut)
async def update_alert_status(
    alert_id: str,
    update_in: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledges, escalates, or resolves a surveillance alert."""
    alert = (await db.execute(select(Alert).where(Alert.id == alert_id))).scalars().first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    if update_in.status:
        alert.status = update_in.status.upper()
        if alert.status == "ACKNOWLEDGED" and not alert.acknowledged_at:
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = current_user.full_name
    if update_in.assigned_to:
        alert.assigned_to = update_in.assigned_to
    if update_in.notes:
        alert.notes = update_in.notes

    await db.commit()
    await db.refresh(alert)

    cam = (await db.execute(select(Camera).where(Camera.id == alert.camera_id))).scalars().first()
    return AlertOut(
        id=alert.id,
        event_id=alert.event_id,
        camera_id=alert.camera_id,
        camera_name=cam.name if cam else None,
        district=cam.district if cam else None,
        watchlist_entry_id=alert.watchlist_entry_id,
        severity=alert.severity,
        title=alert.title,
        description=alert.description,
        matched_entity=alert.matched_entity,
        match_confidence=alert.match_confidence,
        latitude=alert.latitude,
        longitude=alert.longitude,
        evidence_frame_uri=alert.evidence_frame_uri,
        evidence_crop_uri=alert.evidence_crop_uri,
        status=alert.status,
        assigned_to=alert.assigned_to,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        notes=alert.notes,
        created_at=alert.created_at
    )
