import pytest

from multimeter_mcp.services.backends.simulator import SimulatorBackend


@pytest.mark.asyncio
async def test_simulator_dc_voltage():
    backend = SimulatorBackend()
    await backend.connect("sim-dmm-001")
    await backend.set_probe(dc_voltage_v=12.5)
    await backend.set_mode("dc_voltage")
    reading = await backend.read()
    assert reading["backend"] == "simulator"
    assert reading["value"] == 12.5
    assert reading["unit"] == "V"


@pytest.mark.asyncio
async def test_simulator_continuity():
    backend = SimulatorBackend()
    await backend.connect("sim-dmm-001")
    await backend.set_probe(resistance_ohm=10.0)
    await backend.set_mode("continuity")
    reading = await backend.read()
    assert reading["value"] is True
