from fastmcp import FastMCP

mcp = FastMCP(
    "MultimeterMCP",
    instructions=(
        "USB/serial bench multimeters — SCPI serial + honest probe-model simulator. "
        "Portmanteau: dmm_device, dmm_measure, dmm_help."
    ),
    on_duplicate="replace",
)

@mcp.resource("resource://dmm/quickstart")
def quickstart() -> str:
    return (
        "1. dmm_device(operation='connect', device_id='sim-dmm-001') "
        "2. dmm_measure(operation='set_probe', dc_voltage_v=5.0) "
        "3. dmm_measure(operation='dc_voltage')"
    )

@mcp.resource("resource://dmm/capabilities")
def capabilities() -> str:
    return "# multimeter-mcp\nBackends: simulator (probe model), scpi_serial (pyserial + SCPI DMM)."
