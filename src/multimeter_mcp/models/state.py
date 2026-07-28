from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

MeasureMode = Literal["dc_voltage", "dc_current", "resistance", "continuity"]


class ProbeModel(BaseModel):
    """Simulator-only circuit under test."""

    dc_voltage_v: float = Field(3.3, ge=0.0, le=1000.0)
    dc_current_a: float = Field(0.01, ge=0.0, le=10.0)
    resistance_ohm: float = Field(1000.0, gt=0.0, le=1_000_000.0)


class DmmState(BaseModel):
    mode: MeasureMode = "dc_voltage"
    range_auto: bool = True
    probe: ProbeModel = Field(default_factory=ProbeModel)

    def measure(self) -> dict[str, float | bool | str]:
        if self.mode == "dc_voltage":
            return {
                "mode": self.mode,
                "value": round(self.probe.dc_voltage_v, 6),
                "unit": "V",
            }
        if self.mode == "dc_current":
            return {
                "mode": self.mode,
                "value": round(self.probe.dc_current_a, 6),
                "unit": "A",
            }
        if self.mode == "resistance":
            return {
                "mode": self.mode,
                "value": round(self.probe.resistance_ohm, 2),
                "unit": "ohm",
            }
        continuity = self.probe.resistance_ohm < 50.0
        return {
            "mode": self.mode,
            "value": continuity,
            "unit": "bool",
            "resistance_ohm": round(self.probe.resistance_ohm, 2),
        }
