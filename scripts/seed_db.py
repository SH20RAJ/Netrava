"""Database Seeder for Gujarat Police Innovation Challenge 2026 Reference Dataset."""

import asyncio
import os
import hashlib
import numpy as np
import cv2
from datetime import datetime, timedelta
from db.session import AsyncSessionLocal, init_db
from models.camera import Camera
from models.watchlist import Watchlist, WatchlistEntry
from models.sighting import VehicleSighting
from models.alert import Alert
from models.investigation import Investigation, InvestigationEvent
from models.audit import AuditLog
from core.config import settings


def generate_synthetic_evidence_image(plate_text: str, camera_name: str, timestamp: datetime) -> str:
    """Creates a synthetic surveillance frame with vehicle and Indian license plate overlay."""
    os.makedirs(settings.EVIDENCE_LOCAL_STORAGE_DIR, exist_ok=True)
    filename = f"frame_{plate_text}_{int(timestamp.timestamp())}.jpg"
    filepath = os.path.join(settings.EVIDENCE_LOCAL_STORAGE_DIR, filename)

    if not os.path.exists(filepath):
        # Create 1280x720 dark asphalt roadway scene
        img = np.zeros((720, 1280, 3), dtype=np.uint8)
        img[:] = (35, 40, 45)  # Dark road background

        # Lane markings
        cv2.line(img, (200, 720), (500, 300), (200, 200, 200), 4)
        cv2.line(img, (1080, 720), (780, 300), (200, 200, 200), 4)
        cv2.line(img, (640, 720), (640, 300), (255, 255, 0), 3)

        # Vehicle bounding box (White SUV/Sedan)
        cv2.rectangle(img, (460, 340), (820, 620), (220, 220, 225), -1)
        cv2.rectangle(img, (455, 335), (825, 625), (10, 185, 245), 3)  # AI Detection Bounding Box

        # Windshield
        cv2.rectangle(img, (500, 360), (780, 440), (60, 70, 80), -1)

        # Indian License Plate (HSRP White Plate with Black Text)
        cv2.rectangle(img, (560, 530), (720, 580), (255, 255, 255), -1)
        cv2.rectangle(img, (560, 530), (720, 580), (0, 0, 0), 2)
        # Blue IND stripe
        cv2.rectangle(img, (560, 530), (575, 580), (180, 80, 20), -1)
        # Plate Text
        cv2.putText(img, plate_text, (585, 565), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Camera OSD (On-Screen Display)
        osd_text = f"{camera_name} | {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')} | NETRAVA AI v1.0"
        cv2.putText(img, osd_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, f"DETECTED: [CAR] Conf: 0.96 | PLATE: {plate_text} (0.95)", (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10, 185, 245), 2)

        cv2.imwrite(filepath, img)

    return f"/static/evidence/{filename}"


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


async def seed_data():
    await init_db()
    async with AsyncSessionLocal() as db:
        print("[*] Checking existing records...")
        from sqlalchemy import select
        res = await db.execute(select(Camera))
        if res.scalars().first():
            print("[+] Database already populated. Skipping seed.")
            return

        print("[+] Seeding 52 Gujarat Surveillance Cameras...")

        # 52 Gujarat Cameras across Ahmedabad, Gandhinagar, Surat, Vadodara, and Rajkot
        cameras_data = [
            # Ahmedabad - SG Highway Corridor (Critical Target Vehicle Route)
            ("IN-GJ-AHM-0001", "SG Hwy - Vaishnodevi Circle North", "Ahmedabad", "SG Highway Zone", 23.1365, 72.5412, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-AHM-0002", "SG Hwy - Nirma University Junction", "Ahmedabad", "SG Highway Zone", 23.1250, 72.5380, "Axis", "Q1656-LE"),
            ("IN-GJ-AHM-0003", "SG Hwy - Gota Flyover Entry", "Ahmedabad", "SG Highway Zone", 23.1025, 72.5310, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-AHM-0004", "SG Hwy - Sola Civil Cross Roads", "Ahmedabad", "SG Highway Zone", 23.0780, 72.5210, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-AHM-0005", "SG Hwy - Thaltej Cross Roads East", "Ahmedabad", "SG Highway Zone", 23.0504, 72.5085, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-AHM-0006", "SG Hwy - Gurudwara Junction", "Ahmedabad", "SG Highway Zone", 23.0410, 72.5075, "Axis", "Q1656-LE"),
            ("IN-GJ-AHM-0007", "SG Hwy - Iscon Cross Roads Flyover", "Ahmedabad", "SG Highway Zone", 23.0298, 72.5068, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-AHM-0008", "SG Hwy - Karnavati Club Junction", "Ahmedabad", "SG Highway Zone", 23.0210, 72.5090, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-AHM-0009", "SG Hwy - Prahladnagar Junction North", "Ahmedabad", "SG Highway Zone", 23.0135, 72.5126, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-AHM-0010", "SG Hwy - Makarba Cross Roads", "Ahmedabad", "SG Highway Zone", 22.9980, 72.5040, "Axis", "Q1656-LE"),
            ("IN-GJ-AHM-0011", "SG Hwy - Sanathal Circle South", "Ahmedabad", "SG Highway Zone", 22.9750, 72.4920, "CP Plus", "CP-UNC-TA41ZL4"),
            
            # Ahmedabad - SP Ring Road & Central City
            ("IN-GJ-AHM-0012", "SP Ring Rd - Bopal Cross Roads", "Ahmedabad", "West Zone", 23.0340, 72.4650, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-AHM-0013", "SP Ring Rd - Shilaj Circle", "Ahmedabad", "West Zone", 23.0590, 72.4780, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-AHM-0014", "SP Ring Rd - Science City Cross Roads", "Ahmedabad", "West Zone", 23.0820, 72.4980, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-AHM-0015", "Ashram Rd - Income Tax Cross Roads", "Ahmedabad", "Central Zone", 23.0425, 72.5690, "Axis", "Q1656-LE"),
            ("IN-GJ-AHM-0016", "Ashram Rd - Paldi Cross Roads", "Ahmedabad", "Central Zone", 23.0150, 72.5650, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-AHM-0017", "Drive-In Rd - Helmet Circle", "Ahmedabad", "West Zone", 23.0480, 72.5320, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-AHM-0018", "Drive-In Rd - Himalaya Mall Junction", "Ahmedabad", "West Zone", 23.0515, 72.5250, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-AHM-0019", "C.G. Road - Panchvati Circle", "Ahmedabad", "Central Zone", 23.0230, 72.5560, "Axis", "Q1656-LE"),
            ("IN-GJ-AHM-0020", "C.G. Road - Swastik Cross Roads", "Ahmedabad", "Central Zone", 23.0360, 72.5580, "Hikvision", "DS-2CD2T87G2-L"),

            # Gandhinagar (State Capital Surveillance)
            ("IN-GJ-GND-0021", "Koba Circle North Entry", "Gandhinagar", "Koba Zone", 23.1650, 72.6320, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-GND-0022", "Infocity Gate 1 Junction", "Gandhinagar", "Infocity Zone", 23.1890, 72.6280, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-GND-0023", "CHH Road - Sector 11 Circle", "Gandhinagar", "Central Sector", 23.2180, 72.6510, "Axis", "Q1656-LE"),
            ("IN-GJ-GND-0024", "Mahatma Mandir Main Entrance", "Gandhinagar", "Central Sector", 23.2290, 72.6450, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-GND-0025", "Vidhan Sabha Gate 4", "Gandhinagar", "Security Zone", 23.2240, 72.6590, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-GND-0026", "Sector 7 Police Bhavan Perimeter", "Gandhinagar", "HQ Zone", 23.2120, 72.6640, "Axis", "Q1656-LE"),
            ("IN-GJ-GND-0027", "Sector 21 Vegetable Market Circle", "Gandhinagar", "Residential Zone", 23.2380, 72.6610, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-GND-0028", "GIFT City - Bridge Entry East", "Gandhinagar", "GIFT City Zone", 23.1620, 72.6840, "Dahua", "IPC-HFW5842E-ZE"),

            # Surat (South Gujarat Command Center)
            ("IN-GJ-SRT-0029", "Athwa Gate Police Chawk", "Surat", "Athwa Zone", 21.1850, 72.8120, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-SRT-0030", "Ring Road - Majura Gate Cross Roads", "Surat", "Ring Road Zone", 21.1760, 72.8210, "Axis", "Q1656-LE"),
            ("IN-GJ-SRT-0031", "Ring Road - Textile Market Junction", "Surat", "Commercial Zone", 21.1920, 72.8450, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-SRT-0032", "Varachha Main Rd - Poddar Arcade", "Surat", "Varachha Zone", 21.2150, 72.8620, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-SRT-0033", "Varachha - Mini Bazar Circle", "Surat", "Varachha Zone", 21.2220, 72.8710, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-SRT-0034", "Dumas Rd - VR Mall Cross Roads", "Surat", "Airport Corridor", 21.1450, 72.7680, "Axis", "Q1656-LE"),
            ("IN-GJ-SRT-0035", "Surat Airport Terminal Entry", "Surat", "Airport Corridor", 21.1140, 72.7420, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-SRT-0036", "Adajan - Anand Mahal Rd Junction", "Surat", "Rander Zone", 21.1980, 72.7950, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-SRT-0037", "Katargam - Gajera Circle", "Surat", "Katargam Zone", 21.2380, 72.8340, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-SRT-0038", "Udhna - Teen Rasta Cross Roads", "Surat", "Industrial Zone", 21.1520, 72.8420, "Axis", "Q1656-LE"),

            # Vadodara (Central Gujarat Hub)
            ("IN-GJ-BRD-0039", "Alkapuri - RC Dutt Rd Circle", "Vadodara", "Alkapuri Zone", 22.3110, 73.1780, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-BRD-0040", "Fatehgunj - Narhari Hospital Cross Rd", "Vadodara", "Fatehgunj Zone", 22.3250, 73.1890, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-BRD-0041", "Sayajigunj - Railway Station Circle", "Vadodara", "Station Zone", 22.3080, 73.1850, "Axis", "Q1656-LE"),
            ("IN-GJ-BRD-0042", "Akota - Dandia Bazar Bridge West", "Vadodara", "Akota Zone", 22.2960, 73.1750, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-BRD-0043", "Old Padra Rd - Bird Circle", "Vadodara", "West Zone", 22.2980, 73.1550, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-BRD-0044", "Karelibaug - Water Tank Cross Roads", "Vadodara", "East Zone", 22.3320, 73.2080, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-BRD-0045", "NH-48 Golden Chokdi Intersection", "Vadodara", "Highway Zone", 22.3550, 73.2450, "Axis", "Q1656-LE"),
            ("IN-GJ-BRD-0046", "Makarpura - GIDC Main Gate", "Vadodara", "Industrial Zone", 22.2450, 73.1950, "Dahua", "IPC-HFW5842E-ZE"),

            # Rajkot (Saurashtra Command Hub)
            ("IN-GJ-RJK-0047", "Kalawad Road - KKV Hall Circle", "Rajkot", "West Zone", 22.2850, 70.7680, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-RJK-0048", "Yagnik Road - Jilla Panchayat Chowk", "Rajkot", "Central Zone", 22.2980, 70.7980, "CP Plus", "CP-UNC-TA41ZL4"),
            ("IN-GJ-RJK-0049", "Trikon Baug Traffic Intersection", "Rajkot", "Central Zone", 22.3020, 70.8040, "Axis", "Q1656-LE"),
            ("IN-GJ-RJK-0050", "150 Feet Ring Road - Indira Circle", "Rajkot", "Ring Road Zone", 22.2910, 70.7550, "Dahua", "IPC-HFW5842E-ZE"),
            ("IN-GJ-RJK-0051", "150 Feet Ring Road - Madhapar Chowk", "Rajkot", "Ring Road Zone", 22.3250, 70.7650, "Hikvision", "DS-2CD2T87G2-L"),
            ("IN-GJ-RJK-0052", "Greenland Chowkadi - NH-27 Bypass", "Rajkot", "Highway Zone", 22.3120, 70.8450, "Axis", "Q1656-LE")
        ]

        camera_objects = {}
        for ext_id, name, district, zone, lat, lon, mfr, model in cameras_data:
            cam = Camera(
                external_id=ext_id,
                name=name,
                department="Gujarat Police",
                district=district,
                zone=zone,
                latitude=lat,
                longitude=lon,
                manufacturer=mfr,
                model=model,
                protocol="RTSP",
                rtsp_url=f"rtsp://demo-stream-gw:8554/{ext_id.lower().replace('-', '_')}",
                stream_relay_url=f"http://localhost:8888/{ext_id.lower().replace('-', '_')}/index.m3u8",
                status="ONLINE",
                health_score=98.5
            )
            db.add(cam)
            camera_objects[ext_id] = cam

        await db.commit()
        for cam in camera_objects.values():
            await db.refresh(cam)

        print(f"[+] Successfully saved {len(camera_objects)} cameras.")

        # 2. Seed Watchlists
        print("[+] Seeding Operational Watchlists...")
        wl_stolen = Watchlist(
            name="Statewide Stolen Vehicle Hotlist (Crime Branch / CCTNS)",
            category="STOLEN_VEHICLE",
            description="Active priority alert list for reported stolen vehicles under investigation across Gujarat districts.",
            department="Gujarat Police CID Crime",
            created_by="Inspector General of Police (Crime)"
        )
        wl_narcotics = Watchlist(
            name="Organized Crime & Transit Interdiction List",
            category="WANTED_VEHICLE",
            description="Vehicles flagged for surveillance regarding inter-district illicit contraband movement.",
            department="Anti-Terrorist Squad (ATS) / CID",
            created_by="Superintendent of Police"
        )
        db.add(wl_stolen)
        db.add(wl_narcotics)
        await db.commit()
        await db.refresh(wl_stolen)
        await db.refresh(wl_narcotics)

        # Target vehicle entries:
        # GJ01AB1234: The North-Star Hackathon Designated Target Vehicle!
        entry_target = WatchlistEntry(
            watchlist_id=wl_stolen.id,
            entity_type="vehicle",
            identifier="GJ01AB1234",
            secondary_identifier="White Hyundai Creta (2023)",
            threat_level="CRITICAL",
            case_reference="FIR No. 142/2026 Vastrapur PS (Section 379 IPC)",
            notes="Vehicle stolen from Vastrapur commercial complex; suspect flagged traveling south along SG Highway corridor."
        )
        entry_secondary = WatchlistEntry(
            watchlist_id=wl_narcotics.id,
            entity_type="vehicle",
            identifier="GJ05CD5678",
            secondary_identifier="Black Mahindra Scorpio",
            threat_level="HIGH",
            case_reference="Surat Crime Branch Case #88/2026",
            notes="Flagged for surveillance on NH-48 Surat-Vadodara corridor."
        )
        db.add(entry_target)
        db.add(entry_secondary)
        await db.commit()
        await db.refresh(entry_target)

        # 3. Seed Target Vehicle Transit Sightings for GJ01AB1234
        # Simulates the realistic 50-minute movement along the SG Highway Corridor:
        # 10:31 -> Vaishnodevi Circle (Cam 01)
        # 10:44 -> Thaltej Cross Roads (Cam 05)
        # 11:02 -> Iscon Flyover (Cam 07)
        # 11:21 -> Prahladnagar Junction (Cam 09)
        print("[+] Seeding Realistic Multi-Camera Sighting Timeline for GJ01AB1234...")

        now = datetime.utcnow()
        # Set timeline base to today at 10:31 AM
        base_time = now.replace(hour=10, minute=31, second=0, microsecond=0)

        transit_steps = [
            ("IN-GJ-AHM-0001", base_time, 0.945, "car", "white", "trk_v101"),
            ("IN-GJ-AHM-0005", base_time + timedelta(minutes=13), 0.962, "car", "white", "trk_v105"),
            ("IN-GJ-AHM-0007", base_time + timedelta(minutes=31), 0.978, "car", "white", "trk_v107"),
            ("IN-GJ-AHM-0009", base_time + timedelta(minutes=50), 0.985, "car", "white", "trk_v109"),
        ]

        sightings = []
        for ext_id, sighting_time, conf, v_class, color, trk in transit_steps:
            cam = camera_objects[ext_id]
            evt_id = f"evt_{cam.external_id}_{int(sighting_time.timestamp())}"
            
            # Generate synthetic frame with plate overlay
            frame_url = generate_synthetic_evidence_image("GJ01AB1234", cam.name, sighting_time)
            frame_path = os.path.join(settings.EVIDENCE_LOCAL_STORAGE_DIR, os.path.basename(frame_url))
            evidence_hash = compute_sha256(frame_path) if os.path.exists(frame_path) else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

            sighting = VehicleSighting(
                event_id=evt_id,
                camera_id=cam.id,
                timestamp=sighting_time,
                latitude=cam.latitude,
                longitude=cam.longitude,
                plate_number="GJ01AB1234",
                normalized_plate="GJ01AB1234",
                plate_confidence=conf,
                vehicle_class=v_class,
                vehicle_color=color,
                track_id=trk,
                frame_uri=frame_url,
                plate_crop_uri=frame_url,
                evidence_hash=evidence_hash
            )
            db.add(sighting)
            sightings.append(sighting)

        await db.commit()
        for s in sightings:
            await db.refresh(s)

        # 4. Generate Alert for Sighting at Prahladnagar Junction (Most Recent Sighting)
        last_sighting = sightings[-1]
        last_cam = camera_objects["IN-GJ-AHM-0009"]

        alert = Alert(
            event_id=last_sighting.event_id,
            camera_id=last_cam.id,
            watchlist_entry_id=entry_target.id,
            severity="CRITICAL",
            title="CRITICAL WATCHLIST HIT: GJ01AB1234 (Stolen Vehicle)",
            description="Target vehicle (White Hyundai Creta) matching Statewide Hotlist detected at Prahladnagar Junction North. Intercept team notified.",
            matched_entity="GJ01AB1234",
            match_confidence=0.985,
            latitude=last_cam.latitude,
            longitude=last_cam.longitude,
            evidence_frame_uri=last_sighting.frame_uri,
            evidence_crop_uri=last_sighting.plate_crop_uri,
            status="NEW"
        )
        db.add(alert)

        # 5. Create Formal Investigation Dossier
        inv = Investigation(
            case_number="CID-CR-2026-0418",
            title="S.G. Highway Vehicle Theft & Interception Operation",
            lead_investigator="DySP Vikram Patel",
            department="Gujarat Police CID Crime",
            target_plate="GJ01AB1234",
            status="IN_PROGRESS",
            summary="Rapid cross-camera tracking of stolen vehicle GJ01AB1234 along SG Highway from Vaishnodevi Circle toward Prahladnagar Junction."
        )
        db.add(inv)
        await db.commit()
        await db.refresh(inv)

        # Pin the route sightings to the investigation
        for s in sightings:
            inv_event = InvestigationEvent(
                investigation_id=inv.id,
                sighting_id=s.id,
                relevance_notes=f"Confirmed waypoint along SG Highway corridor at {s.timestamp.strftime('%H:%M:%S')}"
            )
            db.add(inv_event)

        # 6. Seed Security Audit Log
        audit = AuditLog(
            user_id="usr_01_patel",
            user_name="DySP Vikram Patel",
            user_role="INVESTIGATOR",
            ip_address="10.24.18.91",
            action="INITIALIZE_DOSSIER",
            entity_type="DOSSIER",
            entity_id=inv.id,
            details={"case_number": inv.case_number, "target_plate": inv.target_plate}
        )
        db.add(audit)
        await db.commit()

        print("[+] Reference database seeding complete!")
        print(f"    - Cameras: {len(cameras_data)}")
        print(f"    - Watchlists: 2")
        print(f"    - Target Vehicle: GJ01AB1234 (4 chronological sightings)")
        print(f"    - Active Critical Alerts: 1")
        print(f"    - Active Investigation: {inv.case_number}")


if __name__ == "__main__":
    asyncio.run(seed_data())
