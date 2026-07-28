from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

BackendType = Literal["simulator", "scpi_serial"]


class DeviceCapabilities(BaseModel):
    backend: BackendType
    modes: list[str] = ["dc_voltage", "dc_current", "resistance", "continuity"]
    scpi: bool = False
    notes: str | None = None


class DeviceInfo(BaseModel):
    device_id: str
    backend: BackendType
    model: str
    port: str | None = None
    connected: bool = False
    capabilities: DeviceCapabilities
    driver_status: str = "available"
    driver_hint: str | None = None
