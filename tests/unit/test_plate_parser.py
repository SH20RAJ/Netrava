"""Unit tests for Indian license plate parser and temporal voter."""

from services.ai_pipeline.anpr import IndianPlateParser, TemporalPlateVoter


def test_normalize_valid_gujarat_plate():
    plate, conf = IndianPlateParser.normalize_plate_syntax("GJ01AB1234")
    assert plate == "GJ01AB1234"
    assert conf >= 0.90


def test_rectify_character_confusion_numeric_zone():
    # 'O' in place of '0' in RTO code and 'B' in place of '8'
    plate, conf = IndianPlateParser.normalize_plate_syntax("GJO1AB1238")
    assert plate.startswith("GJ01")


def test_temporal_voting_consensus():
    voter = TemporalPlateVoter(voting_window=5)
    # 4 frames with GJ01AB1234, 1 noisy frame with GJ01AB1284
    voter.add_observation("trk_1", "GJ01AB1234", 0.90)
    voter.add_observation("trk_1", "GJ01AB1234", 0.95)
    voter.add_observation("trk_1", "GJ01AB1284", 0.60)
    voter.add_observation("trk_1", "GJ01AB1234", 0.92)
    consensus_plate, consensus_conf, votes = voter.add_observation("trk_1", "GJ01AB1234", 0.94)

    assert consensus_plate == "GJ01AB1234"
    assert votes == 4
    assert consensus_conf > 0.90
