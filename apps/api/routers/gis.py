"""GIS and Geospatial Layer Router."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from models.camera import Camera
from schemas.route import GeoJSONFeatureCollection, GeoJSONFeature
from core.security import get_current_user, User

router = APIRouter(prefix="/gis", tags=["GIS & Spatial"])


@router.get("/cameras", response_model=GeoJSONFeatureCollection)
async def get_cameras_geojson(
    district: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns all cameras as a standard GeoJSON FeatureCollection for MapLibre vector tile rendering."""
    query = select(Camera)
    if district:
        query = query.where(Camera.district.ilike(f"%{district}%"))
    if status:
        query = query.where(Camera.status == status.upper())
        
    cameras = (await db.execute(query)).scalars().all()
    features = []

    for cam in cameras:
        features.append(GeoJSONFeature(
            geometry={
                "type": "Point",
                "coordinates": [float(cam.longitude), float(cam.latitude)]
            },
            properties={
                "id": cam.id,
                "external_id": cam.external_id,
                "name": cam.name,
                "department": cam.department,
                "district": cam.district,
                "zone": cam.zone,
                "status": cam.status,
                "health_score": cam.health_score,
                "camera_type": cam.camera_type,
                "manufacturer": cam.manufacturer,
                "stream_relay_url": cam.stream_relay_url
            }
        ))

    return GeoJSONFeatureCollection(features=features)
