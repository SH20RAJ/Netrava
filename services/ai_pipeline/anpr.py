"""Indian License Plate Recognition (ANPR) & Temporal Voting Engine.

Conforms to India Ministry of Road Transport and Highways (MoRTH)
High Security Registration Plate (HSRP) standards:
Syntax: [State Code: 2 letters] [RTO Code: 1-2 digits] [Series: 0-3 letters] [Registration: 4 digits]
Example: GJ01AB1234, GJ05CD5678, DL08C9999, MH12DE4321
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class IndianPlateParser:
    # Standard State Codes in India
    STATE_CODES = {
        "GJ", "MH", "DL", "KA", "TN", "UP", "HR", "RJ", "MP", "WB", 
        "PB", "AP", "TS", "KL", "BR", "JH", "OD", "CH", "GA", "UT"
    }

    # Character confusion matrix for OCR rectification based on position syntax
    NUM_TO_ALPHA = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B'}
    ALPHA_TO_NUM = {'O': '0', 'D': '0', 'Q': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8'}

    @classmethod
    def normalize_plate_syntax(cls, raw_text: str) -> Tuple[str, float]:
        """Cleans and rectifies OCR output into valid Indian HSRP format."""
        cleaned = re.sub(r'[^A-Z0-9]', '', raw_text.upper())
        if len(cleaned) < 8 or len(cleaned) > 11:
            return cleaned, 0.5  # Return raw if length abnormal

        chars = list(cleaned)

        # 1. First two characters MUST be State letters (e.g. GJ)
        for i in range(2):
            if chars[i] in cls.ALPHA_TO_NUM.values():
                chars[i] = cls.NUM_TO_ALPHA.get(chars[i], chars[i])

        # 2. Characters 2-4 are RTO digits (e.g. 01)
        if chars[2] in cls.NUM_TO_ALPHA.values():
            chars[2] = cls.ALPHA_TO_NUM.get(chars[2], chars[2])
        if chars[3] in cls.NUM_TO_ALPHA.values():
            chars[3] = cls.ALPHA_TO_NUM.get(chars[3], chars[3])

        # 3. Last 4 characters MUST be registration digits
        for i in range(-4, 0):
            if chars[i] in cls.NUM_TO_ALPHA.values():
                chars[i] = cls.ALPHA_TO_NUM.get(chars[i], chars[i])

        rectified = "".join(chars)
        
        # Validate regex
        pattern = r'^([A-Z]{2})([0-9]{1,2})([A-Z]{1,3})([0-9]{4})$'
        match = re.match(pattern, rectified)
        if match:
            state = match.group(1)
            conf_bonus = 0.95 if state in cls.STATE_CODES else 0.85
            return rectified, conf_bonus

        return rectified, 0.70


class TemporalPlateVoter:
    """Aggregates plate readings across consecutive video frames to filter transient OCR noise."""

    def __init__(self, voting_window: int = 5):
        self.voting_window = voting_window
        # track_id -> list of (normalized_plate, confidence)
        self.track_candidates: Dict[str, List[Tuple[str, float]]] = defaultdict(list)

    def add_observation(self, track_id: str, raw_plate: str, confidence: float) -> Tuple[str, float, int]:
        """Records a new frame reading and returns (consensus_plate, consensus_confidence, vote_count)."""
        normalized, syntax_conf = IndianPlateParser.normalize_plate_syntax(raw_plate)
        combined_conf = (confidence * 0.6) + (syntax_conf * 0.4)

        self.track_candidates[track_id].append((normalized, combined_conf))
        if len(self.track_candidates[track_id]) > self.voting_window:
            self.track_candidates[track_id].pop(0)

        # Compute weighted consensus
        score_by_plate: Dict[str, float] = defaultdict(float)
        count_by_plate: Dict[str, int] = defaultdict(int)

        for plate, conf in self.track_candidates[track_id]:
            score_by_plate[plate] += conf
            count_by_plate[plate] += 1

        best_plate = max(score_by_plate, key=score_by_plate.get)
        total_votes = count_by_plate[best_plate]
        avg_confidence = score_by_plate[best_plate] / total_votes

        # Confidence boosted if multiple consecutive frames agree
        temporal_boost = min(0.08, (total_votes - 1) * 0.02)
        final_confidence = min(0.999, avg_confidence + temporal_boost)

        return best_plate, round(final_confidence, 4), total_votes
