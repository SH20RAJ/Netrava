"""Camera Registry and Spatial Service."""

import csv
import io
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.camera import Camera
from schemas.camera import CameraCreate, CameraUpdate, CameraHealthOut, CameraClusterOut


class CameraService:
    @staticmethod
    async def get_cameras(
        db: AsyncSession,
        district: Optional[str] = None,
        status: Optional[str] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Camera]:
        """Queries cameras with optional geospatial bounding box and administrative filters."""
        query = select(Camera)
        conditions = []

        if district:
            conditions.append(Camera.district.ilike(f"%{district}%"))
        if status:
            conditions.append(Camera.status == status.upper())
        if min_lat is not None and max_lat is not None:
            conditions.append(and_(Camera.latitude >= min_lat, Camera.latitude <= max_lat))
        if min_lon is not None and max_lon is not None:
            conditions.append(and_(Camera.longitude >= min_lon, Camera.longitude <= max_lon))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_camera_by_id(db: AsyncSession, camera_id: str) -> Optional[Camera]:
        result = await db.execute(select(Camera).where(Camera.id == camera_id))
        return result.scalars().first()

    @staticmethod
    async def get_camera_by_external_id(db: AsyncSession, external_id: str) -> Optional[Camera]:
        result = await db.execute(select(Camera).where(Camera.external_id == external_id))
        return result.scalars().first()

    @staticmethod
    async def create_camera(db: AsyncSession, camera_in: CameraCreate) -> Camera:
        camera = Camera(**camera_in.model_dump())
        db.add(camera)
        await db.commit()
        await db.refresh(camera)
        return camera

    @staticmethod
    async def update_camera(db: AsyncSession, camera_id: str, camera_in: CameraUpdate) -> Optional[Camera]:
        camera = await CameraService.get_camera_by_id(db, camera_id)
        if not camera:
            return None
        update_data = camera_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera, field, value)
        await db.commit()
        await db.refresh(camera)
        return camera

    @staticmethod
    async def get_camera_health(db: AsyncSession, camera_id: str) -> Optional[CameraHealthOut]:
        camera = await CameraService.get_camera_by_id(db, camera_id)
        if not camera:
            return None
        
        # Real-time health simulation based on status
        is_online = camera.status == "ONLINE"
        return CameraHealthOut(
            camera_id=camera.id,
            external_id=camera.external_id,
            name=camera.name,
            status=camera.status,
            health_score=camera.health_score if is_online else 0.0,
            last_ping_latency_ms=14.2 if is_online else 999.0,
            packet_loss_pct=0.0 if is_online else 100.0,
            fps_measured=24.8 if is_online else 0.0,
            bitrate_kbps=2450.0 if is_online else 0.0,
            last_seen_at=camera.last_seen_at or datetime.utcnow()
        )

    @staticmethod
    async def get_district_clusters(db: AsyncSession) -> List[CameraClusterOut]:
        """Aggregates camera nodes into district centroids for national/statewide overview."""
        query = select(
            Camera.district,
            func.count(Camera.id).label("total"),
            func.avg(Camera.latitude).label("avg_lat"),
            func.avg(Camera.longitude).label("avg_lon")
        ).group_by(Camera.district)
        
        results = (await db.execute(query)).all()
        clusters = []
        for row in results:
            district_name = row[0]
            total = row[1]
            avg_lat = float(row[2])
            avg_lon = float(row[3])
            
            # Count online status
            online_q = select(func.count(Camera.id)).where(
                Camera.district == district_name,
                Camera.status == "ONLINE"
            )
            online_count = (await db.execute(online_q)).scalar() or 0
            
            clusters.append(CameraClusterOut(
                district=district_name,
                total_cameras=total,
                online_cameras=online_count,
                degraded_cameras=0,
                offline_cameras=total - online_count,
                centroid_lat=round(avg_lat, 4),
                centroid_lon=round(avg_lon, 4)
            ))
        return clusters

    @staticmethod
    async def import_cameras_csv(db: AsyncSession, csv_content: str) -> int:
        """Parses CSV formatted camera registry and bulk inserts."""
        reader = csv.DictReader(io.StringIO(csv_content))
        imported = 0
        for row in reader:
            external_id = row.get("external_id")
            if not external_id:
                continue
            existing = await CameraService.get_camera_by_external_id(db, external_id)
            if existing:
                continue
            cam = Camera(
                external_id=external_id,
                name=row.get("name", f"Camera {external_id}"),
                department=row.get("department", "Gujarat Police"),
                district=row.get("district", "Ahmedabad"),
                zone=row.get("zone", "Central Zone"),
                latitude=float(row.get("latitude", 23.0225)),
                longitude=float(row.get("longitude", 72.5714)),
                manufacturer=row.get("manufacturer", "CP Plus"),
                model=row.get("model", "CP-UNC-TA41ZL4"),
                protocol=row.get("protocol", "RTSP"),
                rtsp_url=row.get("rtsp_url", f"rtsp://demo-host:8554/{external_id}"),
                status="ONLINE"
            )
            db.add(cam)
            imported += 1
        await db.commit()
        return imported
