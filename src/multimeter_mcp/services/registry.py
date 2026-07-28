from __future__ import annotations

from multimeter_mcp.services.session import DmmSession

_session: DmmSession | None = None
_last_read: dict[str, float | bool | str] | None = None


def get_session() -> DmmSession:
    global _session
    if _session is None:
        _session = DmmSession()
    return _session


def set_last_read(data: dict[str, float | bool | str]) -> None:
    global _last_read
    _last_read = data


def get_last_read() -> dict[str, float | bool | str] | None:
    return _last_read


async def clear_services() -> None:
    global _session, _last_read
    if _session:
        await _session.disconnect()
    _session = None
    _last_read = None
