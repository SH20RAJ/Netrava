"""Cameras API Router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.camera import CameraOut, CameraCreate, CameraUpdate, CameraHealthOut, CameraClusterOut
from services.camera_service import CameraService
from core.security import get_current_user, require_roles, User
from models.audit import AuditLog

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("", response_model=List[CameraOut])
async def list_cameras(
    district: Optional[str] = None,
    status: Optional[str] = None,
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves registered cameras with optional spatial and administrative filters."""
    return await CameraService.get_cameras(
        db=db,
        district=district,
        status=status,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        skip=skip,
        limit=limit
    )


@router.post("", response_model=CameraOut, status_code=status.HTTP_201_CREATED)
async def register_camera(
    camera_in: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN", "DISTRICT_ADMIN"]))
):
    """Registers a new CCTV camera into the statewide registry."""
    existing = await CameraService.get_camera_by_external_id(db, camera_in.external_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Camera with external_id '{camera_in.external_id}' already registered."
        )
    camera = await CameraService.create_camera(db, camera_in)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        ip_address="127.0.0.1",
        action="REGISTER_CAMERA",
        entity_type="CAMERA",
        entity_id=camera.id,
        details={"external_id": camera.external_id, "district": camera.district}
    )
    db.add(audit)
    await db.commit()
    return camera


@router.get("/clusters", response_model=List[CameraClusterOut])
async def get_district_clusters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns aggregated camera nodes grouped by Gujarat district for GIS map clustering."""
    return await CameraService.get_district_clusters(db)


@router.get("/{camera_id}", response_model=CameraOut)
async def get_camera_details(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches full camera profile, stream configurations, and operational parameters."""
    camera = await CameraService.get_camera_by_id(db, camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.patch("/{camera_id}", response_model=CameraOut)
async def update_camera(
    camera_id: str,
    camera_in: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN", "DISTRICT_ADMIN"]))
):
    """Updates camera metadata, operational status, or analytics toggles."""
    camera = await CameraService.update_camera(db, camera_id, camera_in)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.get("/{camera_id}/health", response_model=CameraHealthOut)
async def get_camera_health(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves real-time stream telemetry, measured FPS, packet loss, and ping latency."""
    health = await CameraService.get_camera_health(db, camera_id)
    if not health:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return health


@router.post("/import", status_code=status.HTTP_200_OK)
async def import_cameras_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPER_ADMIN", "STATE_ADMIN"]))
):
    """Bulk imports cameras from CSV file into the central registry."""
    contents = (await file.read()).decode("utf-8")
    count = await CameraService.import_cameras_csv(db, contents)
    return {"status": "success", "imported_count": count}
