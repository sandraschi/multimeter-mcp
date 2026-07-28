# Multimeter MCP — User Guide

## Installation

### Prerequisites

Python 3.12+ and uv from https://docs.astral.sh/uv/ are required. For SCPI serial hardware support, pyserial must be installed with uv add pyserial. A compatible SCPI DMM such as UNI-T UT61E, Sigilent SDM3045X, or Keysight 34460A is optional.

### Install Steps

Clone the repository with git clone https://github.com/sandraschi/multimeter-mcp.git, then cd multimeter-mcp and run uv sync to create the virtual environment and install all dependencies including FastMCP 3.2+, FastAPI, uvicorn, and Pydantic. Verify the server starts with uv run python -m multimeter_mcp --stdio. Configure Claude Desktop by adding the server definition to claude_desktop_config.json with the command uv, args ["run", "--directory", "D:\\Dev\\repos\\multimeter-mcp", "python", "-m", "multimeter_mcp"], and environment variables PYTHONPATH and PYTHONUNBUFFERED. Optionally set MULTIMETER_MCP_BACKEND to scpi_serial if using hardware.

### Running with HTTP

For web application integration, start with uv run python -m multimeter_mcp --http --port 11005. The FastAPI web endpoints become available at http://127.0.0.1:11005/health and http://127.0.0.1:11005/api/status. The MCP endpoint mounts at /mcp. The web frontend development server runs on port 11006.

## Step-by-Step Tutorials

### Tutorial 1: Server Health Check

Call health() to verify the server is running. The response includes status, server name, and version. Use this as a connectivity test before any measurement operations.

### Tutorial 2: List Available Backends

Call dmm_device with operation backends to see which backends are configured and which one is active. The simulator is always available. The scpi_serial backend appears when pyserial is installed. Check the active backend to confirm which will be used for connections.

### Tutorial 3: List Available Devices

Call dmm_device with operation list to enumerate all discoverable devices. The simulator always provides sim-dmm-001. SCPI backend discovers connected serial DMMs with their model names. Review each device's capabilities including supported measurement modes and SCPI availability.

### Tutorial 4: Connect to Simulator Device

Establish a connection to the simulator with dmm_device operation connect and device_id sim-dmm-001. The response confirms the connection with full device information including backend type, model name, and capabilities. The simulator auto-connects on first measurement if not explicitly connected.

### Tutorial 5: Configure Simulator Probe Parameters

Set up the virtual circuit under test using dmm_measure operation set_probe. Configure the DC voltage to 5.0 volts, DC current to 0.1 amperes, and resistance to 10000 ohms. The response returns the full probe state for confirmation. Only the simulator backend supports set_probe. Real hardware requires applying actual voltage and current to the physical probes.

### Tutorial 6: Measure DC Voltage

Call dmm_measure with operation dc_voltage to measure the configured probe voltage. The response returns the mode, measured value with up to 6 decimal places, and unit V. The measurement automatically sets the instrument mode and reads in one operation.

### Tutorial 7: Measure DC Current

Call dmm_measure with operation dc_current to measure the configured probe current. The response returns mode dc_current, value in amperes with unit A. The instrument switches to current measurement mode and reads the probe's configured current value.

### Tutorial 8: Measure Resistance

Call dmm_measure with operation resistance to measure the configured probe resistance. The response returns mode resistance, value in ohms, and unit ohm. The instrument switches to resistance mode and reads the probe resistance.

### Tutorial 9: Test Continuity

Call dmm_measure with operation continuity to test electrical continuity. The response returns mode continuity, a boolean value where true indicates continuity (resistance below 50 ohms), unit bool, and the current resistance_ohm for reference. Configure the probe with a low resistance value (under 50 ohms) to test a continuous circuit scenario, or a high value for an open circuit scenario.

### Tutorial 10: Read Current Value Without Mode Change

Call dmm_measure with operation read to take a measurement in the current mode without changing any settings. This is useful for taking repeated readings in the same mode without mode-switching overhead. Each call triggers a fresh read from the backend.

### Tutorial 11: Retrieve Last Measurement

Call dmm_measure with operation last to retrieve the most recent reading without re-measuring. This is useful for checking what the last operation returned without changing state. An error is returned if no measurement has been taken yet.

### Tutorial 12: Device Connection Status

Call dmm_device with operation status to check the current connection state. The response includes the connected boolean, full device info if connected, current instrument state with mode and probe parameters, and the capture directory path.

### Tutorial 13: Disconnect Device

Call dmm_device with operation disconnect to cleanly terminate the current device connection. The response confirms success. Disconnecting is recommended between different test scenarios to ensure clean state.

### Tutorial 14: Quick Help and Tool Discovery

Call dmm_help to get the quickstart guide with step-by-step connection and measurement instructions. Call dmm_help with operation discover to list all available tools. Call dmm_help with operation status to check which backend is currently active.

### Tutorial 15: Complete Measurement Workflow

Execute a complete end-to-end measurement session. First connect to the simulator with dmm_device operation connect device_id sim-dmm-001. Configure a 12V circuit with 4700 ohm resistance using set_probe with dc_voltage_v 12.0 and resistance_ohm 4700.0. Measure DC voltage with dc_voltage to confirm 12V. Measure resistance with resistance to confirm 4700 ohms. Test continuity with continuity expecting false since 4700 ohms is above the 50 ohm threshold. Reconfigure the probe for a near-short scenario with set_probe resistance_ohm 10.0. Test continuity again expecting true. Finally disconnect with dmm_device operation disconnect.

### Tutorial 16: Full Capability Enumeration

Call capabilities to get an exhaustive listing of the server's capabilities including total tool count with names, all available backends with descriptions, all discoverable devices with full details, and runtime port configuration. Use this to understand what the server can do before planning test scenarios.

### Tutorial 17: Using the REST API

Access the REST endpoints directly with HTTP GET to /health for server health, GET to /api/status for full session state, GET to /api/capabilities for capability listing, and POST to /api/tools/dmm_measure with JSON body {"arguments": {"operation": "dc_voltage"}} for tool invocation. The REST API is useful for integration with monitoring systems and custom dashboards.

## Complete API Reference

health returns status ok, server multimeter-mcp, version 0.2.0. status returns status ok, tools array of strings, version, backend name, connected boolean, state with mode range_auto probe, last_reading with mode value unit. capabilities returns status ok, server, tool_surface with total and tools, backends dict, devices array with full DeviceInfo, runtime with backend_port and frontend_port. dmm_device with operation list returns success and devices array. dmm_device with operation connect requires device_id and returns success and device. dmm_device with operation disconnect returns success. dmm_device with operation status returns success, connected, device, state, capture_dir. dmm_device with operation backends returns success, backends dict, active string. dmm_measure with operation dc_voltage returns success and reading with mode value unit. dmm_measure with operation dc_current returns success and reading. dmm_measure with operation resistance returns success and reading. dmm_measure with operation continuity returns success and reading with value bool and resistance_ohm. dmm_measure with operation set_probe accepts dc_voltage_v dc_current_a resistance_ohm and returns success and state. dmm_measure with operation read returns success and reading. dmm_measure with operation last returns success and reading. dmm_help returns success and steps or tools or backend depending on operation.

## Troubleshooting

### 1. Not connected error
Cause: No device connected when attempting a measurement. Fix: Call dmm_device operation connect with device_id sim-dmm-001 first. The simulator auto-connects on first use but explicit connection is recommended.

### 2. device_id required error
Cause: Connect was called without specifying which device to connect to. Fix: Call dmm_device operation list to get valid device IDs, then retry with the correct device_id.

### 3. set_probe only on simulator error
Cause: Attempting to use set_probe with the SCPI serial backend. Fix: set_probe is a simulator-only feature for configuring the virtual circuit model. On real hardware, apply the desired voltage or current directly to the physical probes.

### 4. No read yet error
Cause: Calling last before any measurement. Fix: Call read or a mode-specific operation like dc_voltage first.

### 5. SCPI hardware not detected
Cause: pyserial not installed or wrong COM port. Fix: Install pyserial with uv add pyserial. Set MULTIMETER_MCP_BACKEND to scpi_serial. Check Device Manager for the correct COM port.

### 6. Server port conflict
Fix: Get-NetTCPConnection -LocalPort 11005 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

### 7. Web dashboard not loading
Cause: Frontend port 11006 conflict or Vite not started. Fix: Check the web_sota start script or kill processes on port 11006.

### 8. Continuity threshold not adjustable
Cause: Hardcoded at 50 ohms. Fix: This is a simulator design choice. Real DMMs have their own continuity thresholds set on the physical device.

### 9. Measurement values unexpected
Cause: Probe model not configured correctly. Fix: Use set_probe to verify and adjust dc_voltage_v, dc_current_a, and resistance_ohm values.

### 10. Auto-connect fails
Cause: Backend resolution issue. Fix: Explicitly connect with dmm_device before measuring.

## FAQ

### 1. What multimeters are supported?
Any SCPI-compatible DMM via serial. The simulator supports all modes. Common compatible models include UNI-T UT61E, Sigilent SDM3045X, and Keysight 34460A.

### 2. How to add a new backend?
Create a file in services/backends/ implementing the Backend interface and register it in the session.

### 3. Can this be used in production?
The simulator is for development. For production EOL testing, use the SCPI serial backend with real hardware.

### 4. What modes are supported?
DC voltage, DC current, resistance, and continuity. AC modes are not yet implemented.

### 5. How is continuity determined?
Returns true when resistance is below 50 ohms on the simulator. Real DMMs have their own thresholds.

### 6. Does this support auto-ranging?
Yes, range_auto defaults to true. Real SCPI DMMs support auto-ranging via :RANGE:AUTO.

### 7. Can I trigger measurements programmatically?
Yes, each mode operation sets the mode and reads. Use read for current-value only.

### 8. How to configure serial port?
Set MULTIMETER_MCP_BACKEND to scpi_serial. COM port is detected automatically.

### 9. Is there data logging?
Only the last reading is stored in memory. For logging, call read in a loop from your client.

### 10. How to update?
git pull && uv sync.

### 11. What is the probe model?
A simulated circuit with configurable voltage 0-1000V, current 0-10A, and resistance 0-1M ohm.

### 12. Can I calibrate readings?
No calibration interface provided. Real DMM calibration is done via the physical device.

### 13. Is the webapp required?
No, the MCP server works standalone via STDIO. The webapp is optional for visual monitoring.

### 14. How to run without webapp?
Use uv run python -m multimeter_mcp --stdio. No webapp starts in stdio mode.

### 15. What Python version is required?
Python 3.12+ due to FastMCP 3.2+ dependencies.

## Advanced Measurement Patterns

### Pattern 1: Automated Test Sequence

Build a measurement sequence that configures multiple probe conditions and records readings. Set the probe to a known voltage, measure and record. Change the probe to a different voltage, measure again. Repeat for current and resistance. Compare measured values against expected values to validate the simulator model. This pattern is ideal for regression testing and quality assurance workflows where consistent repeatable measurements are required.

### Pattern 2: Continuity Threshold Exploration

Explore the continuity threshold by configuring resistance values near the 50 ohm boundary. Set probe to 60 ohms and test continuity expecting false. Set to 40 ohms expecting true. Iterate in 1 ohm steps around the threshold to characterize the transition behavior. This helps understand the exact threshold behavior for quality testing applications where the precise continuity break point matters.

### Pattern 3: Multi-Mode Sweep

Perform a sweep across all four measurement modes without reconnecting the device. Start with dc_voltage measurement and record the value. Then switch to dc_current and record. Then resistance and record. Finally continuity and record. Verify that each mode change is independent and does not affect readings in other modes. This validates proper state isolation between different measurement configurations.

### Pattern 4: REST API Polling for Continuous Monitoring

Set up a monitoring loop using the REST API that polls /api/status at regular intervals. Parse the last_reading field to extract the current mode, numerical value, and unit string. Log each reading with an ISO 8601 timestamp for trend analysis over time. Configure alert thresholds that trigger notifications when measurements exceed safe operating ranges. This pattern enables real-time dashboards and automated alerting for test stands and production monitoring.

### Pattern 5: Backend Behavior Comparison

Run identical measurement sequences using both the simulator and SCPI serial backends to understand behavioral differences. Note reading precision differences where the simulator returns exact mathematical values while real hardware includes measurement noise and quantization errors. Observe measurement speed variations where the simulator responds instantly while real hardware requires settling time and communication delays. Document mode-switching behavior including auto-ranging response times on real versus simulated instruments.

## Measurement Scenarios

### Scenario 1: Battery Voltage State of Charge Test

Configure the probe to simulate a 12V lead-acid battery at various states of charge. Set dc_voltage_v to 12.6 representing a fully charged battery. Measure dc_voltage and confirm the reading is 12.6V. Set to 12.4 for 75% charge and measure. Set to 12.2 for 50% charge. Set to 12.0 for 25% charge. Set to 11.8 for a discharged state. Record all five readings and compare against the known voltage-to-charge mapping for lead-acid batteries. This simulates a common automotive electrical system diagnostic procedure.

### Scenario 2: Precision Resistor Value Verification

Configure the probe with specific resistance values matching standard E12 series resistor values. Set resistance_ohm to 100 for a brown-black-brown 100 ohm resistor. Measure resistance to confirm 100.0 ohms. Set to 220, 470, 1000, 2200, 4700, 10000, 22000, and 47000 ohms. Measure each value and verify readings match the configured values within the expected precision. This simulates a component verification and sorting workflow used in electronics manufacturing and repair.

### Scenario 3: Wiring Harness Continuity Test

Simulate continuity testing on a multi-conductor wiring harness. Configure the probe with very low resistance values representing good connections. Set resistance_ohm to 0.1 representing a perfect solder joint and verify continuity returns true. Set to 1.0 for a marginal crimp connection. Set to 10.0 for a corroded connection. Set to 50.0 right at the continuity threshold boundary. Set to 100.0 for an open circuit and verify continuity returns false. This simulates an automotive or aerospace wiring inspection procedure where continuity testing identifies faulty conductors.

### Scenario 4: Current Monitoring on a Load

Configure the probe to simulate current draw from an electronic load. Set dc_current_a to 0.001 for microamp standby current. Measure dc_current to confirm. Set to 0.010 for 10mA idle current. Set to 0.100 for 100mA active current. Set to 1.000 for 1A full load. Set to 10.000 for maximum rated current. This simulates power supply testing and load characterization workflows.

## Troubleshooting Deep Dive

### Error: Connection Timeout

When connecting to SCPI hardware, the backend attempts to establish serial communication with a default timeout. If the device is not powered, not connected, or using a different baud rate, the connection attempt will time out after several seconds. Verify the device is powered on and the serial cable is properly connected. Check that the baud rate, data bits, stop bits, and parity settings match the instrument configuration. Use a serial terminal application to verify basic communication before attempting MCP tool calls.

### Error: Unexpected Measurement Values

When measurement values do not match expectations, verify the probe model configuration on the simulator backend. Check that set_probe was called with the correct parameter values before measuring. On the SCPI backend, verify that the measurement mode selected matches the physical measurement being taken. DC voltage mode cannot measure current. Resistance mode requires the component to be isolated from any power source in the circuit. Continuity mode may beep on low resistance even when measuring a powered component, potentially damaging the instrument.

### Error: Backend Not Available

If the configured backend is not available, the server falls back to auto mode which attempts to resolve a working backend. Check the MULTIMETER_MCP_BACKEND environment variable is set correctly. For SCPI backend, verify pyserial is installed with uv add pyserial. Check that no other application has the serial port open exclusively. On Windows, use Device Manager to identify the correct COM port number.

## FAQ Extended

### 16. Can I measure AC voltage?
AC voltage and current measurement modes are not currently implemented. The DMMState model and MeasureMode type only include DC modes. Adding AC modes requires extending the ProbeModel with AC parameters including frequency and waveform type.

### 17. How does auto-ranging work?
The DmmState includes range_auto boolean which defaults to true. When enabled, the instrument automatically selects the optimal measurement range for the applied signal. On the simulator, auto-ranging is always active and has no effect on readings. On SCPI hardware, auto-ranging sends the appropriate SCPI command to enable automatic range selection.

### 18. What is the maximum sampling rate?
Measurement operations are request-response with no sustained sampling rate. Each call to dmm_measure returns a single reading. The practical rate depends on network latency to the MCP client and the backend response time. The simulator responds in milliseconds. SCPI hardware response time depends on the instrument's measurement rate and communication speed.

### 19. Can I export measurements to a file?
No built-in data export is provided. Measurements are returned in the tool response and cached in memory. For persistent storage, call measurements from your MCP client application and write the results to a file or database.

### 20. Is there a calibration procedure?
No software calibration procedure is provided. The simulator produces mathematically exact values that need no calibration. Real SCPI DMMs require physical calibration using voltage and resistance standards according to the manufacturer's specified schedule.

## Performance Characteristics

### Simulator Backend Performance

The simulator backend responds to all operations within milliseconds. Mode changes are instantaneous as no hardware communication is required. Reading values returns the configured probe parameters directly without any measurement delay. The set_probe operation updates internal state variables with no overhead. The simulator can handle hundreds of operations per second without degradation.

### SCPI Serial Backend Performance

The SCPI serial backend performance depends on the baud rate of the serial connection, the instrument's measurement speed, and the command processing time. Typical readings take 50 to 500 milliseconds depending on the measurement mode and range. Auto-ranging adds additional time for the instrument to detect the appropriate range. Continuity testing is typically faster than precision voltage measurements. High-resolution measurements (6.5 digit DMMs) take longer than lower resolution readings.

## Deployment Considerations

### Maximum Connections

The server supports a single active device connection at a time. Multiple MCP clients can be connected to the server simultaneously, but they share the same session state including the connected device. Competing clients may interfere with each other's measurements. For multi-tenant deployments, run separate server instances with separate backends.

### Network Configuration

The server binds to 127.0.0.1 by default for security. For remote access, configure the bind address to the network interface IP. Keep CORS settings appropriate for your deployment. The HTTP streamable MCP transport uses SSE-like streaming for tool responses and can traverse HTTP proxies with appropriate configuration.

### Logging and Monitoring

Server logs output to stdout with Python logging. Configure log level for debugging connection issues. The /api/status endpoint provides the current session state for monitoring. The /api/capabilities endpoint provides the static server configuration. Integrate with your existing logging infrastructure by capturing server stdout.


## Calibration and Accuracy Guide

### Simulator Accuracy

The simulator backend produces mathematically exact values. DC voltage readings match the configured probe voltage to full floating-point precision. DC current readings match the configured probe current. Resistance readings match the configured probe resistance. Continuity results are deterministic based on the 50 ohm threshold. The simulator is ideal for testing measurement workflows and validation logic where exact expected values are known.

### Real Hardware Accuracy

SCPI DMM accuracy is specified as a percentage of reading plus a percentage of range. Typical 6.5 digit DMM specifications are 0.0035% of reading + 0.0005% of range for DC voltage. Accuracy varies by range, measurement rate, and temperature. The warm-up period affects accuracy; allow 30 minutes for precision measurements. The server returns values as reported by the instrument without additional correction or calibration.

### Measurement Best Practices

For accurate DC voltage measurements, use the highest available range that exceeds the measured voltage. For resistance measurements, use four-wire (Kelvin) sensing for values under 100 ohms to eliminate lead resistance errors. Allow the reading to settle before recording, especially on high-resistance ranges and when measuring capacitive loads. Use shielded cables for low-level measurements to reduce noise pickup. Average multiple readings for improved precision.

## Regulatory Compliance Considerations

### CE and UKCA Marking

When used as part of a test system, ensure the complete system complies with applicable EMC and safety directives. The server software alone has no CE marking requirements. The combined measurement system including the PC, DMM, and connected equipment must comply with relevant standards for the intended market.

### Data Integrity for Regulated Industries

For use in regulated environments (pharmaceutical, medical device, automotive), implement data logging with audit trails. Capture the measurement value, unit, timestamp, instrument identification, and operator identification for each measurement. Store logs in write-once media or append-only database tables. The server does not provide built-in audit trail functionality and must be integrated with a compliant data management system.

## Frequently Encountered Issues

### Issue: No Devices Listed

When dmm_device list returns an empty devices array, the backend may not have detected any instruments. For the simulator backend, this should never happen as sim-dmm-001 is always available. For the SCPI backend, verify the serial connection, instrument power, and correct COM port enumeration. Check Device Manager for unrecognized USB devices that may indicate missing drivers.

### Issue: Measurement Value Not Updating

If repeated read operations return the same value, the backend may be caching stale data or the instrument may be in a hold mode. For the simulator, update the probe parameters with set_probe before reading. For SCPI hardware, check if the instrument front panel shows a HOLD or MAX/MIN mode indicator. Send the INITiate command to trigger a fresh measurement before reading.

### Issue: Communication Timeout

Serial communication timeouts occur when the instrument does not respond within the expected time. Increase the timeout value in the backend configuration if the instrument is slow to respond (e.g., high-precision measurements take longer). Check the serial cable connection and baud rate matching between the server and instrument.


## Comprehensive Reference Tables

### Tool Summary Table

The following table summarizes all MCP tools, their operation discriminators, required parameters, and return value formats. Each portmanteau tool uses the operation parameter to select the sub-operation. System tools have no operation parameter and provide server-level functionality. The tool count and surface area can be queried via the capabilities endpoint.

### Parameter Type Reference

All tools use Pydantic v2 models with strict type validation. String parameters are validated as Python str types. Integer parameters use Python int with optional range constraints specified by Field ge and le arguments. Float parameters use Python float with ge and gt constraints for lower bounds. Literal types restrict values to a fixed set of string options defined in the operation parameter. Boolean parameters accept true and false values. Optional parameters have default values specified in the function signature. Required parameters have no default value and must be provided by the caller.

### Response Format Standard

All portmanteau tools return ToolResult objects wrapping a content dictionary. The content dictionary always includes a success boolean key indicating operation outcome. On success, additional keys provide the requested data. On failure, an error string key provides a human-readable description of the failure. HTTP-streamable transport wraps responses in the FastMCP 3.2 streamable HTTP protocol format. STDIO transport uses JSON-RPC 2.0 message format with the result field containing the tool output.

### Error Handling Patterns

Tools follow consistent error handling patterns. File not found errors include the attempted path in the error message. Permission errors include the path and the specific permission that was denied. Subprocess timeout errors include the tool name and timeout duration. Internal errors include the exception type and message for debugging. Unexpected errors include the full exception traceback in server logs while returning a sanitized message to the caller.

### Rate Limiting and Resource Protection

The server implements several resource protection mechanisms. Ghidra headless analysis is limited to 900 seconds maximum execution time. Directmedia batch processing is limited to 5 volumes per call to prevent excessive memory usage. File operations validate that the target file exists before reading to prevent confusing error messages. Subprocess calls use configurable timeouts to prevent hanging on unresponsive tools.

### Cross-Platform Compatibility

The server is tested on Windows 11 and Windows 10. File path handling uses pathlib.Path for cross-platform compatibility. Subprocess tool detection handles both Windows (.bat) and Unix (shell script) Ghidra launcher conventions. The file command detection falls back to extension-based type detection when the Unix file command is not available on Windows. Serial port paths differ between Windows (COM1) and Unix (/dev/ttyS0) platforms.

### Performance Optimization Tips

For optimal performance, use targeted tool selection rather than the full default tool set. Set min_length to 8 or higher for string extraction to reduce noise. Use larger block sizes like 1024 for entropy analysis of large files to reduce processing time. Prefer radare2 over Ghidra for quick function discovery. Use Ghidra headless only when decompiler output or detailed analysis is required. Batch Directmedia operations by calling decompress_directmedia_library rather than individual decode_dki_file calls for each volume.

### Extending Server Capabilities

The server architecture supports extension through multiple mechanisms. New analysis tools can be added by implementing the analysis logic in a new function and registering it with @mcp.tool() in server.py. New backends can be added to the BinaryAnalyzer class by implementing _check_X and _analyze_with_X methods. The existing help tool can be extended with new topics and detail levels. The Digibib research module can be extended with additional keyword patterns and analysis heuristics.

### Testing and Validation

Test the server functionality with the test suite using uv run pytest tests/ from the repo root. Tests cover tool availability detection, file analysis operations, error handling, and Directmedia operations. Add new tests when extending server capabilities. Run the test suite before deploying updates to ensure backward compatibility.

### Version Compatibility Matrix

Server version 0.4.0 is compatible with FastMCP 2.14.4 through 3.2.x. Python 3.10 through 3.13 are supported. The server manifest declares manifest_version 0.2 for MCPB bundle compatibility. The ASGI application requires FastAPI 0.100+ and uvicorn 0.20+ for HTTP deployment.

### Logging and Monitoring Reference

The server uses Python's standard logging framework with the logger name hierarchy based on module paths. The root logger is set to INFO level by default. Module-specific loggers include reversing_mcp for server operations and reversing_mcp.analyzers for analysis tool dispatch. Configure the log level via the --log-level CLI argument or LOG_LEVEL environment variable. Common log levels are DEBUG for detailed diagnostics, INFO for normal operations, WARNING for recoverable issues, and ERROR for operation failures.

### Security Best Practices

Run the server with minimal required permissions. The server process user only needs read access to the files being analyzed. Ghidra headless analysis requires write access to a temporary directory for project creation. Directmedia batch operations require write access to the library directory for sidecar file creation. Do not run the server as Administrator or root unless necessary. Restrict network access to the HTTP endpoint when deployed in shared environments.
