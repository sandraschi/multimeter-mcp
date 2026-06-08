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

## Fleet

Part of the Sandra bench MCP family with oscilloscope-mcp and logic-analyzer-mcp.
