# NETRAVA: Integration & Workflow Architecture
## Edge-to-Cloud Video Intelligence Fabric
**Reference Repository Document**: `https://github.com/SH20RAJ/Netrava/blob/main/architecture.md`

---

## 1. End-to-End System Workflow Architecture

```mermaid
flowchart TD
    subgraph EdgeTier["EDGE TIER (Camera-Adjacent & Police Stations)"]
        Cam1["Heterogeneous IP Cameras\n(Hikvision, Axis, CP Plus, Dahua)"]
        Cam2["Analog DVRs / Existing Dept NVRs"]
        Adapter["CameraAdapter Interface\n(RTSP / ONVIF / VMS Federation)"]
        EdgeGW["Netrava Edge Gateway\n(Stream Buffer, Health Pings, 5 FPS Sampler)"]
        Cam1 --> Adapter
        Cam2 --> Adapter
        Adapter --> EdgeGW
    end

    subgraph RegionalTier["REGIONAL TIER (34 District Command Hubs)"]
        MediaMTX["MediaMTX Media Server\n(WebRTC & Low-Latency HLS Remux)"]
        AIPool["GPU Inference Worker Pool\n(YOLOv8 + Indian HSRP OCR)"]
        Voter["5-Frame Temporal Voting\n& Duplicate Suppression"]
        LocalCache["7-Day Local NVMe\nVideo Ring Buffer (434 TB/hub)"]
        
        EdgeGW --> MediaMTX
        MediaMTX --> AIPool
        AIPool --> Voter
        MediaMTX -. Continuous 25 FPS .-> LocalCache
    end

    subgraph CentralTier["CENTRAL TIER (Gandhinagar Cloud / State Data Center)"]
        EventBus["CloudEvents Event Bus\n(Apache Kafka / Redpanda Partitioned Log)"]
        Registry["Central Camera Registry\n(PostGIS 16 Spatial Engine)"]
        Correlation["Multi-Modal Correlation Engine\n(Plate + Kinematics + Class + Color)"]
        WatchlistEngine["Watchlist & Alert Engine\n(CCTNS, VAHAN, FIR Hotlists)"]
        EvidenceVault["Cryptographic Evidence Vault\n(MinIO S3 + SHA-256 Provenance)"]
        AuditLog["Immutable Security Audit Log\n(RBAC & Access Tracking)"]
        
        Voter -- "2.5 KB CloudEvent (No Raw Video!)" --> EventBus
        EventBus --> Registry
        EventBus --> Correlation
        EventBus --> WatchlistEngine
        EventBus --> EvidenceVault
    end

    subgraph CommandWorkspace["COMMAND CENTER & INVESTIGATION WORKSPACE"]
        Dashboard["Tactical Command Dashboard\n(KPI Banner & Real-time Alerts)"]
        GISMap["Interactive MapLibre GL GIS\n(80k Cluster Layer & Trajectory Polylines)"]
        VideoWall["Tactical Video Matrix\n(Sub-Second WebRTC Video Feeds)"]
        Investigator["Vehicle Investigation Workspace\n(/vehicles/GJ01AB1234)"]
        
        WatchlistEngine -- "WebSocket Alert Push" --> Dashboard
        Correlation --> Investigator
        Registry --> GISMap
        MediaMTX -- "WebRTC Stream Relay" --> VideoWall
        Investigator --> AuditLog
    end
```

---

## 2. Camera Adapter Federation Workflow (Model 3)

The `CameraAdapter` abstraction isolates the analytics pipeline from proprietary video protocol differences:

```mermaid
sequenceDiagram
    autonumber
    participant Core as Netrava Registry
    participant Adapter as CameraAdapter Interface
    participant Camera as Physical Camera / NVR
    participant MTX as MediaMTX Streaming Relay

    Core->>Adapter: initialize(camera_config)
    Adapter->>Camera: connect(RTSP / ONVIF credentials)
    alt Connection Success
        Camera-->>Adapter: RTSP SDP Handshake OK
        Adapter->>MTX: publishStream(source_url, stream_path)
        MTX-->>Core: stream_ready (WebRTC / HLS endpoints active)
        Core->>Core: updateStatus("ONLINE", health_score=100)
    else Timeout / Authentication Failure
        Camera--xAdapter: 401 Unauthorized / Network Timeout
        Adapter-->>Core: error(StreamUnavailable)
        Core->>Core: updateStatus("OFFLINE", health_score=0)
    end
```

---

## 3. Computer Vision & ANPR Temporal Voting Pipeline

```mermaid
flowchart LR
    Frame["Input Video Frame\n(1920x1080 @ 5 FPS)"] --> Det["YOLOv8 Vehicle Detector\n(Cars, SUVs, Trucks, Buses)"]
    Det --> Track["ByteTrack Object Tracker\n(Persistent Track ID trk_1042)"]
    Track --> PlateROI["License Plate Localization\n(BBox Crop: 420, 630, 540, 675)"]
    PlateROI --> OCR["Indian HSRP OCR Parser\n(MoRTH Syntax Validation)"]
    OCR --> Rectify["Syntax-Aware Character Rectification\n(O->0, D->0, B->8)"]
    Rectify --> Voter["Temporal Consensus Voter\n(5-Frame Window)"]
    Voter --> Sighting["Consensus Plate: GJ01AB1234\nConfidence: 96.4%\nVotes: 5/5"]
```

---

## 4. Multi-Modal Cross-Camera Correlation & Kinematics

Netrava evaluates transitions between surveillance points to prevent false matches and catch cloned plates:

```mermaid
flowchart TD
    SightingA["Sighting A (Cam 01: Vaishnodevi Circle)\nTimestamp: 10:31 AM | Lat: 23.1365, Lon: 72.5412\nPlate: GJ01AB1234 | Class: SUV | Color: White"]
    SightingB["Sighting B (Cam 05: Thaltej Cross Roads)\nTimestamp: 10:44 AM | Lat: 23.0504, Lon: 72.5085\nPlate: GJ01AB1234 | Class: SUV | Color: White"]

    SightingA & SightingB --> Score["Correlation Scoring Engine"]
    
    Score --> S1["1. Plate Levenshtein Match: 60.0 / 60"]
    Score --> S2["2. Haversine Distance: 10.1 km\nElapsed Time: 13.0 min\nVelocity: 46.6 km/h (Plausible: +15.0 / 15)"]
    Score --> S3["3. Vehicle Class Match (SUV): +10.0 / 10"]
    Score --> S4["4. Color Match (White): +5.0 / 5"]

    S1 & S2 & S3 & S4 --> Composite["Composite Match Score: 94.0%\nVerified Single Continuous Transit"]
    Composite --> Route["Add Node to MapLibre Reconstructed Route Polyline"]

    subgraph ClonedPlateBranch["Fraudulent Cloned Plate Scenario"]
        SightingC["Sighting C (Cam 40: Vadodara)\nTimestamp: 10:33 AM (2 mins later, 110 km away)\nImplied Velocity: 3300 km/h"]
        SightingA & SightingC --> Anomaly["Kinematic Speed Anomaly Validator"]
        Anomaly --> Fraud["ALERT: Physically Impossible Velocity!\nFlagged as Potential CLONED PLATE\nScore: -35.0"]
    end
```

---

## 5. Government Multi-Agency Integration Architecture

```mermaid
flowchart TD
    subgraph ExternalGovDBs["Government External Databases"]
        CCTNS["Police CCTNS\n(FIRs, Stolen Vehicles, Missing Persons)"]
        VAHAN["MoRTH VAHAN\n(National Vehicle Registration Registry)"]
        SARTHI["MoRTH SARTHI\n(Driving License & Identity Records)"]
        NAFIS["AFIS / NAFIS\n(National Automated Fingerprint System)"]
        ERSS["Emergency Response 112 / ERSS\n(Dispatch & Intercept Command)"]
    end

    subgraph NetravaHub["NETRAVA Integration Gateway"]
        SyncMgr["Government DB Synchronization Manager"]
        WatchlistCore["Netrava Watchlist Engine"]
        AlertDispatcher["WebSocket Alert Dispatcher"]
    end

    CCTNS -- "Stolen Vehicle FIR 142/2026" --> SyncMgr
    VAHAN -- "Owner & Registration Lookup" --> SyncMgr
    SyncMgr --> WatchlistCore
    WatchlistCore -- "Real-Time Watchlist Hit" --> AlertDispatcher
    AlertDispatcher -- "Automated CAD Incident Creation" --> ERSS
```
