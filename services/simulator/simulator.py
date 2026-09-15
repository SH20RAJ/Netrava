"""Deterministic Multi-Camera Stream Simulator for Netrava.

Simulates target vehicle GJ01AB1234 moving sequentially along the SG Highway corridor
in Ahmedabad for evaluation and live hackathon demonstration.
"""

import asyncio
import time
from datetime import datetime
from db.session import AsyncSessionLocal
from models.camera import Camera
from services.ai_pipeline.pipeline import VideoAnalyticsPipeline
import numpy as np


class ScenarioSimulator:
    def __init__(self):
        self.running = False

    async def run_scenario(self, target_plate: str = "GJ01AB1234", interval_sec: int = 5):
        """Sequentially triggers sightings of target vehicle across SG Highway cameras."""
        self.running = True
        print(f"\n[+] Starting Scenario Simulator for Target Vehicle: {target_plate}")
        
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            # Get SG Highway cameras
            cams = (await db.execute(select(Camera).where(Camera.zone == "SG Highway Zone").order_by(Camera.latitude.desc()))).scalars().all()
            if not cams:
                print("[-] No SG Highway cameras found. Please run 'make seed' first.")
                return

        print(f"[+] Found {len(cams)} surveillance cameras along corridor.")

        while self.running:
            for idx, cam in enumerate(cams[:5]):
                print(f"[*] Step {idx+1}/{len(cams[:5])}: Vehicle {target_plate} entering FOV of {cam.name}...")
                pipeline = VideoAnalyticsPipeline(camera_id=cam.id, external_id=cam.external_id)
                dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                dummy_frame[300:600, 400:800] = (200, 200, 200)

                res = await pipeline.process_frame(
                    frame=dummy_frame,
                    latitude=cam.latitude,
                    longitude=cam.longitude,
                    simulated_plate=target_plate
                )
                print(f"    -> Detections: {len(res['detections'])}, Latency: {res['latency_ms']}ms")
                await asyncio.sleep(interval_sec)

            print("[+] Target vehicle completed corridor transit. Looping scenario in 10s...")
            await asyncio.sleep(10)


if __name__ == "__main__":
    sim = ScenarioSimulator()
    asyncio.run(sim.run_scenario())
