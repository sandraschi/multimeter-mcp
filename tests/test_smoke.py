import pytest


def _payload(result) -> dict:
    content = result.content
    if isinstance(content, dict):
        return content
    if isinstance(content, list) and content:
        item = content[0]
        if hasattr(item, "text"):
            import json

            return json.loads(item.text)
    raise AssertionError(type(content))


@pytest.mark.asyncio
async def test_help_discover():
    from multimeter_mcp.tools.portmanteau.help import dmm_help

    result = await dmm_help(operation="discover")
    assert _payload(result)["success"] is True
    assert "dmm_measure" in _payload(result)["tools"]


@pytest.mark.asyncio
async def test_simulator_flow():
    from multimeter_mcp.services.registry import clear_services
    from multimeter_mcp.tools.portmanteau.device import dmm_device
    from multimeter_mcp.tools.portmanteau.measure import dmm_measure

    await clear_services()
    await dmm_device(operation="connect", device_id="sim-dmm-001")
    await dmm_measure(operation="set_probe", dc_voltage_v=3.3)
    result = await dmm_measure(operation="dc_voltage")
    reading = _payload(result)["reading"]
    assert reading["value"] == 3.3
    assert reading["backend"] == "simulator"
