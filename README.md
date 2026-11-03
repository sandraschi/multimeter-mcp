# multimeter-mcp

FastMCP 3.2+ — **Multimeter MCP**. USB/serial bench multimeters and simulator.

## Quick start

```powershell
Set-Location D:\Dev\repos\multimeter-mcp
uv sync --extra dev
uv run python -m multimeter_mcp --stdio
```

## Tools

- `dmm_device` — list, connect, disconnect, status
- `dmm_run` — dc_voltage, dc_current, resistance, continuity
- `dmm_help` — quickstart, discover, status

## Ports

Backend: **11005** · Frontend: **11006** (webapp planned)

## Bench family

One bench, nine servers. `bench-orchestrator-mcp` conducts (`mcu_bringup` drives
its six wired peers); the rest are instruments:

| Server | Role | Wired peer? |
|--------|------|-------------|
| [bench-orchestrator-mcp](https://github.com/sandraschi/bench-orchestrator-mcp) | Conductor — `bench_workflow` (`power_check`, `bus_check`, `debug_check`, `mcu_bringup`) | — (it conducts) |
| [jtag-swd-mcp](https://github.com/sandraschi/jtag-swd-mcp) | Halt / inspect / flash the CPU | yes (`dbg`) |
| [oscilloscope-mcp](https://github.com/sandraschi/oscilloscope-mcp) | Scope traces — signal integrity | yes (`scope`) |
| [logic-analyzer-mcp](https://github.com/sandraschi/logic-analyzer-mcp) | Digital capture + UART/I2C/SPI decode | yes (`la`) |
| `multimeter-mcp` (here) | DMM — rails, continuity ("is it even powered?") | yes (`dmm`) |
| [power-supply-mcp](https://github.com/sandraschi/power-supply-mcp) | Bench PSU — target power | yes (`psu`) |
| [function-generator-mcp](https://github.com/sandraschi/function-generator-mcp) | AWG stimulus — clocks, reset, fault injection | yes (`fgen`) |
| [bench-camera-mcp](https://github.com/sandraschi/bench-camera-mcp) | Bench vision — LEDs, 7-segment | family (not wired) |
| [spectrum-analyzer-mcp](https://github.com/sandraschi/spectrum-analyzer-mcp) | Spectrum — EMI around the target | family (not wired) |
