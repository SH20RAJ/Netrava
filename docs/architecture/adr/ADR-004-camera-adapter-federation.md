# ADR-004: Camera Adapter Federation Pattern (Model 3)

## Status
Accepted

## Context
Gujarat's 80,000 CCTV cameras originate from diverse manufacturers (Hikvision, CP Plus, Axis, Dahua, Hanwha), standalone analog DVRs, on-premise NVRs, and proprietary departmental VMS platforms (Milestone, Genetec). Attempting to replace all existing hardware with a single centralized VMS is financially and logistically unviable.

## Decision
Netrava implements a vendor-neutral `CameraAdapter` interface:
```python
class CameraAdapter(ABC):
    async def discover(self) -> List[CameraEndpoint]: ...
    async def connect(self) -> StreamSession: ...
    async def get_stream_url(self, profile: str) -> str: ...
    async def get_health(self) -> HealthStatus: ...
```
Implemented adapters include:
1. `RTSPAdapter` (RFC 2326 / RFC 7826 standard video streams)
2. `ONVIFAdapter` (Profile S / G discovery, PTZ, and stream profile extraction)
3. `VMSFederationAdapter` (REST proxy for proprietary departmental systems)
4. `SyntheticStreamAdapter` (Offline / hackathon deterministic evaluation feeds)

Media streams are normalized into WebRTC and Low-Latency HLS via an embedded MediaMTX media server.
