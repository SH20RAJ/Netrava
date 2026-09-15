"""Unit tests for 80,000-Camera Scalability Calculator."""

from schemas.system import ScalabilityCalculationRequest
from services.scalability_calculator import ScalabilityCalculator


def test_80k_camera_sizing_equations():
    req = ScalabilityCalculationRequest(
        camera_count=80000,
        average_bitrate_mbps=2.5,
        analytics_fps=5.0,
        hot_storage_days=7,
        regional_hubs_count=34,
        gpu_inference_rate_fps=350.0
    )
    result = ScalabilityCalculator.calculate_sizing(req)

    # 1. Verify naive centralized raw video = 80,000 * 2.5 Mbps = 200 Gbps
    assert result.centralized_raw_video_bandwidth_gbps == 200.0

    # 2. Verify Netrava edge-to-cloud metadata bandwidth is < 500 Mbps (approx 99.8% reduction)
    assert result.netrava_edge_to_cloud_bandwidth_mbps < 500.0
    assert result.bandwidth_reduction_pct > 99.0

    # 3. Verify total inferences per sec = 80,000 * 5 = 400,000
    assert result.total_statewide_inferences_per_sec == 400000.0

    # 4. Verify GPU allocation per district hub
    # 80000 / 34 ~ 2352 cams per hub * 5 FPS = 11764 inferences/sec / 350 FPS/GPU ~ 34 GPUs per hub
    assert 30 <= result.gpus_required_per_hub <= 40

    # 5. Verify hot storage
    assert result.hot_storage_petabytes > 10.0
