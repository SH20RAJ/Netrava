"""Vehicle Route Reconstruction Service."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.camera import Camera
from models.sighting import VehicleSighting
from models.watchlist import WatchlistEntry
from schemas.route import RouteReconstructionOut, RouteWaypoint, KinematicAssessment, GeoJSONFeatureCollection, GeoJSONFeature
from services.correlation_engine import CorrelationEngine, haversine_distance_km


class RouteReconstructor:
    @staticmethod
    async def reconstruct_route(plate: str, db: AsyncSession) -> Optional[RouteReconstructionOut]:
        """Reconstructs chronological transit path, GeoJSON polyline, and kinematics for a target license plate."""
        normalized_plate = plate.upper().replace(" ", "").replace("-", "")
        
        # 1. Fetch sightings ordered chronologically
        query = (
            select(VehicleSighting, Camera)
            .join(Camera, VehicleSighting.camera_id == Camera.id)
            .where(VehicleSighting.normalized_plate == normalized_plate)
            .order_by(VehicleSighting.timestamp.asc())
        )
        results = (await db.execute(query)).all()
        if not results:
            return None

        # 2. Check Watchlist status
        wl_query = select(WatchlistEntry).where(
            WatchlistEntry.identifier == normalized_plate,
            WatchlistEntry.is_active == True
        )
        wl_hit = (await db.execute(wl_query)).scalars().first()

        waypoints: List[RouteWaypoint] = []
        coordinates: List[List[float]] = []
        total_distance = 0.0
        confidences: List[float] = []

        prev_lat: Optional[float] = None
        prev_lon: Optional[float] = None
        prev_time: Optional[datetime] = None

        for idx, (sighting, camera) in enumerate(results):
            confidences.append(float(sighting.plate_confidence))
            coordinates.append([float(camera.longitude), float(camera.latitude)])
            
            kinematic_eval = None
            if prev_lat is not None and prev_lon is not None and prev_time is not None:
                step_dist = haversine_distance_km(prev_lat, prev_lon, camera.latitude, camera.longitude)
                total_distance += step_dist
                eval_res = CorrelationEngine.evaluate_sighting_transition(
                    prev_lat, prev_lon, prev_time,
                    camera.latitude, camera.longitude, sighting.timestamp,
                    sighting.plate_number, sighting.plate_number,
                    sighting.vehicle_class or "car", sighting.vehicle_class or "car",
                    sighting.vehicle_color or "white", sighting.vehicle_color or "white"
                )
                kinematic_eval = KinematicAssessment(
                    is_plausible=eval_res["is_plausible"],
                    implied_speed_kmh=eval_res["implied_speed_kmh"],
                    distance_traveled_km=eval_res["distance_km"],
                    transit_duration_minutes=eval_res["transit_minutes"],
                    assessment_narrative="; ".join(eval_res["reasons"]),
                    anomaly_detected=eval_res["anomaly_detected"],
                    anomaly_type=eval_res["anomaly_type"]
                )

            prev_lat = camera.latitude
            prev_lon = camera.longitude
            prev_time = sighting.timestamp

            waypoints.append(RouteWaypoint(
                step_number=idx + 1,
                sighting_id=sighting.id,
                camera_id=camera.id,
                camera_name=camera.name,
                district=camera.district,
                zone=camera.zone,
                latitude=camera.latitude,
                longitude=camera.longitude,
                timestamp=sighting.timestamp,
                plate_confidence=sighting.plate_confidence,
                vehicle_class=sighting.vehicle_class or "car",
                vehicle_color=sighting.vehicle_color or "white",
                frame_uri=sighting.frame_uri,
                plate_crop_uri=sighting.plate_crop_uri,
                evidence_hash=sighting.evidence_hash,
                kinematic_from_prev=kinematic_eval
            ))

        start_time = waypoints[0].timestamp
        end_time = waypoints[-1].timestamp
        duration_minutes = max(0.1, (end_time - start_time).total_seconds() / 60.0)
        duration_hours = duration_minutes / 60.0
        avg_speed = total_distance / duration_hours if duration_hours > 0 else 0.0
        overall_conf = sum(confidences) / len(confidences) if confidences else 0.0

        # Build GeoJSON FeatureCollection
        features = [
            # The line string connecting all waypoints
            GeoJSONFeature(
                geometry={
                    "type": "LineString",
                    "coordinates": coordinates
                },
                properties={
                    "plate": normalized_plate,
                    "total_distance_km": round(total_distance, 2),
                    "total_duration_minutes": round(duration_minutes, 1),
                    "color": "#F59E0B" if wl_hit else "#06B6D4"
                }
            )
        ]

        # Add point features for each waypoint
        for wp in waypoints:
            features.append(GeoJSONFeature(
                geometry={
                    "type": "Point",
                    "coordinates": [wp.longitude, wp.latitude]
                },
                properties={
                    "step_number": wp.step_number,
                    "camera_name": wp.camera_name,
                    "district": wp.district,
                    "timestamp": wp.timestamp.isoformat(),
                    "confidence": wp.plate_confidence,
                    "vehicle_class": wp.vehicle_class
                }
            ))

        geojson_coll = GeoJSONFeatureCollection(features=features)

        summary_narrative = (
            f"Vehicle {normalized_plate} detected across {len(waypoints)} surveillance points "
            f"covering {total_distance:.1f} km over {duration_minutes:.1f} minutes. "
            f"Average transit velocity: {avg_speed:.1f} km/h."
        )

        return RouteReconstructionOut(
            normalized_plate=normalized_plate,
            total_waypoints=len(waypoints),
            start_time=start_time,
            end_time=end_time,
            total_distance_km=round(total_distance, 2),
            total_duration_minutes=round(duration_minutes, 1),
            average_speed_kmh=round(avg_speed, 1),
            waypoints=waypoints,
            geojson_polyline=geojson_coll,
            overall_confidence=round(overall_conf, 3),
            is_watchlist_hit=bool(wl_hit),
            watchlist_severity=wl_hit.threat_level if wl_hit else None,
            kinematic_summary=summary_narrative
        )
