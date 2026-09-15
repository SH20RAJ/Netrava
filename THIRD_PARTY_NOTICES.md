# Netrava — Third-Party Notices & Open-Source Attribution

This document contains open-source software notices, licenses, and attributions for third-party components, frameworks, models, and libraries incorporated into or utilized by **NETRAVA**.

Netrava adheres to an open-architecture, vendor-neutral philosophy and selects dependencies based on:
1. Permissive licensing (MIT, Apache 2.0, BSD-3-Clause) suitable for government, private, and public-sector deployments.
2. Isolation of copyleft libraries behind standard protocol and process boundaries.
3. Production security posture and active community maintenance.

---

## 1. Core Frameworks & Infrastructure

### MediaMTX (formerly rtsp-simple-server)
- **Project**: MediaMTX (Zero-dependency RTSP/RTMP/WebRTC/HLS Media Server)
- **License**: MIT License
- **Copyright**: (c) 2019-2024 Alessandro Vergani (bluenviron)
- **Source**: https://github.com/bluenviron/mediamtx
- **Usage**: Deployed as an independent process / container for normalizing heterogeneous camera RTSP streams into WebRTC and Low-Latency HLS.

### FFmpeg
- **Project**: FFmpeg Multimedia Framework
- **License**: LGPL v2.1+ / GPL v2+ (depending on build flags)
- **Copyright**: (c) 2000-2025 the FFmpeg developers
- **Source**: https://ffmpeg.org
- **Usage**: Executed via standard sub-process boundaries for segment clipping, transcode proxying, and synthetic feed test generation.

### PostgreSQL & PostGIS
- **Project**: PostgreSQL Database Management System
- **License**: PostgreSQL License (permissive BSD-style)
- **Copyright**: (c) 1996-2024 The PostgreSQL Global Development Group
- **Source**: https://www.postgresql.org
- **Project**: PostGIS Spatial Database Extension
- **License**: GNU GPL v2 (Database engine level, client access via standard wire protocol SQL)
- **Copyright**: PostGIS Development Team
- **Source**: https://postgis.net

### Apache Kafka / Redpanda
- **Project**: Redpanda / Apache Kafka Client Library
- **License**: BSL / Apache 2.0
- **Source**: https://redpanda.com / https://kafka.apache.org
- **Usage**: Distributed event streaming for normalized CloudEvents.

---

## 2. Frontend Libraries

### Next.js & React
- **Project**: Next.js (Vercel) & React (Meta)
- **License**: MIT License
- **Copyright**: (c) Vercel, Inc. / Meta Platforms, Inc.
- **Source**: https://nextjs.org / https://react.dev

### MapLibre GL JS
- **Project**: MapLibre GL JS (Open-source vector tile map SDK)
- **License**: BSD-3-Clause
- **Copyright**: (c) 2020 MapLibre contributors
- **Source**: https://github.com/maplibre/maplibre-gl-js
- **Usage**: GPU-accelerated client-side rendering for 80,000 camera node clusters, FOV cones, and vehicle trajectory polylines.

### Lucide React & Tailwind CSS
- **Project**: Lucide Icons & Tailwind CSS
- **License**: MIT License / ISC License
- **Source**: https://lucide.dev / https://tailwindcss.com

---

## 3. Computer Vision & Machine Learning Libraries

### ONNX Runtime
- **Project**: ONNX Runtime (Cross-platform ML inference)
- **License**: MIT License
- **Copyright**: (c) Microsoft Corporation
- **Source**: https://github.com/microsoft/onnxruntime
- **Usage**: Hardware-accelerated inference backend for vehicle and license plate neural networks across CPU, Apple Silicon MPS, and NVIDIA GPUs.

### OpenCV (Open Source Computer Vision Library)
- **Project**: OpenCV / opencv-python-headless
- **License**: Apache 2.0 License
- **Copyright**: (c) OpenCV team and contributors
- **Source**: https://opencv.org
- **Usage**: Frame decoding, image preprocessing, bounding box cropping, and perspective transform.

### ByteTrack
- **Project**: ByteTrack: Multi-Object Tracking by Associating Every Detection Box
- **License**: MIT License
- **Copyright**: (c) 2021 Yifu Zhang et al.
- **Source**: https://github.com/ifzhang/ByteTrack
- **Usage**: Per-camera spatial object association and tracklet continuity.

---

## 4. Government Standards & Protocol Conformance

- **CloudEvents 1.0**: CNCF specification for event data formatting.
- **ONVIF Core Specification**: Profile S (Streaming) & Profile G (Storage/Retrieval).
- **India MoRTH High Security Registration Plate (HSRP) Standard**: Conformance to AIS-037 & Motor Vehicles Act format specifications.
