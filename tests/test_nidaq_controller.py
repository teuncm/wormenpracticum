from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest

from app.feature.nidaq import nidaq_controller as module
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_generator import StimulusGenerator


@pytest.mark.parametrize("duration", [0.5, 0.0])
def test_execute_concatenated_buffer(monkeypatch, duration):
    generator = StimulusGenerator(
        StimulusConfig(
            dur_s=duration,
            limit_v=3.0,
            n_steps=10,
            pulses=[
                Pulse(
                    amp_v=0.1,
                    start_s=0.0,
                    dur_s=0.25,
                    step_amp_v=0.1,
                    is_monophasic=True,
                )
            ],
        )
    )
    model = SimpleNamespace(
        stim_generator=generator,
        protocol_config=SimpleNamespace(positive_channel=4, negative_channel=8),
        update_raw_data=MagicMock(),
    )
    tasks = [MagicMock() for _ in range(3)]
    for task in tasks:
        task.__enter__.return_value = task
    task_factory = MagicMock(side_effect=tasks)
    monkeypatch.setattr(module, "Task", task_factory)
    writer = MagicMock()
    reader = MagicMock()
    monkeypatch.setattr(module, "AnalogMultiChannelWriter", lambda stream: writer)
    monkeypatch.setattr(module, "AnalogMultiChannelReader", lambda stream: reader)
    controller = module.NidaqController(SimpleNamespace(device_name="Dev1"), model)

    if duration == 0:
        with pytest.raises(ValueError, match="must contain samples"):
            controller.execute()
        task_factory.assert_not_called()
        return

    controller.execute()

    digital, ai, ao = tasks
    digital.write.assert_called_once_with([132, 144])
    writer.write_many_sample.assert_called_once()
    output = writer.write_many_sample.call_args.args[0]
    assert output.shape == (2, 78000)
    for step in range(10):
        np.testing.assert_allclose(
            output[0, step * 7800 : step * 7800 + 3900], 0.1 * (step + 1)
        )
        np.testing.assert_array_equal(
            output[0, step * 7800 + 3900 : (step + 1) * 7800], 0
        )
    np.testing.assert_array_equal(output[1], -output[0])
    for task in (ai, ao):
        assert (
            task.timing.cfg_samp_clk_timing.call_args.kwargs["samps_per_chan"] == 78000
        )
    assert reader.read_many_sample.call_args.kwargs == {
        "number_of_samples_per_channel": 78000,
        "timeout": 7.0,
    }
    ao.wait_until_done.assert_called_once_with(timeout=7.0)
    data = model.update_raw_data.call_args.args[0]
    assert data.shape == (78000, 17)
    np.testing.assert_array_equal(data["t_(s)"], np.arange(78000) / 15600)
