from __future__ import annotations

from abc import ABC, abstractmethod

from multimeter_mcp.models.device import DeviceInfo
from multimeter_mcp.models.state import DmmState, MeasureMode


class DmmBackend(ABC):
    name: str

    @abstractmethod
    async def list_devices(self) -> list[DeviceInfo]: ...

    @abstractmethod
    async def connect(self, device_id: str) -> DeviceInfo: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def get_connected_device(self) -> DeviceInfo | None: ...

    @abstractmethod
    async def get_state(self) -> DmmState: ...

    @abstractmethod
    async def set_mode(self, mode: MeasureMode) -> DmmState: ...

    @abstractmethod
    async def read(self) -> dict[str, float | bool | str]: ...
