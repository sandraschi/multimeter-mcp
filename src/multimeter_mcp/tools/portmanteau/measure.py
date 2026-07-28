from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from multimeter_mcp.app import mcp
from multimeter_mcp.models.state import MeasureMode
from multimeter_mcp.services.backends.simulator import SimulatorBackend
from multimeter_mcp.services.registry import get_last_read, get_session, set_last_read


@mcp.tool()
async def dmm_measure(
    operation: Annotated[
        Literal["dc_voltage", "dc_current", "resistance", "continuity", "set_probe", "read", "last"],
        Field(),
    ],
    dc_voltage_v: Annotated[float | None, Field(ge=0)] = None,
    dc_current_a: Annotated[float | None, Field(ge=0)] = None,
    resistance_ohm: Annotated[float | None, Field(gt=0)] = None,
) -> ToolResult:
    session = get_session()
    try:
        backend = session.backend
        if backend is None:
            backend = await session.resolve_backend()
            await backend.connect("sim-dmm-001")

        if operation == "set_probe":
            if not isinstance(backend, SimulatorBackend):
                raise RuntimeError("set_probe only available on simulator backend")
            state = await backend.set_probe(
                dc_voltage_v=dc_voltage_v,
                dc_current_a=dc_current_a,
                resistance_ohm=resistance_ohm,
            )
            return ToolResult(content={"success": True, "state": state.model_dump()})

        if operation == "last":
            data = get_last_read()
            if not data:
                raise RuntimeError("No read yet. dmm_measure(operation='read')")
            return ToolResult(content={"success": True, "reading": data})

        if operation == "read":
            data = await backend.read()
            set_last_read(data)
            return ToolResult(content={"success": True, "reading": data})

        mode: MeasureMode = operation
        await backend.set_mode(mode)
        data = await backend.read()
        set_last_read(data)
        return ToolResult(content={"success": True, "reading": data})
    except Exception as exc:
        return ToolResult(content={"success": False, "error": str(exc)})
