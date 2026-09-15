"""Alert & Watchlist Matching Service."""

import asyncio
from typing import List, Set, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket
from models.alert import Alert
from models.watchlist import WatchlistEntry
from models.camera import Camera
from schemas.alert import AlertOut, AlertCreate


class ConnectionManager:
    """Manages active WebSocket connections for real-time alert broadcasting."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(alert_data)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.active_connections.discard(dead)


ws_manager = ConnectionManager()


class AlertService:
    @staticmethod
    async def match_and_create_alert(
        db: AsyncSession,
        event_id: str,
        camera_id: str,
        normalized_plate: str,
        confidence: float,
        latitude: float,
        longitude: float,
        frame_uri: Optional[str] = None,
        crop_uri: Optional[str] = None
    ) -> Optional[Alert]:
        """Checks if a detected plate matches an active watchlist entry.

        If matched, generates an Alert, persists it, and broadcasts via WebSocket.
        """
        # Query active watchlist entries
        query = select(WatchlistEntry).where(
            WatchlistEntry.identifier == normalized_plate,
            WatchlistEntry.is_active == True
        )
        entry = (await db.execute(query)).scalars().first()
        if not entry:
            return None

        # Check for alert deduplication (suppress duplicate alerts within 5 minutes for same camera/plate)
        dedup_window = datetime.utcnow() - timedelta(minutes=5)
        recent_alert_q = select(Alert).where(
            Alert.camera_id == camera_id,
            Alert.matched_entity == normalized_plate,
            Alert.created_at >= dedup_window
        )
        recent = (await db.execute(recent_alert_q)).scalars().first()
        if recent:
            return recent

        # Fetch camera name
        cam_q = select(Camera).where(Camera.id == camera_id)
        cam = (await db.execute(cam_q)).scalars().first()
        cam_name = cam.name if cam else "Surveillance Camera"
        district = cam.district if cam else "Gujarat"

        title = f"WATCHLIST HIT: {entry.threat_level} — {normalized_plate}"
        desc = (
            f"Vehicle matching watchlist entry ({entry.threat_level}) detected at {cam_name} ({district}). "
            f"Case Reference: {entry.case_reference or 'N/A'}. Confidence: {confidence*100:.1f}%."
        )

        alert = Alert(
            event_id=event_id,
            camera_id=camera_id,
            watchlist_entry_id=entry.id,
            severity=entry.threat_level,
            title=title,
            description=desc,
            matched_entity=normalized_plate,
            match_confidence=confidence,
            latitude=latitude,
            longitude=longitude,
            evidence_frame_uri=frame_uri,
            evidence_crop_uri=crop_uri,
            status="NEW"
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        # Broadcast via WebSocket
        alert_payload = {
            "type": "NEW_ALERT",
            "alert": {
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity,
                "matched_entity": alert.matched_entity,
                "confidence": alert.match_confidence,
                "camera_name": cam_name,
                "district": district,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "timestamp": alert.created_at.isoformat(),
                "frame_uri": alert.evidence_frame_uri,
                "crop_uri": alert.evidence_crop_uri
            }
        }
        asyncio.create_task(ws_manager.broadcast_alert(alert_payload))
        return alert
