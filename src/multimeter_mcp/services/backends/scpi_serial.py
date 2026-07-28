from __future__ import annotations

import asyncio

from multimeter_mcp.models.device import DeviceCapabilities, DeviceInfo
from multimeter_mcp.models.state import DmmState, MeasureMode
from multimeter_mcp.services.backends.base import DmmBackend

_MODE_SCPI: dict[MeasureMode, tuple[str, str]] = {
    "dc_voltage": ('FUNC "VOLT:DC"', "MEAS:VOLT:DC?"),
    "dc_current": ('FUNC "CURR:DC"', "MEAS:CURR:DC?"),
    "resistance": ('FUNC "RES"', "MEAS:RES?"),
    "continuity": ('FUNC "RES"', "MEAS:RES?"),
}


def _list_ports() -> list[str]:
    try:
        from serial.tools import list_ports
    except ImportError:
        return []
    return [p.device for p in list_ports.comports()]


async def _query(port: str, cmd: str) -> str:
    return await asyncio.to_thread(_query_sync, port, cmd)


async def _write(port: str, cmd: str) -> None:
    await asyncio.to_thread(_write_sync, port, cmd)


def _query_sync(port: str, cmd: str) -> str:
    import serial

    with serial.Serial(port=port, baudrate=9600, timeout=2.0) as ser:
        ser.write(f"{cmd}\n".encode())
        ser.flush()
        return ser.readline().decode("utf-8", errors="replace").strip()


def _write_sync(port: str, cmd: str) -> None:
    import serial

    with serial.Serial(port=port, baudrate=9600, timeout=2.0) as ser:
        ser.write(f"{cmd}\n".encode())
        ser.flush()


class ScpiSerialBackend(DmmBackend):
    name = "scpi_serial"

    def __init__(self) -> None:
        self._port: str | None = None
        self._device_id: str | None = None
        self._mode: MeasureMode = "dc_voltage"

    async def list_devices(self) -> list[DeviceInfo]:
        try:
            import serial  # noqa: F401
        except ImportError:
            return [
                DeviceInfo(
                    device_id="scpi:unavailable",
                    backend="scpi_serial",
                    model="pyserial not installed",
                    connected=False,
                    capabilities=DeviceCapabilities(backend="scpi_serial", scpi=True, notes="uv sync --extra serial"),
                    driver_status="unavailable",
                    driver_hint="pip install pyserial",
                )
            ]
        devices: list[DeviceInfo] = []
        for port in _list_ports():
            devices.append(
                DeviceInfo(
                    device_id=f"scpi:{port}",
                    backend="scpi_serial",
                    model=f"SCPI DMM on {port}",
                    port=port,
                    connected=self._device_id == f"scpi:{port}",
                    capabilities=DeviceCapabilities(backend="scpi_serial", scpi=True),
                )
            )
        if not devices:
            devices.append(
                DeviceInfo(
                    device_id="scpi:none",
                    backend="scpi_serial",
                    model="No COM ports found",
                    connected=False,
                    capabilities=DeviceCapabilities(backend="scpi_serial", scpi=True),
                    driver_status="no_devices",
                )
            )
        return devices

    async def connect(self, device_id: str) -> DeviceInfo:
        port = device_id.removeprefix("scpi:")
        if not port or port in {"unavailable", "none"}:
            raise ValueError(f"Cannot connect to '{device_id}'")
        self._port = port
        self._device_id = device_id
        devices = await self.list_devices()
        match = next((d for d in devices if d.device_id == device_id), None)
        if match:
            return match.model_copy(update={"connected": True})
        return DeviceInfo(
            device_id=device_id,
            backend="scpi_serial",
            model=port,
            port=port,
            connected=True,
            capabilities=DeviceCapabilities(backend="scpi_serial", scpi=True),
        )

    async def disconnect(self) -> None:
        self._port = None
        self._device_id = None

    async def get_connected_device(self) -> DeviceInfo | None:
        if not self._device_id:
            return None
        devices = await self.list_devices()
        return next((d.model_copy(update={"connected": True}) for d in devices if d.device_id == self._device_id), None)

    async def get_state(self) -> DmmState:
        self._require_port()
        return DmmState(mode=self._mode)

    async def set_mode(self, mode: MeasureMode) -> DmmState:
        self._require_port()
        func_cmd, _ = _MODE_SCPI[mode]
        await _write(self._port, func_cmd)
        self._mode = mode
        return DmmState(mode=mode)

    async def read(self) -> dict[str, float | bool | str]:
        self._require_port()
        _, meas_cmd = _MODE_SCPI[self._mode]
        raw = await _query(self._port, meas_cmd)
        if self._mode == "continuity":
            resistance = float(raw)
            return {
                "backend": self.name,
                "mode": self._mode,
                "value": resistance < 50.0,
                "unit": "bool",
                "resistance_ohm": resistance,
            }
        value = float(raw)
        unit = {"dc_voltage": "V", "dc_current": "A", "resistance": "ohm"}[self._mode]
        return {"backend": self.name, "mode": self._mode, "value": value, "unit": unit}

    def _require_port(self) -> None:
        if not self._port:
            raise RuntimeError("No SCPI DMM connected.")
