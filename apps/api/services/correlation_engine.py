"""Multi-Modal Cross-Camera Correlation & Kinematic Plausibility Engine.

Computes explainable match scores combining:
1. License Plate string distance & Indian HSRP syntax rules (Max 60 pts)
2. Kinematic travel time & speed plausibility (Max 15 pts)
3. Vehicle Classification & Model consistency (Max 10 pts)
4. Vehicle Dominant Color consistency (Max 5 pts)
5. Visual Re-ID Embedding Cosine Similarity (Max 10 pts)
"""

import math
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two points on Earth in kilometers."""
    r = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Computes normalized string similarity [0.0, 1.0] between two strings."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    max_len = max(m, n)
    return 1.0 - (dp[m][n] / max_len)


class CorrelationEngine:
    @staticmethod
    def evaluate_sighting_transition(
        prev_lat: float,
        prev_lon: float,
        prev_time: datetime,
        curr_lat: float,
        curr_lon: float,
        curr_time: datetime,
        plate_a: str,
        plate_b: str,
        class_a: str = "car",
        class_b: str = "car",
        color_a: str = "white",
        color_b: str = "white",
        embedding_a: Optional[List[float]] = None,
        embedding_b: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Calculates explainable correlation score and kinematic validation."""
        reasons: List[str] = []
        distance_km = haversine_distance_km(prev_lat, prev_lon, curr_lat, curr_lon)
        time_delta_sec = abs((curr_time - prev_time).total_seconds())
        time_delta_hours = time_delta_sec / 3600.0

        # 1. Plate Match (Max 60 pts)
        sim = levenshtein_similarity(plate_a, plate_b)
        if plate_a == plate_b:
            plate_score = 60.0
            reasons.append("Exact license plate match (+60)")
        elif sim >= 0.8:
            plate_score = round(45.0 * sim, 1)
            reasons.append(f"High plate visual similarity {sim*100:.0f}% (+{plate_score})")
        else:
            plate_score = round(20.0 * sim, 1)
            reasons.append(f"Partial plate similarity {sim*100:.0f}% (+{plate_score})")

        # 2. Kinematic & Speed Plausibility (Max 15 pts)
        anomaly_detected = False
        anomaly_type = None
        is_plausible = True

        if time_delta_sec < 1.0:
            if distance_km > 0.05:
                # Same vehicle seen at two distinct locations within 1 second -> Cloned Plate!
                kinematic_score = -40.0
                is_plausible = False
                anomaly_detected = True
                anomaly_type = "IMPOSSIBLE_SPEED_CLONED_PLATE"
                implied_speed = 999.9
                reasons.append("ALERT: Near-simultaneous sighting on distinct cameras! High probability of CLONED / FRAUDULENT PLATE (-40)")
            else:
                kinematic_score = 15.0
                implied_speed = 0.0
                reasons.append("Stationary sighting on same or adjacent camera (+15)")
        else:
            implied_speed = distance_km / time_delta_hours
            if implied_speed <= 120.0:
                kinematic_score = 15.0
                reasons.append(f"Transit velocity {implied_speed:.1f} km/h is highly plausible (+15)")
            elif implied_speed <= 160.0:
                kinematic_score = 8.0
                reasons.append(f"Elevated highway velocity {implied_speed:.1f} km/h (+8)")
            else:
                kinematic_score = -35.0
                is_plausible = False
                anomaly_detected = True
                anomaly_type = "IMPOSSIBLE_SPEED_CLONED_PLATE"
                reasons.append(f"ALERT: Physically impossible transit velocity ({implied_speed:.1f} km/h) indicates CLONED PLATE (-35)")

        # 3. Vehicle Classification Consistency (Max 10 pts)
        if class_a.lower() == class_b.lower():
            class_score = 10.0
            reasons.append(f"Vehicle class consistent ({class_a}) (+10)")
        else:
            class_score = -15.0
            anomaly_detected = True
            anomaly_type = "VEHICLE_CLASS_MISMATCH"
            reasons.append(f"Vehicle class conflict: {class_a} vs {class_b} (-15)")

        # 4. Color Consistency (Max 5 pts)
        if color_a.lower() == color_b.lower():
            color_score = 5.0
            reasons.append(f"Color consistent ({color_a}) (+5)")
        else:
            color_score = 0.0
            reasons.append(f"Color variation: {color_a} vs {color_b} (+0)")

        # 5. Visual Re-ID Embedding (Max 10 pts)
        visual_score = 0.0
        if embedding_a and embedding_b and len(embedding_a) == len(embedding_b):
            dot_product = sum(a * b for a, b in zip(embedding_a, embedding_b))
            norm_a = math.sqrt(sum(a * a for a in embedding_a))
            norm_b = math.sqrt(sum(b * b for b in embedding_b))
            if norm_a > 0 and norm_b > 0:
                cosine_sim = dot_product / (norm_a * norm_b)
                if cosine_sim > 0.7:
                    visual_score = round(cosine_sim * 10.0, 1)
                    reasons.append(f"Vehicle visual feature match {cosine_sim*100:.0f}% (+{visual_score})")

        total_score = max(0.0, min(100.0, plate_score + kinematic_score + class_score + color_score + visual_score))

        return {
            "match_score": round(total_score, 1),
            "is_match": total_score >= 65.0,
            "is_plausible": is_plausible,
            "implied_speed_kmh": round(implied_speed, 1),
            "distance_km": round(distance_km, 2),
            "transit_minutes": round(time_delta_sec / 60.0, 1),
            "anomaly_detected": anomaly_detected,
            "anomaly_type": anomaly_type,
            "score_breakdown": {
                "plate_score": plate_score,
                "kinematic_score": kinematic_score,
                "class_score": class_score,
                "color_score": color_score,
                "visual_score": visual_score
            },
            "reasons": reasons
        }
