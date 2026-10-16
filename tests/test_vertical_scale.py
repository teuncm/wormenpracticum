import numpy as np
import pytest

from app.feature.analysis.vertical_scale import (
    default_total_amplitude,
    vertical_pin_layout,
)


def test_default_amplitude_uses_absolute_finite_values_and_visible_count():
    values = np.array([[np.nan, np.inf], [2.0, -3.0]])
    assert default_total_amplitude(values, 2) == pytest.approx(14.4)
    assert default_total_amplitude(np.full(4, np.nan), 4) == pytest.approx(0.004)
    assert default_total_amplitude(np.full(3, 2.0), 1) == pytest.approx(4.8)


def test_vertical_pin_layout_keeps_lowest_baseline_at_zero():
    spacing, offsets = vertical_pin_layout(16.0, 4)
    assert spacing == 4.0
    assert offsets == [0.0, 4.0, 8.0, 12.0]
    assert vertical_pin_layout(4.0, 0) == (4.0, [0.0])
