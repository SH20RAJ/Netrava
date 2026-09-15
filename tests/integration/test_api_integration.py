"""Integration tests for Netrava API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "NETRAVA"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_cameras_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/cameras")
    assert response.status_code == 200
    cameras = response.json()
    assert len(cameras) >= 50
    assert any(c["district"] == "Ahmedabad" for c in cameras)


@pytest.mark.asyncio
async def test_vehicle_dossier_target_plate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/vehicles/GJ01AB1234")
    assert response.status_code == 200
    dossier = response.json()
    assert dossier["normalized_plate"] == "GJ01AB1234"
    assert dossier["total_sightings"] == 4
    assert dossier["watchlist_flagged"] is True
    assert dossier["risk_level"] == "CRITICAL"


@pytest.mark.asyncio
async def test_vehicle_route_reconstruction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/vehicles/GJ01AB1234/route")
    assert response.status_code == 200
    route = response.json()
    assert route["normalized_plate"] == "GJ01AB1234"
    assert route["total_waypoints"] == 4
    assert route["total_distance_km"] > 10.0
    assert route["is_watchlist_hit"] is True
    assert len(route["geojson_polyline"]["features"]) >= 5


@pytest.mark.asyncio
async def test_scalability_calculator_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "camera_count": 80000,
            "average_bitrate_mbps": 2.5,
            "analytics_fps": 5.0,
            "hot_storage_days": 7,
            "regional_hubs_count": 34,
            "gpu_inference_rate_fps": 350.0
        }
        response = await ac.post("/api/v1/system/scalability-calculator", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["camera_count"] == 80000
    assert res["centralized_raw_video_bandwidth_gbps"] == 200.0
    assert res["bandwidth_reduction_pct"] > 99.0
    assert res["total_statewide_inferences_per_sec"] == 400000.0
