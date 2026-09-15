<div align="center">

# 🛡️ NETRAVA
### Open Government Video Intelligence Fabric
**The Open-Source Distributed Video Intelligence & Cross-Camera Investigation Platform**  
*Official Submission & Reference Deployment for Gujarat Police Innovation Challenge 2026 (Sentinel CCTV Challenge)*

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12%2B-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20Async-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js: 14](https://img.shields.io/badge/Frontend-Next.js%2014%20(React%2018)-black.svg)](https://nextjs.org)
[![PostGIS: 16](https://img.shields.io/badge/Spatial%20DB-PostgreSQL%2016%20%2B%20PostGIS-336791.svg)](https://postgis.net)
[![MediaMTX: Streaming](https://img.shields.io/badge/Media%20Relay-MediaMTX%20WebRTC%20%2F%20HLS-orange.svg)](https://github.com/bluenviron/mediamtx)
[![Tests: 12 Passed](https://img.shields.io/badge/Tests-12%2F12%20Passed-brightgreen.svg)](#running-automated-tests)

[**🎥 Watch Demonstration Video (soln.mp4)**](https://github.com/SH20RAJ/Netrava/blob/main/soln.mp4) • [**📐 High-Level Design (hld.md)**](https://github.com/SH20RAJ/Netrava/blob/main/hld.md) • [**🔄 Architecture Diagrams (artitrcture.md)**](https://github.com/SH20RAJ/Netrava/blob/main/artitrcture.md) • [**📈 80,000 Camera Capacity Whitepaper**](https://github.com/SH20RAJ/Netrava/blob/main/docs/scaling/80k_capacity_model.md)

</div>

---

> ### 🏛️ Core Architectural Maxim
> *"Federate what already exists, centralize intelligence where useful, and push processing toward the edge when bandwidth or latency requires it."*

---

## 📑 Table of Contents
1. [The Gujarat Challenge & Problem Statement](#1-the-gujarat-challenge--problem-statement)
2. [Why Netrava Wins: Key Innovations](#2-why-netrava-wins-key-innovations)
3. [System Architecture: Edge-to-Cloud Hybrid Fabric](#3-system-architecture-edge-to-cloud-hybrid-fabric)
4. [The North-Star Hackathon Evaluation Scenario (`GJ01AB1234`)](#4-the-north-star-hackathon-evaluation-scenario-gj01ab1234)
5. [Cross-Camera Multi-Modal Correlation & Kinematics](#5-cross-camera-multi-modal-correlation--kinematics)
6. [Indian HSRP ANPR & 5-Frame Temporal Voting](#6-indian-hsrp-anpr--5-frame-temporal-voting)
7. [80,000-Camera Statewide Capacity Model](#7-80000-camera-statewide-capacity-model)
8. [Chain-of-Custody Cryptographic Evidence (Section 65B)](#8-chain-of-custody-cryptographic-evidence-section-65b)
9. [Quick Start Guide (Ready in 60 Seconds)](#9-quick-start-guide-ready-in-60-seconds)
10. [Automated Verification & Test Suite](#10-automated-verification--test-suite)
11. [Repository & Monorepo Structure](#11-repository--monorepo-structure)
12. [Architecture Decision Records (ADRs)](#12-architecture-decision-records-adrs)
13. [License & Third-Party Notices](#13-license--third-party-notices)

---

## 1. The Gujarat Challenge & Problem Statement

The **Gujarat Police Innovation Challenge 2026** tasks engineers with unifying approximately **80,000 CCTV cameras** operated by **26 disparate government departments** across **34 districts**. 

### The Five Critical Roadblocks:
1. **Hardware & VMS Fragmentation**: Mix of analog DVRs, on-prem NVRs, and proprietary closed VMS platforms (Hikvision, CP Plus, Axis, Dahua, Milestone, Genetec).
2. **The 200 Gbps WAN Bottleneck**: Streaming 80,000 continuous raw video feeds to a central cloud consumes over **200 Gbps** of bandwidth—physically impossible across semi-urban district links and financially unfeasible.
3. **OCR False Positives & Dirty Plates**: Standard ANPR models suffer from optical noise and transient misreadings ('8' vs 'B', '0' vs 'D').
4. **Cloned License Plate Fraud**: Naive systems assume `"same plate = same vehicle"`, allowing criminals with duplicate plates to scramble police investigations.
5. **Lack of Court Provenance**: Exported video footage without cryptographic hashing fails the stringent legal threshold of Section 65B of the Indian Evidence Act.

---

## 2. Why Netrava Wins: Key Innovations

| Capability | Legacy / Conventional VMS | Netrava Video Intelligence Fabric |
| :--- | :--- | :--- |
| **Architectural Model** | Naive centralized raw video streaming (Model 4 only) | **Hybrid Model 1 + 2 + 3 + 4 Edge-to-Cloud Fabric** |
| **WAN Bandwidth Load** | **200 Gbps** (160–320 Gbps uninterrupted) | **336 Mbps** (**99.87% Bandwidth Reduction**) |
| **Camera Interoperability** | Vendor lock-in; requires hardware replacement | **Vendor-neutral `CameraAdapter` interface** (RTSP, ONVIF, VMS Federation) |
| **ANPR Reliability** | Single-frame raw OCR (high error rate on dirty plates) | **Syntax-aware Indian HSRP correction + 5-Frame Temporal Consensus Voting** |
| **Cross-Camera Tracking** | Simplistic string matching (`plate_a == plate_b`) | **Explainable Multi-Modal Scoring** (Plate + Kinematics + Class + Color + Re-ID) |
| **Fraud / Cloned Plates** | Blindly merges conflicting routes | **Kinematic Speed Validator**: Flags $>180$ km/h jumps as **CLONED PLATES** |
| **Legal Admissibility** | Unhashed MP4 downloads | **Deterministic SHA-256 Provenance Hashing** (Sec 65B Indian Evidence Act) |
| **Scale Validation** | Vague claims of scalability | **Mathematical 80,000-Camera Capacity Calculator** with verified hardware sizing |

---

## 3. System Architecture: Edge-to-Cloud Hybrid Fabric

```
                             [ EDGE TIER ]
   (Camera-Adjacent / Edge Gateways / Police Station NVRs)
 +--------------------+  +--------------------+  +--------------------+
 |  Hikvision / Axis  |  | CP Plus / Dahua IP |  | Existing Dept VMS  |
 |  RTSP / ONVIF Cam  |  |  RTSP / ONVIF Cam  |  | (Milestone/Genetec)|
 +---------+----------+  +---------+----------+  +---------+----------+
           |                       |                       |
           v                       v                       v
 +--------------------------------------------------------------------+
 |                 NETRAVA ADAPTER INTERFACE                          |
 |  - RTSPAdapter     - ONVIFAdapter     - VMSFederationAdapter       |
 +---------------------------------+----------------------------------+
                                   |
                                   v
 +--------------------------------------------------------------------+
 |                     NETRAVA EDGE GATEWAY (Local)                   |
 |  - Stream Buffer & Health Ping (5s heartbeat)                      |
 |  - Adaptive Frame Sampler (25 FPS stream -> 5 FPS Analytics)       |
 +---------------------------------+----------------------------------+
                                   |
             [ REGIONAL / DISTRICT TIER (Hubs) ]
 +---------------------------------+----------------------------------+
 |                  NETRAVA REGIONAL PROCESSING HUB                   |
 |  - MediaMTX Stream Relay (WebRTC / Low-Latency HLS)                |
 |  - High-Throughput Worker Pool (GPU YOLOv8 + Indian HSRP OCR)      |
 |  - Temporal Plate Voting & Duplicate Suppression Engine            |
 |  - Local Ring-Buffer Video Cache (NVMe Hot Store, 7-day retention) |
 +---------------------------------+----------------------------------+
                                   | Normalized Events (2.5 KB/evt)
                                   | (99.87% WAN Bandwidth Reduction)
                                   v
             [ CENTRAL STATE COMMAND TIER (Cloud / SDC) ]
 +--------------------------------------------------------------------+
 |              NETRAVA CENTRAL INTELLIGENCE FABRIC                   |
 |                                                                    |
 |  +--------------------+  +------------------+  +----------------+  |
 |  | Central Camera     |  | PostGIS Spatial  |  | Apache Kafka / |  |
 |  | Registry (80k cams)|  | Intelligence DB  |  | Redpanda Bus   |  |
 |  +--------------------+  +------------------+  +----------------+  |
 |                                                                    |
 |  +--------------------+  +------------------+  +----------------+  |
 |  | Cross-Camera Multi-|  | Watchlist Engine |  | Cryptographic  |  |
 |  | Modal Correlation  |  | (VAHAN/CCTNS/Hot)|  | Evidence Vault |  |
 |  +--------------------+  +------------------+  +----------------+  |
 +---------------------------------+----------------------------------+
                                   |
                                   v
 +--------------------------------------------------------------------+
 |            NETRAVA COMMAND & INVESTIGATION WORKSPACE               |
 |  - Tactical Command Center (Live Video Wall, KPI Banner, Alarms)   |
 |  - Spatial GIS Explorer (MapLibre GL, 80k Cluster Layer, Coverage) |
 |  - Vehicle Dossier & Route Reconstructor (Timeline + Kinematics)   |
 |  - Watchlist Manager & Live Alert Dispatcher                       |
 |  - Chain-of-Custody Evidence Viewer & Cryptographic Case Exporter  |
 +------------------------------------+-------------------------------+
```

---

## 4. The North-Star Hackathon Evaluation Scenario (`GJ01AB1234`)

The benchmark evaluation scenario follows stolen target vehicle **`GJ01AB1234`** (White Hyundai Creta, reported under **Vastrapur Police Station FIR No. 142/2026**) traveling sequentially along Ahmedabad's **SG Highway Corridor**:

```
[10:31 AM] Camera 01: SG Hwy - Vaishnodevi Circle North (Lat: 23.1365, Lon: 72.5412)
   │  (Distance: 10.1 km | Elapsed: 13.0 min | Speed: 46.6 km/h)
   ▼
[10:44 AM] Camera 05: SG Hwy - Thaltej Cross Roads East (Lat: 23.0504, Lon: 72.5085)
   │  (Distance: 2.3 km | Elapsed: 18.0 min | Speed: 7.7 km/h - Peak Signal Delay)
   ▼
[11:02 AM] Camera 07: SG Hwy - Iscon Cross Roads Flyover (Lat: 23.0298, Lon: 72.5068)
   │  (Distance: 1.9 km | Elapsed: 19.0 min | Speed: 6.0 km/h)
   ▼
[11:21 AM] Camera 09: SG Hwy - Prahladnagar Junction North (Lat: 23.0135, Lon: 72.5126)
   └─── CRITICAL WATCHLIST HIT DISPATCHED OVER WEBSOCKETS! Intercept Team Deployed.
```

### Measured Trajectory Statistics:
- **Total Corridor Distance**: **14.35 km**
- **Transit Duration**: **50.0 minutes**
- **Average Transit Velocity**: **17.2 km/h** (Typical Ahmedabad peak urban traffic)
- **Watchlist Threat Severity**: **CRITICAL**
- **MapLibre Polyline**: Dynamically rendered with numbered milestone pins and direction vectors.

---

## 5. Cross-Camera Multi-Modal Correlation & Kinematics

Netrava implements an explainable composite scoring algorithm to validate transitions between cameras:

$$\text{MatchScore} = S_{\text{plate}} + S_{\text{kinematic}} + S_{\text{class}} + S_{\text{color}} + S_{\text{visual}}$$

```
MATCH SCORE: 94.0% (VERIFIED SINGLE TRIP)
├── Plate Exact Match:           +60.0 / 60  ("GJ01AB1234" consistent across 4 cameras)
├── Kinematic Velocity Check:    +15.0 / 15  (17.2 km/h average speed is physically plausible)
├── Vehicle Class Consistency:   +10.0 / 10  (Detected as Car / SUV consistently)
├── Dominant Paint Color:        +5.0  / 5   (White vehicle detected across all lighting)
└── Cloned Plate Anomaly Check:  PASS        (No physically impossible transit speeds)
```

### Cloned Plate Fraud Detection
If a vehicle with the same plate appears at an impossible location (e.g. Ahmedabad at 10:31 AM and Vadodara at 10:33 AM), Netrava calculates $v = \frac{110\text{ km}}{2\text{ min}} = 3,300\text{ km/h}$, penalizes the kinematic score by **-35 points**, and issues an immediate **CLONED PLATE FRAUD ALERT** to headquarters.

---

## 6. Indian HSRP ANPR & 5-Frame Temporal Voting

Conforming to India Ministry of Road Transport & Highways (MoRTH) standards:
- **Syntax Validator**: Enforces `^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$`.
- **Character Confusion Rectification**: Position-aware correction (e.g., swapping `O` to `0` in RTO digits; swapping `8` to `B` in series zone).
- **5-Frame Temporal Voting**:
  ```
  Frame t-4: GJ01AB1234 (Conf: 0.94)  -> Match
  Frame t-3: GJ01AB1234 (Conf: 0.96)  -> Match
  Frame t-2: GJ01AB1284 (Conf: 0.61)  -> Transient Optical Noise / Glare
  Frame t-1: GJ01AB1234 (Conf: 0.97)  -> Match
  Frame t-0: GJ01AB1234 (Conf: 0.98)  -> Match
  -------------------------------------------------------------
  CONSENSUS: 4/5 Votes Agree -> Final Plate: GJ01AB1234 (Conf: 98.5%)
  ```

---

## 7. 80,000-Camera Statewide Capacity Model

*Full derivation in [`docs/scaling/80k_capacity_model.md`](docs/scaling/80k_capacity_model.md).*

### 1. Network WAN Bandwidth Sizing
- **Naive Central Streaming**:
  $$\text{BW}_{\text{naive}} = 80,000 \times 2.5\text{ Mbps} = \mathbf{200\text{ Gbps}}$$
- **Netrava Edge-to-Cloud Fabric**:
  - Event Metadata Rate: $80,000 \times 0.2\text{ evts/sec} \times 2.5\text{ KB} \times 8 = 320\text{ Mbps}$.
  - Alert Evidence Clips (on-demand): $16\text{ Mbps}$.
  - **Total Central WAN Load**: $\mathbf{336\text{ Mbps}}$ ($\mathbf{99.87\%}$ reduction!).

### 2. GPU Inference Sizing (District Hubs)
- Total State Inferences: $80,000 \times 5\text{ FPS} = 400,000\text{ inferences/sec}$.
- Across 34 District Hubs: $2,352\text{ cameras} \times 5\text{ FPS} = 11,765\text{ inferences/sec/district}$.
- Using NVIDIA L4 (TensorRT INT8 batch-8 throughput $\approx 350\text{ FPS}$):
  $$\text{GPUs per District Hub} = \frac{11,765}{350} \approx \mathbf{34\text{ GPUs (e.g. 4 enterprise 2U servers with 8x L4 each)}}$$
- **Statewide Total**: $1,156\text{ GPUs}$.

### 3. Tiered Storage Architecture
- **Tier 1 (Hot - District NVMe Ring Buffer)**: 7 days continuous cyclic video storage per camera = $434\text{ TB}$ per district ($14.75\text{ PB}$ distributed statewide).
- **Tier 2 (Warm - State Data Center MinIO S3)**: Tamper-evident evidence clips and metadata for 1 year = $\approx 80\text{ TB}$.
- **Tier 3 (Cold - Archive / Tape)**: Statutory criminal evidence preserved for 7 years.

---

## 8. Chain-of-Custody Cryptographic Evidence (Section 65B)

To satisfy the statutory evidentiary requirements of **Section 65B of the Indian Evidence Act**:
1. Every sighting frame crop and video clip computes an immutable **SHA-256 cryptographic integrity hash** at the instant of capture.
2. The hash, camera hardware ID, GPS location, model version, and UTC timestamp are stored in an append-only relational ledger.
3. Every operator query and export action records an immutable entry in the audit log (`who, what, when, query, IP, purpose`).

---

## 9. Quick Start Guide (Ready in 60 Seconds)

### Prerequisites
- Python 3.11+ (recommended: managed with `uv`)
- Node.js 20+ & `pnpm`
- FFmpeg 6.0+

### Setup & Launch
```bash
# 1. Clone repository
git clone https://github.com/SH20RAJ/Netrava.git
cd Netrava

# 2. Setup Python environment and install dependencies
make setup

# 3. Seed Gujarat Reference Infrastructure (52 Cameras, Watchlists & Target GJ01AB1234)
make seed

# 4. Start Central API Gateway & Command Center Web Console
make dev-api   # in Terminal 1 (FastAPI on port 8000)
make dev-web   # in Terminal 2 (Next.js on port 3000)
```

### URLs to Access
- **Tactical Command Center**: [http://localhost:3000](http://localhost:3000)
- **Target Vehicle Investigation**: [http://localhost:3000/vehicles/GJ01AB1234](http://localhost:3000/vehicles/GJ01AB1234)
- **CCTV Registry (52 Cameras)**: [http://localhost:3000/cameras](http://localhost:3000/cameras)
- **Tactical Video Matrix**: [http://localhost:3000/live](http://localhost:3000/live)
- **Interactive 80k Scalability Calculator**: [http://localhost:3000/system](http://localhost:3000/system)
- **FastAPI OpenAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 10. Automated Verification & Test Suite

Run the full automated test suite (100% pass rate):
```bash
make test
```

### Test Coverage Summary:
- `tests/integration/test_api_integration.py`:
  - `test_root_endpoint`: Verifies platform metadata and version.
  - `test_cameras_list`: Validates 52 cameras seeded across Gujarat districts.
  - `test_vehicle_dossier_target_plate`: Verifies target plate `GJ01AB1234` dossier, sightings, and CRITICAL threat flag.
  - `test_vehicle_route_reconstruction`: Validates 4-point chronological route, GeoJSON polyline, and velocity kinematics.
  - `test_scalability_calculator_api`: Verifies 80,000 camera capacity model formulas and 99.87% WAN reduction.
- `tests/unit/test_plate_parser.py`:
  - `test_normalize_valid_gujarat_plate`: Validates Indian HSRP regex conformance.
  - `test_rectify_character_confusion_numeric_zone`: Validates `O->0` and `B->8` position-aware substitutions.
  - `test_temporal_voting_consensus`: Validates 5-frame temporal voting eliminating single-frame optical glare.
- `tests/unit/test_correlation_engine.py`:
  - `test_haversine_distance`: Verifies great-circle spatial distance math.
  - `test_plausible_highway_transit`: Validates highway transit kinematics ($46.6\text{ km/h}$).
  - `test_cloned_plate_detection_impossible_speed`: Validates cloned plate anomaly detection ($3,600\text{ km/h}$).
- `tests/unit/test_scalability_calculator.py`:
  - `test_80k_camera_sizing_equations`: Validates GPU inference, bandwidth, and storage equations.

---

## 11. Repository & Monorepo Structure

```
/Users/shaswatraj/Desktop/hackathons/netrava/
├── apps/
│   ├── web/                     # Next.js 14/15 Tactical Command Center UI
│   │   ├── src/app/             # App router (/dashboard, /cameras, /live, /vehicles/[plate], /system, /alerts)
│   │   └── src/components/      # MapLibre vector canvas, Navigation, Video Wall
│   └── api/                     # Central FastAPI application gateway
│       ├── core/                # Config, JWT/RBAC security, audit logging
│       ├── db/                  # SQLAlchemy 2.0 async engine & session
│       ├── models/              # Camera, Watchlist, VehicleSighting, Alert, Investigation, AuditLog
│       ├── schemas/             # Pydantic v2 validation contracts
│       ├── routers/             # cameras, vehicles, watchlists, alerts, investigations, evidence, gis, system
│       └── services/            # Correlation engine, Route reconstructor, Camera manager, Alert broadcaster
├── services/
│   ├── ai_pipeline/             # YOLOv8 detector, Indian HSRP OCR, 5-frame temporal voter, ByteTracker
│   ├── stream-gateway/          # MediaMTX configuration and RTSP relay
│   └── simulator/               # Deterministic multi-camera SG Highway scenario generator
├── db/
│   └── schemas/init.sql         # PostGIS 16 spatial schema with GIST indexes and enum types
├── docs/
│   ├── architecture/            # System architecture and ADRs (ADR-001 to ADR-005)
│   ├── scaling/                 # 80k_capacity_model.md mathematical whitepaper
│   └── hackathon/               # demo_script.md 2-3 minute presentation guide
├── infra/
│   ├── compose/                 # docker-compose.yml (PostGIS, Redis, MinIO, MediaMTX)
│   └── kubernetes/              # Production Kubernetes StatefulSets, Deployments, and HPA
├── scripts/
│   ├── seed_db.py               # Seeds 52 Gujarat cameras, watchlists, and target vehicle GJ01AB1234
│   └── render_demo_video.py     # Renders 1080p official demonstration video (soln.mp4)
├── tests/                       # Unit and integration pytest test suite (12/12 passing)
├── hld.md                       # Comprehensive High-Level Design document
├── artitrcture.md               # Workflow and integration architecture diagrams
├── soln.mp4                     # Official demonstration video
├── Makefile                     # Root automation script
├── THIRD_PARTY_NOTICES.md       # Open-source licenses audit
├── LICENSE                      # Apache License 2.0
└── README.md                    # Master documentation
```

---

## 12. Architecture Decision Records (ADRs)

- [**ADR-001**](docs/architecture/adr/ADR-001-postgresql-postgis.md): Selection of PostgreSQL + PostGIS as Spatial System of Record.
- [**ADR-002**](docs/architecture/adr/ADR-002-event-bus-and-cloudevents.md): Universal Event Schema using CNCF CloudEvents 1.0.
- [**ADR-003**](docs/architecture/adr/ADR-003-edge-regional-central-hierarchy.md): Three-Tier Edge-to-Cloud Distributed Architecture.
- [**ADR-004**](docs/architecture/adr/ADR-004-camera-adapter-federation.md): Camera Adapter Federation Pattern (Model 3).
- [**ADR-005**](docs/architecture/adr/ADR-005-multi-modal-cross-camera-correlation.md): Multi-Modal Cross-Camera Correlation & Kinematics.

---

## 13. License & Third-Party Notices

Netrava is open-source software licensed under the **Apache License 2.0**, permitting unrestricted government deployment, private-sector integration, and research extension. See [LICENSE](LICENSE).

Complete third-party notices, model attributions, and open-source licenses are detailed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
