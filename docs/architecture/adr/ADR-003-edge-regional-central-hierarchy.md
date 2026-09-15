# ADR-003: Three-Tier Edge-to-Cloud Distributed Architecture

## Status
Accepted

## Context
Streaming 80,000 live CCTV cameras centrally across Gujarat requires over 200 Gbps of uninterrupted WAN bandwidth—impossible across semi-urban and rural district links and economically disastrous.

## Decision
Netrava institutes a strict three-tier processing hierarchy:
1. **Edge Tier (Police Station / Junction NVR)**: RTSP/ONVIF connection, lightweight motion filtering, 5-frame temporal buffer, health heartbeat.
2. **Regional Tier (34 District Command Hubs)**: MediaMTX stream aggregation, high-throughput GPU inference pool (YOLOv8 + HSRP OCR), 7-day local NVMe video ring buffer, and WAN outage resilience.
3. **Central State Command Tier (Gandhinagar / Cloud)**: Global camera registry, PostGIS spatial queries, watchlists, cross-camera correlation, investigation dossiers, and court-admissible evidence vault.

**Architectural Rule**: Continuous raw video NEVER traverses the statewide WAN. Only lightweight event metadata (2.5 KB) and on-demand alert clips (1 MB) are transmitted centrally, achieving a 99.87% reduction in network load.
