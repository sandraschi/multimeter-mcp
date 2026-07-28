import json
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from multimeter_mcp import __version__
from multimeter_mcp.services.registry import get_last_read, get_session


def setup_webapp(app: FastAPI, mcp: Any) -> None:
    @app.get("/health")
    async def health():
        return {"status": "ok", "server": "multimeter-mcp", "version": __version__}

    @app.get("/api/status")
    async def status():
        session = get_session()
        tools = await mcp.list_tools()
        active = session.backend
        dev = await active.get_connected_device() if active else None
        state = await active.get_state() if active and dev else None
        return {
            "status": "ok",
            "tools": [t.name for t in tools],
            "version": __version__,
            "backend": session.backend_name,
            "connected": dev is not None,
            "state": state.model_dump() if state else None,
            "last_reading": get_last_read(),
        }

    @app.get("/api/capabilities")
    async def capabilities():
        session = get_session()
        tools = await mcp.list_tools()
        devices = await session.list_all_devices()
        return {
            "status": "ok",
            "server": {"name": "multimeter-mcp", "version": __version__},
            "tool_surface": {"total": len(tools), "tools": [t.name for t in tools]},
            "backends": session.list_backends(),
            "devices": [d.model_dump() for d in devices],
            "runtime": {"backend_port": 11005, "frontend_port": 11006},
        }

    @app.post("/api/tools/{name}/call")
    async def api_tool_call(name: str, body: dict[str, Any]) -> JSONResponse | dict[str, Any]:
        try:
            result = await mcp.call_tool(name, body.get("arguments", {}))
            content = result.content if hasattr(result, "content") else result
            if isinstance(content, list) and content:
                item = content[0]
                text = item.text if hasattr(item, "text") else str(item)
                try:
                    parsed = json.loads(text)
                    return {"success": True, "data": parsed}
                except (json.JSONDecodeError, TypeError):
                    return {"success": True, "data": text}
            return {"success": True, "data": content}
        except Exception as exc:
            return JSONResponse({"success": False, "message": str(exc)}, status_code=500)
