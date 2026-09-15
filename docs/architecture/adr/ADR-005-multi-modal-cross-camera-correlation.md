# ADR-005: Multi-Modal Cross-Camera Correlation and Kinematic Plausibility

## Status
Accepted

## Context
Standard license plate recognition systems often rely exclusively on string equality (`plate_A == plate_B`). In public safety surveillance, this causes critical failures:
1. Dirt, occlusion, or bad lighting causes OCR character errors ('8' vs 'B', '0' vs 'D').
2. Criminals frequently install cloned or fraudulent plates on different vehicles.
3. Two sightings 10 km apart within 10 seconds cannot physically be the same vehicle.

## Decision
Netrava enforces an **Explainable Multi-Signal Composite Score**:
$$\text{MatchScore} = S_{\text{plate}} (60\text{ pts}) + S_{\text{kinematic}} (15\text{ pts}) + S_{\text{class}} (10\text{ pts}) + S_{\text{color}} (5\text{ pts}) + S_{\text{visual}} (10\text{ pts})$$

- **Kinematic Speed Validator**: Calculates transit velocity via Haversine distance and elapsed time. If velocity exceeds 180 km/h, Netrava immediately raises a **CLONED / FRAUDULENT PLATE ANOMALY ALERT** rather than linking the sightings into an erroneous path.
- **Explainability**: Every match returns a point-by-point narrative explaining precisely why the platform concluded two camera events represent the same physical entity.
