from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from multimeter_mcp.app import mcp
from multimeter_mcp.services.registry import get_session


@mcp.tool()
async def dmm_help(
    operation: Annotated[Literal["quickstart", "discover", "status"], Field()] = "quickstart",
) -> ToolResult:
    if operation == "quickstart":
        return ToolResult(
            content={
                "success": True,
                "steps": [
                    "dmm_device(operation='connect', device_id='sim-dmm-001')",
                    "dmm_measure(operation='set_probe', dc_voltage_v=5.0, resistance_ohm=1000)",
                    "dmm_measure(operation='dc_voltage')",
                    "dmm_measure(operation='continuity')",
                ],
            }
        )
    if operation == "discover":
        return ToolResult(
            content={
                "success": True,
                "tools": ["dmm_device", "dmm_measure", "dmm_help"],
            }
        )
    session = get_session()
    return ToolResult(content={"success": True, "backend": session.backend_name})
