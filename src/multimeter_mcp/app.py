from fastmcp import FastMCP

mcp = FastMCP(
    "MultimeterMCP",
    instructions="USB/serial bench multimeters and simulator. Portmanteau: dmm_device, dmm_run, dmm_help.",
    on_duplicate="replace",
)

@mcp.resource("resource://dmm/quickstart")
def quickstart() -> str:
    return "1. dmm_device(operation='connect') 2. dmm_run(operation='dc_voltage')"

@mcp.resource("resource://dmm/capabilities")
def capabilities() -> str:
    return "# multimeter-mcp\nSimulator + planned hardware backends."
