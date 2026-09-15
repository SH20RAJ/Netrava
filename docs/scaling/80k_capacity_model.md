# Netrava: Sizing & Capacity Architecture for 80,000 Cameras
## Engineering Whitepaper & Mathematical Model
**Target Deployment**: Gujarat Police Innovation Challenge 2026 / Sentinel CCTV Network  
**Jurisdiction**: 34 Districts, 26 Government Departments, 80,000 CCTV Endpoints

---

## 1. The Scaling Challenge

Statewide public-safety networks cannot simply stream all video feeds to a central cloud:
- **Raw Stream Bandwidth**: $80,000 \text{ cameras} \times 2.5 \text{ Mbps} = \mathbf{200 \text{ Gbps}}$.
- **Monthly WAN Transit Cost**: Multi-crore INR recurring recurring cost, vulnerable to regional link severance.
- **Inference Compute**: Continuous 25 FPS inference across 80,000 cameras = $2,000,000$ frames/sec (economically unviable).

---

## 2. Netrava's Hierarchical Solution

```
80,000 Edge Cameras
     ↓ (RTSP / ONVIF @ 25 FPS)
34 District Command Hubs (Regional Processing)
  - 2,352 cameras / district
  - Sampled to 5 FPS for analytics (11,760 inferences/sec/district)
  - 34x NVIDIA L4 GPUs per district (4 enterprise 2U servers)
  - 7-Day Local NVMe Ring Buffer (440 TB / district)
     ↓ (Lightweight CloudEvents: 2.5 KB/event @ 0.2 evts/sec/cam)
Central State Intelligence Fabric (Gandhinagar Cloud / SDC)
  - Aggregate Bandwidth: ~256 Mbps (99.87% WAN Reduction!)
  - PostGIS Central Registry, Watchlists & Cross-Camera Correlation
```

---

## 3. Mathematical Equations & Sizing Calculations

### 3.1 Network Bandwidth Sizing
$$\text{Central WAN Bandwidth} = \left( N_{\text{cams}} \times f_{\text{event}} \times S_{\text{metadata}} \right) + \text{Bandwidth}_{\text{clips}}$$
$$\text{Metadata Load} = 80,000 \times 0.2 \text{ events/sec} \times 2.5 \text{ KB} \times 8 = 320 \text{ Mbps}$$
$$\text{Alert Clips Load} = 10 \text{ active alerts/sec} \times 1 \text{ MB clip} / 5 \text{ sec} = 16 \text{ Mbps}$$
$$\mathbf{\text{Total Netrava Central Bandwidth} \approx 336 \text{ Mbps (vs 200,000 Mbps Naive)}}$$

### 3.2 Compute & GPU Inference Requirements
$$\text{District Inference Load} = \frac{80,000}{34} \times 5 \text{ FPS} = 11,765 \text{ inferences/sec/district}$$
Using NVIDIA L4 (24GB VRAM) with TensorRT INT8 batch-8 inference:
$$\text{Throughput per L4 GPU} \approx 350 \text{ FPS (YOLOv8m + HSRP OCR)}$$
$$\text{GPUs per District Hub} = \frac{11,765}{350} \approx \mathbf{34 \text{ GPUs (e.g., 4 servers with 8x L4 each)}}$$
$$\mathbf{\text{Total Statewide GPUs Across 34 Districts} = 1,156 \text{ GPUs}}$$

### 3.3 Tiered Storage Architecture
1. **Tier 1 (Hot - District NVMe/SAS RAID-6)**:
   - 7 days continuous cyclic video retention per camera:
     $$\text{Storage per Camera/Day} = \frac{2.5 \text{ Mbps} \times 86,400}{8 \times 1,024 \times 1,024} = 0.02636 \text{ TB}$$
     $$\text{District 7-Day Buffer} = 2,352 \times 0.02636 \times 7 = \mathbf{434 \text{ TB / District Hub}}$$
     $$\text{Statewide Hot Buffer} = 434 \text{ TB} \times 34 = \mathbf{14.75 \text{ Petabytes (Distributed)}}$$
2. **Tier 2 (Warm - SDC MinIO / S3 Object Store)**:
   - Metadata, plates, and alert evidence clips retained for 1 year: $\approx \mathbf{80 \text{ Terabytes}}$.
3. **Tier 3 (Cold - Statutory Compliance Archive)**:
   - Certified criminal evidence retained for 7 years under court mandate.
