import numpy as np
import pytest
from app.model.signal import get_timeframe_s, get_timepoint_s

TEST_SR_HZ = 4.0


@pytest.fixture
def simple_timeframe_s():
    return [0.0, 0.25, 0.5, 0.75, 1.0]


def test_get_timeframe_s(simple_timeframe_s):
    """Verify that the signal timeframe is calculated correctly."""
    timeframe = get_timeframe_s(n_samples=len(simple_timeframe_s), sr_hz=TEST_SR_HZ)

    expected_timeframe = np.array(simple_timeframe_s)
    assert np.allclose(timeframe, expected_timeframe)


def test_get_timepoint_s():
    """Verify that the signal timeframe is calculated correctly."""
    assert 0.0 == get_timepoint_s(sr_hz=TEST_SR_HZ, sample_offset=0)
    assert 1.0 == get_timepoint_s(sr_hz=TEST_SR_HZ, sample_offset=4)
