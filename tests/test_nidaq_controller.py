from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest

from app.feature.acquisition.protocol_config import ProtocolConfig
from app.feature.nidaq import nidaq_controller as module
from app.feature.stimulus.pulse import Pulse
from app.feature.stimulus.stimulus_config import StimulusConfig
from app.feature.stimulus.stimulus_generator import StimulusGenerator


@pytest.mark.parametrize("duration", [0.5, 0.0])
@pytest.mark.parametrize("divider", [1, 4])
def test_execute_concatenated_buffer(monkeypatch, duration, divider):
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
        protocol_config=ProtocolConfig(
            positive_channel=4,
            negative_channel=8,
            selected_pins=[2, 3],
            sample_rate_divider=divider,
        ),
        update_recording=MagicMock(),
    )
    tasks = [MagicMock() for _ in range(3)]
    for task in tasks:
        task.__enter__.return_value = task
    task_factory = MagicMock(side_effect=tasks)
    monkeypatch.setattr(module, "Task", task_factory)
    writer = MagicMock()
    reader = MagicMock()
    writer_factory = MagicMock(return_value=writer)
    monkeypatch.setattr(module, "AnalogMultiChannelWriter", writer_factory)
    monkeypatch.setattr(module, "AnalogMultiChannelReader", lambda stream: reader)
    events = []
    writer.write_many_sample.side_effect = lambda *a, **kw: events.append("preload")
    tasks[1].start.side_effect = lambda: events.append("start_ai")
    tasks[2].start.side_effect = lambda: events.append("start_ao")

    def read_samples(data, **kwargs):
        data[:] = np.arange(16)[:, None] * 100000 + np.arange(data.shape[1])
        events.append("read")

    reader.read_many_sample.side_effect = read_samples
    controller = module.NidaqController(SimpleNamespace(device_name="Dev1"), model)

    if duration == 0:
        with pytest.raises(ValueError, match="must contain samples"):
            controller.execute()
        task_factory.assert_not_called()
        model.update_recording.assert_not_called()
        return

    controller.execute()

    digital, ai, ao = tasks
    assert events == ["preload", "start_ai", "start_ao", "read"]
    writer_factory.assert_called_once_with(ao.out_stream, auto_start=False)
    digital.write.assert_called_once_with([132, 144])
    writer.write_many_sample.assert_called_once()
    output = writer.write_many_sample.call_args.args[0]
    rate = 15600 / divider
    step_samples = int(0.5 * rate)
    pulse_samples = int(0.25 * rate)
    n_samples = step_samples * 10
    assert output.shape == (2, n_samples)
    assert writer.write_many_sample.call_args.kwargs == {"timeout": 7.0}
    for step in range(10):
        np.testing.assert_allclose(
            output[0, step * step_samples : step * step_samples + pulse_samples],
            0.1 * (step + 1),
        )
        np.testing.assert_array_equal(
            output[0, step * step_samples + pulse_samples : (step + 1) * step_samples],
            0,
        )
    np.testing.assert_array_equal(output[1], -output[0])
    for task in (ai, ao):
        timing = task.timing.cfg_samp_clk_timing.call_args.kwargs
        assert timing["samps_per_chan"] == n_samples
        assert timing["rate"] == rate
        assert timing["sample_mode"] == module.AcquisitionType.FINITE
    assert (
        ai.timing.cfg_samp_clk_timing.call_args.kwargs["source"]
        == "/Dev1/ao/SampleClock"
    )
    ai.triggers.start_trigger.cfg_dig_edge_start_trig.assert_called_once_with(
        "/Dev1/ao/StartTrigger"
    )
    assert reader.read_many_sample.call_args.kwargs == {
        "number_of_samples_per_channel": n_samples,
        "timeout": 7.0,
    }
    ao.wait_until_done.assert_called_once_with(timeout=7.0)
    model.update_recording.assert_called_once()
    data, metadata, config = model.update_recording.call_args.args
    assert data.shape == (n_samples, 17)
    assert list(data.columns) == ["t_(s)", *[f"ai{i}_(V)" for i in range(16)]]
    np.testing.assert_array_equal(data["t_(s)"], np.arange(n_samples) / rate)
    for channel in range(16):
        np.testing.assert_array_equal(
            data[f"ai{channel}_(V)"], channel * 100000 + np.arange(n_samples)
        )
    assert metadata == {
        "device_name": "Dev1",
        "sample_rate_hz": rate,
        "stimulus_size_samples": step_samples,
        "stimulus_count": 10,
        "sample_count": n_samples,
        "pin_channels": {f"ai{i}_(V)": i + 1 for i in range(16)},
    }
    assert config["stim_config"] == generator.config.to_dict()
    assert config["protocol_config"]["sample_rate_divider"] == divider


@pytest.mark.parametrize("available", [False, True])
def test_run_requires_device_discovery(available):
    controller = module.NidaqController(
        SimpleNamespace(device_status="No device available"), SimpleNamespace()
    )
    controller.discover = MagicMock(return_value=available)
    controller.execute = MagicMock()

    if available:
        controller.run()
        controller.execute.assert_called_once_with()
    else:
        with pytest.raises(RuntimeError, match="No device available"):
            controller.run()
        controller.execute.assert_not_called()
