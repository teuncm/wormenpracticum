import numpy as np
import pytest
from app.model.signal import (
    get_time_bounds_s,
    get_time_frame_s,
    get_time_point_s,
    quantize_time_point,
)

TEST_SR_HZ = 4.0


@pytest.fixture
def simple_time_frame_s():
    return [0.0, 0.25, 0.5, 0.75]


def test_quantize_time_point():
    """Verify that the time point is quantized correctly."""
    assert -1 == quantize_time_point(time_s=-0.2, sr_hz=TEST_SR_HZ)
    assert 0 == quantize_time_point(time_s=0.0, sr_hz=TEST_SR_HZ)
    assert 0 == quantize_time_point(time_s=0.2, sr_hz=TEST_SR_HZ)
    assert 1 == quantize_time_point(time_s=0.25, sr_hz=TEST_SR_HZ)


def test_get_time_frame_s(simple_time_frame_s):
    """Verify that the sample timeframe is calculated correctly."""
    time_frame = get_time_frame_s(n_samples=len(simple_time_frame_s), sr_hz=TEST_SR_HZ)

    expected_time_frame = np.array(simple_time_frame_s)
    assert np.allclose(time_frame, expected_time_frame)


def test_get_time_point_s():
    """Verify that the signal timeframe is calculated correctly."""
    assert 0.0 == get_time_point_s(sr_hz=TEST_SR_HZ, sample_offset=0)
    assert 0.75 == get_time_point_s(sr_hz=TEST_SR_HZ, sample_offset=3)


def test_get_time_bounds_s(simple_time_frame_s):
    """Verify that the signal time bounds are calculated correctly."""
    left, right = get_time_bounds_s(
        n_samples=len(simple_time_frame_s), sr_hz=TEST_SR_HZ, sample_offset=0
    )

    assert left == 0.0
    assert right == 1.0
