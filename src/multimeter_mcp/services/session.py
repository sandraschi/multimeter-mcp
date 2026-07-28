from __future__ import annotations

from typing import Literal

from multimeter_mcp.config import get_settings
from multimeter_mcp.models.device import DeviceCapabilities, DeviceInfo
from multimeter_mcp.services.backends.base import DmmBackend
from multimeter_mcp.services.backends.scpi_serial import ScpiSerialBackend
from multimeter_mcp.services.backends.simulator import SimulatorBackend

BackendPreference = Literal["auto", "simulator", "scpi_serial"]


class DmmSession:
    def __init__(self) -> None:
        self._backend: DmmBackend | None = None
        self._backend_name: str | None = None
        self._available: dict[str, DmmBackend] = {
            "simulator": SimulatorBackend(),
            "scpi_serial": ScpiSerialBackend(),
        }

    @property
    def backend(self) -> DmmBackend | None:
        return self._backend

    @property
    def backend_name(self) -> str | None:
        return self._backend_name

    def list_backends(self) -> list[str]:
        return list(self._available.keys())

    def get_backend(self, name: str) -> DmmBackend:
        backend = self._available.get(name)
        if backend is None:
            raise ValueError(f"Unknown backend '{name}'")
        return backend

    async def resolve_backend(self, preference: BackendPreference | None = None) -> DmmBackend:
        pref = preference or get_settings().backend
        if pref != "auto":
            self._backend = self.get_backend(pref)
            self._backend_name = pref
            return self._backend
        for name in ("scpi_serial", "simulator"):
            backend = self.get_backend(name)
            devices = await backend.list_devices()
            if any(d.driver_status == "available" for d in devices):
                self._backend = backend
                self._backend_name = name
                return backend
        self._backend = self.get_backend("simulator")
        self._backend_name = "simulator"
        return self._backend

    async def list_all_devices(self) -> list[DeviceInfo]:
        out: list[DeviceInfo] = []
        for name in self._available:
            try:
                out.extend(await self._available[name].list_devices())
            except Exception as exc:
                out.append(
                    DeviceInfo(
                        device_id=f"{name}:error",
                        backend="simulator",
                        model=name,
                        connected=False,
                        capabilities=DeviceCapabilities(backend="simulator", notes=str(exc)),
                        driver_status="unavailable",
                    )
                )
        return out

    async def connect(self, device_id: str, *, backend: str | None = None) -> DeviceInfo:
        if backend:
            selected = self.get_backend(backend)
        elif device_id.startswith("scpi:"):
            selected = self.get_backend("scpi_serial")
        elif device_id.startswith("sim-"):
            selected = self.get_backend("simulator")
        else:
            selected = await self.resolve_backend()
        if self._backend and self._backend is not selected:
            await self._backend.disconnect()
        self._backend = selected
        self._backend_name = selected.name
        return await selected.connect(device_id)

    async def disconnect(self) -> None:
        if self._backend:
            await self._backend.disconnect()
        self._backend = None
        self._backend_name = None
