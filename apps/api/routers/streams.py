"""Media Streams and Relay Router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.camera import Camera
from models.audit import AuditLog
from core.config import settings
from core.security import get_current_user, User

router = APIRouter(prefix="/streams", tags=["Media Streams"])


@router.get("/{camera_id}/live")
async def get_live_stream_endpoint(
    camera_id: str,
    protocol: str = "webrtc",  # webrtc, hls, rtsp
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates low-latency WebRTC or HLS stream access URLs proxied through MediaMTX."""
    camera = (await db.execute(select(Camera).where(Camera.id == camera_id))).scalars().first()
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    # Record stream viewing in audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        ip_address="127.0.0.1",
        action="VIEW_LIVE_FEED",
        entity_type="CAMERA",
        entity_id=camera.id,
        details={"protocol": protocol, "camera_name": camera.name}
    )
    db.add(audit)
    await db.commit()

    stream_path = camera.external_id.lower().replace("-", "_")
    
    return {
        "camera_id": camera.id,
        "external_id": camera.external_id,
        "name": camera.name,
        "status": camera.status,
        "endpoints": {
            "webrtc": f"http://{settings.MEDIAMTX_WEBRTC_HOST}/{stream_path}",
            "hls": f"http://{settings.MEDIAMTX_HLS_HOST}/{stream_path}/index.m3u8",
            "rtsp": f"rtsp://{settings.MEDIAMTX_RTSP_HOST}/{stream_path}",
            "mjpeg_proxy": f"/api/v1/streams/{camera_id}/preview"
        }
    }
