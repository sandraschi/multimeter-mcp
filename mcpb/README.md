# multimeter-mcp (MCPB Bundle)

FastMCP 3.2+ — USB/serial bench multimeters and honest probe-model simulator.

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "multimeter-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "multimeter_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **health**: health
- **status**: status
- **capabilities**: capabilities
- **api_tool_call**: api_tool_call
- **dmm_device**: dmm_device
- **dmm_device_list**: dmm_device(list)
- **dmm_device_connect**: dmm_device(connect)
- **dmm_device_disconnect**: dmm_device(disconnect)
- **dmm_device_status**: dmm_device(status)
- **dmm_device_backends**: dmm_device(backends)
- **dmm_help**: dmm_help
- **dmm_help_quickstart**: dmm_help(quickstart)
- **dmm_help_discover**: dmm_help(discover)
- **dmm_help_status**: dmm_help(status)
- **dmm_measure**: dmm_measure
- **dmm_measure_dc_voltage**: dmm_measure(dc_voltage)
- **dmm_measure_dc_current**: dmm_measure(dc_current)
- **dmm_measure_resistance**: dmm_measure(resistance)
- **dmm_measure_continuity**: dmm_measure(continuity)
- **dmm_measure_set_probe**: dmm_measure(set_probe)
- **dmm_measure_read**: dmm_measure(read)
- **dmm_measure_last**: dmm_measure(last)

## Requirements

- Python 3.12+
- uv
