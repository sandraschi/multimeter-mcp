# Multimeter MCP — System Documentation

## Overview

Multimeter MCP is a FastMCP 3.2+ server for controlling USB and serial bench multimeters. It supports real hardware via SCPI serial protocol using pyserial and an honest probe-model simulator for development, testing, and demonstration. The server follows the portmanteau pattern with three main tool groups: dmm_device for device lifecycle management, dmm_measure for taking measurements and configuring the probe model, and dmm_help for quickstart guides and tool discovery. System-level tools include health for server health checks, status for full session state, capabilities for comprehensive capability listing, and api_tool_call for REST-based tool invocation. The server exposes FastAPI web endpoints for HTTP access and mounts the FastMCP streamable HTTP transport at the /mcp path.

## Architecture

The server follows a layered architecture with clear separation of concerns. The transport layer supports both STDIO mode for Claude Desktop and HTTP streamable mode for web applications and REST API access. The presentation layer is implemented in web.py with FastAPI endpoints for health checks, session status, capability enumeration, and proxy tool invocation at POST /api/tools/{name}/call. The application layer consists of FastMCP tools defined in the tools/portmanteau/ directory, each implementing a single MCP tool with an operation discriminator parameter. The services layer manages session state, backend lifecycle, and the measurement registry which stores the last reading in memory. The backend layer abstracts hardware differences between the simulator and SCPI serial backends behind a common interface.

### REST API Endpoints

GET /health returns server identity and version. GET /api/status returns complete session state including connected device info, backend name, current DMM state with mode and probe parameters, and the last measurement reading. GET /api/capabilities returns the full server capability listing including tool surface with total tool count and names, available backends with descriptions, discovered devices with details, and runtime port configuration. POST /api/tools/{name}/call accepts a JSON body with optional arguments dict and proxies the call to the named MCP tool, returning the tool result as parsed JSON. The FastMCP endpoint is mounted at /mcp for streamable HTTP MCP communication.

### Data Models

MeasureMode is a Literal type supporting four measurement modes: dc_voltage, dc_current, resistance, and continuity. ProbeModel simulates the circuit under test with dc_voltage_v ranging from 0.0 to 1000.0 volts, dc_current_a ranging from 0.0 to 10.0 amperes, and resistance_ohm ranging from greater than 0 to 1,000,000.0 ohms. DmmState captures the current instrument configuration including the active mode, auto-ranging flag, and probe model. DeviceInfo describes a connected or available device with device_id, backend type, human-readable model name, optional serial port, connection status, capabilities, and driver status with optional hint. DeviceCapabilities specifies the backend type, supported modes list, whether SCPI is available, and optional notes.

## Tools

### health

Purpose: Quick server health check returning server name and version. No parameters required. Returns a simple JSON object with status ok, server name string, and version string. Response time is sub-millisecond as it only constructs the response object.

### status

Purpose: Full session status including connected device, backend configuration, current instrument state, and last measurement reading. No parameters required. Returns status ok, tools list (names of all registered MCP tools), version string, backend name string, connected boolean, state object with mode, range_auto, and probe parameters, and last_reading object with mode, value, and unit. If no device is connected, state is null. If no measurement has been taken, last_reading is null.

### capabilities

Purpose: Full server capability listing including tool surface enumeration, backend options with descriptions, discovered devices with full capability details, and runtime port configuration. No parameters required. Returns status ok, server identity with name and version, tool_surface with total tool count and tool names list, backends dict mapping backend name to description string, devices list with full DeviceInfo for each discoverable device, and runtime dict with backend_port and frontend_port integers.

### api_tool_call

Purpose: Call any MCP tool by name with specified arguments, proxying through the REST API. The tool exists both as an MCP tool and as a POST /api/tools/{name}/call HTTP endpoint. The name parameter specifies which tool to invoke. The arguments parameter provides the tool-specific parameters as a JSON object. The return format depends entirely on the called tool. Errors are returned as HTTP 500 with success false and message string via the REST endpoint.

### dmm_device

Purpose: Device lifecycle management for multimeter instruments. Supports five operations: list enumerates all available devices with their capabilities and connection state; connect establishes a connection to a specified device with optional backend override; disconnect terminates the current device connection; status queries the current connection state with device details and instrument status; backends lists available backend implementations and indicates which one is active.

Parameters: operation is a required Literal choosing among list, connect, disconnect, status, and backends. device_id is an optional string required only for the connect operation. backend is an optional string to override the configured backend preference when connecting.

Return Format: The list operation returns a success boolean and devices array containing DeviceInfo objects with device_id, backend, model, port, connected status, capabilities including backend, modes list, scpi boolean, and notes. The connect operation returns success and device info for the connected device. The disconnect operation returns success boolean. The status operation returns success, connected boolean, device object with full info, state object with current mode and probe configuration, and capture_dir string. The backends operation returns success, backends dict mapping names to descriptions, and active backend name.

Errors: Connect without device_id returns success false with error device_id required. Connection failures with invalid IDs return appropriate error messages. Backend resolution failures are caught and returned with descriptive messages.

### dmm_measure

Purpose: Take measurements, configure the simulator probe model, and retrieve reading results. Supports seven operations. dc_voltage sets the instrument mode to DC voltage measurement and takes an immediate reading. dc_current sets the mode to DC current measurement and reads. resistance sets the mode to resistance measurement and reads. continuity sets the mode to continuity test and reads, returning a boolean value indicating whether resistance is below 50 ohms. set_probe configures the circuit parameters on the simulator backend only, setting voltage, current, and resistance values for the virtual circuit. read takes a reading in the current mode without changing the instrument configuration. last returns the most recent reading without re-measuring.

Parameters: operation is a required Literal choosing among all seven operations. dc_voltage_v is an optional float with ge=0 constraint used only by set_probe. dc_current_a is an optional float with ge=0 constraint used only by set_probe. resistance_ohm is an optional float with gt=0 constraint used only by set_probe.

Return Format: dc_voltage, dc_current, resistance, and read all return success boolean and reading object with mode string, value float, and unit string. continuity additionally returns a unit of bool and resistance_ohm float. set_probe returns success and state object with full DmmState including mode, range_auto, and probe parameters. last returns success and reading matching the last measurement format.

Errors: set_probe on non-simulator backend returns error set_probe only available on simulator backend. last before any measurement returns error No read yet with guidance to call read first. Auto-connection failures return Not connected error with connect guidance.

### dmm_help

Purpose: Quickstart guide, tool discovery, and backend status check. Supports three operations. quickstart returns step-by-step instructions for connecting to a device and taking the first measurement. discover returns a list of all available tool names. status returns the current backend name.

Parameters: operation is a Literal with default quickstart. Valid values are quickstart, discover, and status.

Return Format: All operations return success boolean. quickstart additionally returns steps array of strings. discover returns tools array of strings. status returns backend string name.

### Resources

resource://dmm/quickstart provides a plain-text quick start guide string. resource://dmm/capabilities describes the supported backends in text format.

## Configuration

### Environment Variables

MULTIMETER_MCP_BACKEND controls the backend preference with valid values auto, simulator, and scpi_serial. The default auto setting prefers the simulator when no hardware is detected and falls back to SCPI serial when a compatible device is found. MULTIMETER_MCP_PORT sets the MCP HTTP and SSE listen port with a default of 11005. MULTIMETER_MCP_WEBAPP_PORT sets the web frontend development port with a default of 11006. MULTIMETER_MCP_WORK_DIR specifies the working data directory path with a default of ./data.

### Backends

The simulator backend is always available and provides an honest probe model that simulates a circuit under test with configurable DC voltage from 0 to 1000 volts, DC current from 0 to 10 amperes, and resistance from 0 to 1 megohm. The probe model supports set_probe for configuring circuit parameters and auto-connects when a measurement is attempted without a prior explicit connection. The SCPI serial backend provides real hardware support via pyserial, communicating with SCPI-compatible DMMs over serial ports. The COM port is system-detected and the backend requires the pyserial package to be installed.

## Security Model

No authentication is required as the server is designed for local use on 127.0.0.1. CORS middleware allows all origins to support the web dashboard from any frontend URL. Serial port access requires the OS user to have appropriate permissions. The server stores no persistent data beyond the last reading in application memory. Communication between the MCP client and server occurs over localhost only in default configurations.

## Error Handling

All portmanteau tools follow a consistent error pattern returning ToolResult objects. On success, the content dict includes success true and operation-specific fields. On failure, the content dict includes success false and an error string describing the issue. Common error messages include device_id required when connect is called without a device identifier, set_probe only available on simulator backend when trying to configure the probe on real hardware, No read yet when attempting to retrieve the last measurement before any measurement was taken, Not connected guidance when operations are attempted without an active device connection, and backend-specific error messages from hardware communication failures. The api_tool_call endpoint wraps errors in HTTP 500 responses for REST API consumers.

## Data Storage

No persistent data storage is implemented. The last reading is retained in memory via the registry module and is lost when the server process terminates. Session state including the active backend and connected device is similarly in-memory only. The work_dir configuration points to a data directory but is reserved for future persistence features.

## Version Information

Current server version is 0.2.0. The manifest declares manifest_version 0.2. The server requires Python 3.12+ and is built on FastMCP 3.2+ with Pydantic v2 models. The transport layer supports FastMCP 2.14.4+ compatibility features.

## Detailed Tool Parameter Tables

### dmm_device Operation Details

The list operation takes no additional parameters beyond the operation discriminator. It queries all registered backends for their discoverable devices and aggregates the results. The connect operation requires the device_id parameter which must match a device_id returned by a prior list call. The optional backend parameter allows overriding the configured backend preference for this specific connection, useful when multiple backends can manage the same device. The disconnect operation takes no additional parameters and cleanly shuts down the current device connection through the active backend. The status operation queries the active backend for the current connection state and device information, returning device details if connected and null device information if not connected. The backends operation returns a mapping of backend names to human-readable descriptions from all registered backends.

### dmm_measure Operation Details

Each measurement operation follows a consistent pattern of setting the measurement mode on the backend and then reading the current value. The dc_voltage operation configures the backend for DC voltage measurement by calling set_mode with the dc_voltage MeasureMode value. The dc_current operation similarly sets dc_current mode. The resistance operation sets resistance mode. The continuity operation sets continuity mode which returns a boolean value based on whether the measured resistance is below the 50 ohm threshold. The set_probe operation is exclusive to the SimulatorBackend and configures the virtual circuit parameters: dc_voltage_v sets the voltage source value in volts from 0.0 to 1000.0, dc_current_a sets the current source value in amperes from 0.0 to 10.0, resistance_ohm sets the resistive load value in ohms from 0.0 to 1,000,000.0. The read operation reads the current value from the backend without changing the measurement mode, preserving the existing configuration. The last operation returns the most recently read value from an in-memory cache without communicating with the backend.

### dmm_help Operation Details

The quickstart operation returns a predefined set of step-by-step instructions encoded as a string array in the response content. The discover operation returns the list of tool names currently registered on the MCP server. The status operation queries the session for the currently active backend name.

## Backend Compatibility Matrix

### Simulator Backend
The simulator backend supports all four measurement modes: dc_voltage, dc_current, resistance, and continuity. It supports the set_probe operation for configuring the virtual circuit under test. Auto-ranging is always enabled. SCPI protocol is not supported as this is a pure software model. The simulator always auto-connects when a measurement is attempted without an explicit connect call. Device listing always returns sim-dmm-001. Connection simulation succeeds for any device_id. Driver status is reported as available at all times.

### SCPI Serial Backend
The SCPI serial backend supports all four measurement modes when the connected hardware supports them. The set_probe operation is not available as it has no physical meaning on real hardware. Auto-ranging support depends on the specific DMM model and its SCPI command set. SCPI protocol is supported via pyserial over the configured COM port. Device listing scans available serial ports for SCPI-compatible instruments. Connection requires a valid COM port device_id and successful SCPI identification query.

## Data Flow

When a measurement operation is called, the server resolves the active backend from the session, ensuring a connection exists either from an explicit connect call or via auto-connect. The backend's set_mode method is called with the requested MeasureMode value to configure the instrument. The backend's read method is then called to obtain the current measurement value from the instrument or simulator. The reading is cached in the registry via set_last_read for retrieval by the last operation. The reading value is rounded to 6 decimal places for voltage and current readings, and 2 decimal places for resistance readings. The formatted response includes the mode identifier, numerical value, and SI unit string.

## Integration Examples

### Integration with Monitoring Systems

The REST API endpoints at /api/status and /api/capabilities provide machine-readable JSON responses suitable for integration with monitoring systems, dashboards, and automation tools. The GET /api/status endpoint returns the current measurement state including last_reading which can be polled periodically for continuous monitoring. The POST /api/tools/{name}/call endpoint allows programmatic tool invocation with JSON request bodies and responses, enabling integration with scripting languages and workflow automation tools.

### Integration with CI/CD Pipelines

The simulator backend enables automated testing of measurement workflows without hardware dependencies. CI/CD pipelines can connect to the simulator, configure probe parameters for known circuit conditions, take measurements, and assert expected values. This enables regression testing of measurement logic, automated validation of instrument control code, and integration testing with downstream systems that consume measurement data.

## Complete Error Reference

### Error: Not connected (dmm_measure)

When a measurement is attempted without an active device connection and the auto-connect mechanism fails, the server returns success false with error "Not connected. dmm_device(operation='connect', device_id='sim-dmm-001')". This occurs when the backend resolution cannot find a suitable backend. The recommended recovery is to explicitly call dmm_device with operation connect and a known device_id before retrying the measurement. The simulator device sim-dmm-001 is always available and will never fail to connect.

### Error: device_id required (dmm_device connect)

When dmm_device connect is called without providing the device_id parameter, the server returns success false with error "device_id required". This is a validation error that prevents connecting without specifying which device to target. The recommended recovery is to call dmm_device with operation list first to enumerate available devices and their identifiers, then retry the connect call with the correct device_id value.

### Error: set_probe not available on SCPI backend (dmm_measure set_probe)

When set_probe is attempted while using the SCPI serial backend, the server returns success false with error "set_probe only available on simulator backend". This is a capability restriction because set_probe configures the virtual circuit model which only exists in the simulator. Real hardware SCPI instruments cannot have their circuit parameters configured through software. The recommended recovery is to either switch to the simulator backend by reconnecting with backend set to simulator, or apply the desired voltage and current directly to the physical probe inputs on the real DMM.

### Error: No read yet (dmm_measure last)

When dmm_measure with operation last is called before any measurement has been taken, the server returns success false with error "No read yet. dmm_measure(operation='read')". The last operation retrieves the cached result of the most recent measurement operation. If no measurement has been performed, the cache is empty. The recommended recovery is to call dmm_measure with operation read to take an initial measurement, or call a mode-specific operation like dc_voltage to perform a mode change and measurement simultaneously.

### Error: Backend resolution failure (backend auto-detect)

When the server attempts to auto-resolve a backend and no backend is available, the error depends on the specific condition. If the configured backend is scpi_serial but pyserial is not installed, the backend initialization fails with an import error. If the SCPI backend is configured but no serial ports respond to the identification query, the connection attempt returns a timeout or device not found error. The recommended recovery is to verify the MULTIMETER_MCP_BACKEND environment variable is set correctly and the required dependencies are installed.

### Error: REST API HTTP 500 (api_tool_call)

When api_tool_call encounters an internal error, the REST endpoint returns HTTP status 500 with success false and message field containing the error description. This can occur when the called tool raises an unhandled exception or when the arguments cannot be deserialized. The recommended recovery is to verify the tool name is correct, the arguments are valid JSON, and the server logs show the specific error details.

## Supported SCPI Commands (Hardware Backend)

The SCPI serial backend communicates with compatible DMMs using the Standard Commands for Programmable Instrumentation protocol. Common SCPI commands include *IDN? for instrument identification query returning manufacturer, model, serial number, and firmware version. MEAS:VOLT:DC? measures DC voltage and returns the value. MEAS:CURR:DC? measures DC current. MEAS:RES? measures resistance. CONF:VOLT:DC sets the instrument to DC voltage measurement mode. CONF:CURR:DC sets DC current mode. CONF:RES sets resistance mode. SYSTem:RSOLution sets measurement resolution. INPut:IMPedance:AUTO sets input impedance. Frontend:SET? queries the current frontend configuration. The specific command set varies by manufacturer and model. Refer to the instrument's programming manual for the complete command set.


## Deployment Architecture

### Single-User Development Setup

Run the server in STDIO mode for direct connection to Claude Desktop or Cursor. The simulator backend provides full functionality without physical instruments. All tools are accessible through the MCP client interface. No network configuration is required. The server binds to stdout for JSON-RPC communication. Logging output is directed to stderr to maintain protocol integrity. For development and testing, this mode provides the fastest feedback loop with no external dependencies.

### Multi-User Lab Setup

For shared laboratory environments, run the server in HTTP streamable mode bound to the local network interface. Multiple MCP clients can connect to the same server instance through the HTTP endpoint. The server maintains a single session state shared across clients. Co-located measurement workstations can access the same backend without running separate server instances. Use firewall rules to restrict access to authorized client IP addresses.

### Production Test System

For production automated test equipment, deploy the server in HTTP mode with the SCPI serial backend connected to a calibrated DMM. The REST API endpoints provide integration with test automation frameworks (LabVIEW, Python, C#). Monitor server health via the /health endpoint. Implement client-side retry logic for transient hardware communication failures. Log all measurements with timestamps for traceability. Schedule regular calibration verification using external voltage and resistance standards.

## Logging and Diagnostics

### Log Levels

The server uses Python standard logging output to stderr in STDIO mode and to stdout in HTTP mode. The log level is set via the LOG_LEVEL environment variable or the --log-level CLI argument. DEBUG level shows all tool invocations with parameters and response data. INFO level shows server startup, device connections, and major operation boundaries. WARNING level shows recoverable errors and configuration fallbacks. ERROR level shows operation failures requiring intervention.

### Diagnostic Endpoints

The /api/status endpoint provides the complete current state including backend name, device connection status, instrument configuration, and last reading. The /api/capabilities endpoint provides the static server configuration including tool surface, backend options, and discoverable devices. Both endpoints are read-only and have no side effects. Use these endpoints for monitoring dashboards and health check automation.

### Common Diagnostic Procedures

When encountering unexpected behavior, first check the server log output for error messages. Verify the backend selection and device connection status. Test with the simulator backend to isolate hardware issues. Confirm the probe model configuration matches the expected circuit parameters. Measure known reference values (a known resistor or voltage source) to validate instrument readings.

## Compatibility Notes

### Python Version Compatibility

The server requires Python 3.12 or later due to FastMCP 3.2+ dependency requirements. Python 3.10 and 3.11 lack type features used by the Pydantic v2 models. The server has been tested with Python 3.12 and 3.13 on Windows 11 and Windows 10.

### SCPI Command Compatibility

Different DMM manufacturers implement different subsets of the SCPI standard. The server supports common commands for voltage, current, resistance, and continuity measurement. Refer to the specific instrument's programming manual for supported command set. The DeviceCapabilities scpi flag indicates whether the device supports SCPI protocol. Devices with scpi false use manufacturer-specific protocols.

### Serial Port Configuration

The SCPI serial backend communicates at the instrument's configured baud rate, data bits, stop bits, and parity. Typical configurations are 9600-115200 baud, 8 data bits, 1 stop bit, no parity. Flow control settings depend on the instrument. Configure the serial port parameters in the backend implementation if non-standard settings are required.