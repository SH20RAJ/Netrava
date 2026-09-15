# Netrava: Official 2-3 Minute Hackathon Demonstration Script
## Gujarat Police Innovation Challenge 2026 / Sentinel CCTV Challenge

---

### SCENE 1: The Statewide Problem & CCTV Registry (0:00 - 0:25)
- **Visual**: Open `http://localhost:3000` — Command Center Map showing 52 camera nodes across Gujarat with real-time KPI ribbon.
- **Narrator**:
  > "Gujarat currently operates over 80,000 CCTV cameras across 26 distinct government departments. But today, they exist in vendor silos—Hikvision, CP Plus, Axis, legacy DVRs, and proprietary VMSs.
  > Welcome to **NETRAVA** — the Open Government Video Intelligence Fabric.
  > Instead of replacing existing infrastructure, Netrava establishes a vendor-neutral Model 1 GIS Registry and federates heterogeneous feeds using lightweight Model 3 adapters."

---

### SCENE 2: Heterogeneous Streaming & Video Wall (0:25 - 0:50)
- **Visual**: Navigate to `/live` — show 4-tile video wall displaying RTSP/WebRTC feeds from Vaishnodevi, Thaltej, Iscon, and Prahladnagar with real-time AI bounding box overlays.
- **Narrator**:
  > "Through our MediaMTX edge relay, heterogeneous RTSP and ONVIF streams are normalized into sub-second WebRTC feeds.
  > Notice our AI pipeline operating in real time: YOLOv8 vehicle detection coupled with High Security Registration Plate (HSRP) Indian OCR and 5-frame temporal voting to eliminate character misreadings."

---

### SCENE 3: Real-Time Watchlist Hit & Alert Dispatch (0:50 - 1:15)
- **Visual**: Switch to `/alerts` or observe top right alert drawer: a flashing red `CRITICAL WATCHLIST HIT: GJ01AB1234 (Stolen Vehicle - FIR 142/2026)`.
- **Narrator**:
  > "Watch what happens when a vehicle of interest enters the surveillance fabric.
  > Target plate `GJ01AB1234`—a white Hyundai Creta reported stolen under Vastrapur Police Station FIR 142/2026—is detected at Prahladnagar Junction.
  > Instantly, a sub-second alert is broadcast over WebSockets to every control room operator statewide."

---

### SCENE 4: The North-Star Investigation & Route Reconstruction (1:15 - 1:55)
- **Visual**: Click "Inspect Vehicle Route" to open `/vehicles/GJ01AB1234`.
- **Narrator**:
  > "With one click, an investigator accesses the complete cross-camera dossier.
  > Netrava doesn't just match strings. It reconstructs the entire spatial trajectory polyline on MapLibre:
  > - 10:31 AM: Vaishnodevi Circle
  > - 10:44 AM: Thaltej Cross Roads
  > - 11:02 AM: Iscon Flyover
  > - 11:21 AM: Prahladnagar Junction
  > Covering 14.3 kilometers over 50 minutes at an average speed of 17.2 km/h.
  > Look at our explainable correlation card: Netrava validates the kinematic transit velocity, vehicle class, and color consistency, confirming with 94% confidence that this is a single continuous transit and NOT a cloned plate."

---

### SCENE 5: Cryptographic Chain-of-Custody & Evidence Export (1:55 - 2:15)
- **Visual**: Scroll to the Chronological Evidence ladder. Click on evidence frame to view SHA-256 hash. Click "Export Case Report".
- **Narrator**:
  > "Every single observation is anchored by a cryptographic SHA-256 integrity hash, guaranteeing court-admissible provenance under Section 65B of the Indian Evidence Act.
  > The investigator can immediately export an official case report or pin all waypoints to formal Crime Branch dossier `CID-CR-2026-0418`."

---

### SCENE 6: Sizing to 80,000 Cameras & Conclusion (2:15 - 2:45)
- **Visual**: Open `/system` — show interactive 80,000 camera calculator with sliders adjusting FPS and bandwidth.
- **Narrator**:
  > "How does this scale to 80,000 cameras?
  > By strictly following our architectural maxim:
  > *Federate what already exists, centralize intelligence where useful, and push processing toward the edge.*
  > Raw video stays at local district NVRs. Only 2.5 KB metadata events transmit centrally, slashing statewide WAN bandwidth from 200 Gbps down to 336 Mbps—a 99.87% reduction.
  > One intelligence fabric.
  > Many camera vendors.
  > Many government systems.
  > One operational view.
  > This is NETRAVA for Gujarat Police."
