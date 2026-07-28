from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from multimeter_mcp.app import mcp
from multimeter_mcp.config import get_settings
from multimeter_mcp.services.registry import get_session


@mcp.tool()
async def dmm_device(
    operation: Annotated[Literal["list", "connect", "disconnect", "status", "backends"], Field()],
    device_id: Annotated[str | None, Field()] = None,
    backend: Annotated[str | None, Field()] = None,
) -> ToolResult:
    session = get_session()
    try:
        if operation == "list":
            devices = await session.list_all_devices()
            return ToolResult(content={"success": True, "devices": [d.model_dump() for d in devices]})
        if operation == "backends":
            return ToolResult(
                content={"success": True, "backends": session.list_backends(), "active": session.backend_name}
            )
        if operation == "connect":
            if not device_id:
                raise ValueError("device_id required")
            dev = await session.connect(device_id, backend=backend)
            return ToolResult(content={"success": True, "device": dev.model_dump()})
        if operation == "disconnect":
            await session.disconnect()
            return ToolResult(content={"success": True})
        if operation == "status":
            active = session.backend
            if not active:
                return ToolResult(content={"success": True, "connected": False})
            dev = await active.get_connected_device()
            state = await active.get_state() if dev else None
            return ToolResult(
                content={
                    "success": True,
                    "connected": dev is not None,
                    "device": dev.model_dump() if dev else None,
                    "state": state.model_dump() if state else None,
                    "capture_dir": str(get_settings().work_dir),
                }
            )
        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "error": str(exc)})
