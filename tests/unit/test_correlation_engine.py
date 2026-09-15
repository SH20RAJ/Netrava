"""Unit tests for Correlation Engine and Kinematic Plausibility."""

from datetime import datetime, timedelta
from services.correlation_engine import CorrelationEngine, haversine_distance_km


def test_haversine_distance():
    # Distance between SG Hwy Vaishnodevi (23.1365, 72.5412) and Thaltej (23.0504, 72.5085) ~ 10.1 km
    dist = haversine_distance_km(23.1365, 72.5412, 23.0504, 72.5085)
    assert 9.0 < dist < 12.0


def test_plausible_highway_transit():
    t0 = datetime(2026, 9, 15, 10, 31, 0)
    t1 = t0 + timedelta(minutes=13)  # 13 mins for 10 km ~ 46 km/h (Normal traffic)
    
    result = CorrelationEngine.evaluate_sighting_transition(
        23.1365, 72.5412, t0,
        23.0504, 72.5085, t1,
        "GJ01AB1234", "GJ01AB1234"
    )

    assert result["is_match"] is True
    assert result["is_plausible"] is True
    assert result["anomaly_detected"] is False
    assert result["match_score"] >= 80.0
    assert 40.0 < result["implied_speed_kmh"] < 60.0


def test_cloned_plate_detection_impossible_speed():
    t0 = datetime(2026, 9, 15, 10, 31, 0)
    t1 = t0 + timedelta(seconds=10)  # 10 seconds to travel 10 km = 3600 km/h -> Cloned plate!
    
    result = CorrelationEngine.evaluate_sighting_transition(
        23.1365, 72.5412, t0,
        23.0504, 72.5085, t1,
        "GJ01AB1234", "GJ01AB1234"
    )

    assert result["is_plausible"] is False
    assert result["anomaly_detected"] is True
    assert result["anomaly_type"] == "IMPOSSIBLE_SPEED_CLONED_PLATE"
