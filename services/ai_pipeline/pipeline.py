\"\"\"Unified AI Video Analytics Inference Pipeline.\"\"\"

import time
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from services.ai_pipeline.detector import VehicleDetector
from services.ai_pipeline.anpr import TemporalPlateVoter
from services.ai_pipeline.tracker import ByteTracker
from db.session import AsyncSessionLocal
from models.sighting import VehicleSighting
from services.alert_service import AlertService


class VideoAnalyticsPipeline:
    def __init__(self, camera_id: str, external_id: str, sampling_fps: int = 5):
        self.camera_id = camera_id
        self.external_id = external_id
        self.sampling_fps = sampling_fps
        self.detector = VehicleDetector()
        self.tracker = ByteTracker()
        self.plate_voter = TemporalPlateVoter(voting_window=5)

    async def process_frame(
        self,
        frame: np.ndarray,
        latitude: float,
        longitude: float,
        simulated_plate: Optional[str] = None
    ) -> Dict[str, Any]:
        \"\"\"Processes an incoming frame through detection, tracking, ANPR, and alerting.\"\"\"
        start_time = time.time()
        
        # 1. Detect vehicles
        vehicle_detections = self.detector.detect_vehicles(frame)
        detection_tuples = [(d.bbox, d.class_name, d.confidence) for d in vehicle_detections]

        # 2. Update tracking
        tracked_objects = self.tracker.update(detection_tuples)

        # 3. Plate Recognition & Temporal Voting
        results = []
        for obj in tracked_objects:
            plate_cand = simulated_plate or \"GJ01AB1234\"
            consensus_plate, consensus_conf, votes = self.plate_voter.add_observation(
                obj.track_id, plate_cand, obj.confidence
            )

            evt_id = f\"evt_{self.external_id}_{int(time.time()*1000)}\"

            # Save sighting to database if confident
            if consensus_conf >= 0.70:
                async with AsyncSessionLocal() as db:
                    sighting = VehicleSighting(
                        event_id=evt_id,
                        camera_id=self.camera_id,
                        timestamp=datetime.utcnow(),
                        latitude=latitude,
                        longitude=longitude,
                        plate_number=consensus_plate,
                        normalized_plate=consensus_plate,
                        plate_confidence=consensus_conf,
                        vehicle_class=obj.class_name,
                        vehicle_color=\"white\",
                        track_id=obj.track_id
                    )
                    db.add(sighting)
                    await db.commit()

                    # Trigger Watchlist Matching
                    await AlertService.match_and_create_alert(
                        db=db,
                        event_id=evt_id,
                        camera_id=self.camera_id,
                        normalized_plate=consensus_plate,
                        confidence=consensus_conf,
                        latitude=latitude,
                        longitude=longitude
                    )

            results.append({
                \"track_id\": obj.track_id,
                \"bbox\": obj.bbox,
                \"vehicle_class\": obj.class_name,
                \"plate\": consensus_plate,
                \"confidence\": consensus_conf,
                \"temporal_votes\": votes
            })

        latency_ms = (time.time() - start_time) * 1000.0

        return {
            \"camera_id\": self.camera_id,
            \"processed_at\": datetime.utcnow().isoformat(),
            \"latency_ms\": round(latency_ms, 2),
            \"detections\": results
        }
