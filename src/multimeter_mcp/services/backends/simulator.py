from __future__ import annotations

from multimeter_mcp.models.device import DeviceCapabilities, DeviceInfo
from multimeter_mcp.models.state import DmmState, MeasureMode
from multimeter_mcp.services.backends.base import DmmBackend


class SimulatorBackend(DmmBackend):
    name = "simulator"

    def __init__(self) -> None:
        self._device_id: str | None = None
        self._state = DmmState()

    async def list_devices(self) -> list[DeviceInfo]:
        return [
            DeviceInfo(
                device_id="sim-dmm-001",
                backend="simulator",
                model="Bench DMM Simulator (Fluke 87V model)",
                connected=self._device_id == "sim-dmm-001",
                capabilities=DeviceCapabilities(
                    backend="simulator",
                    notes="Probe model with settable V/I/R. Readings computed from probe state.",
                ),
            )
        ]

    async def connect(self, device_id: str) -> DeviceInfo:
        if device_id != "sim-dmm-001":
            raise ValueError(f"Unknown simulator device '{device_id}'")
        self._device_id = device_id
        devices = await self.list_devices()
        return devices[0].model_copy(update={"connected": True})

    async def disconnect(self) -> None:
        self._device_id = None

    async def get_connected_device(self) -> DeviceInfo | None:
        if not self._device_id:
            return None
        devices = await self.list_devices()
        return devices[0].model_copy(update={"connected": True})

    async def get_state(self) -> DmmState:
        self._require_connected()
        return self._state

    async def set_mode(self, mode: MeasureMode) -> DmmState:
        self._require_connected()
        self._state = self._state.model_copy(update={"mode": mode})
        return self._state

    async def set_probe(
        self,
        *,
        dc_voltage_v: float | None = None,
        dc_current_a: float | None = None,
        resistance_ohm: float | None = None,
    ) -> DmmState:
        self._require_connected()
        probe = self._state.probe
        updates: dict[str, float] = {}
        if dc_voltage_v is not None:
            updates["dc_voltage_v"] = dc_voltage_v
        if dc_current_a is not None:
            updates["dc_current_a"] = dc_current_a
        if resistance_ohm is not None:
            updates["resistance_ohm"] = resistance_ohm
        if updates:
            probe = probe.model_copy(update=updates)
            self._state = self._state.model_copy(update={"probe": probe})
        return self._state

    async def read(self) -> dict[str, float | bool | str]:
        self._require_connected()
        data = self._state.measure()
        data["backend"] = self.name
        return data

    def _require_connected(self) -> None:
        if not self._device_id:
            raise RuntimeError("No DMM connected. Use dmm_device(operation='connect').")
