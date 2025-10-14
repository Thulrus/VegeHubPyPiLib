# Integration Testing Guide

## Overview

The `integration_test.py` script provides comprehensive testing of the VegeHub library against real hardware devices. Unlike unit tests that use mocked responses, these tests communicate with actual VegeHub devices on your local network.

## Features

### Automatic Device Discovery

The test uses mDNS (multicast DNS) to automatically discover VegeHub devices on your network:

- Scans for devices advertising the `_vege._tcp.local.` service
- Lists all discovered devices with their IP addresses
- Lets you choose which device to test

### Interactive Safety Controls

- **Device Selection**: Choose which VegeHub to test
- **Actuator Testing**: Optional - you can skip actuator tests if they would cause problems
- **Confirmation Prompts**: Review test configuration before proceeding

### Comprehensive Test Coverage

The integration tests cover:

1. **Basic Properties** - IP address and URL generation
2. **MAC Address Retrieval** - Network communication and data parsing
3. **Device Info Updates** - Fetching hub configuration and status
4. **Property Accessors** - All device property getters
5. **Actuator States** - Retrieving actuator status information
6. **Actuator Control** (optional) - Sending commands (with safe parameters)
7. **Configuration Access** - Reading device configuration
8. **Error Handling** - Connection timeout and error conditions

## Prerequisites

1. **VegeHub Device**: A physical VegeHub device on the same network
2. **Network Access**: The computer running tests must be on the same local network
3. **Dependencies**: The `zeroconf` package (installed with `poetry install`)

## Running the Tests

### Method 1: Command Line

```bash
poetry run python integration_test.py
```

### Method 2: VS Code Task

1. Open Command Palette (Ctrl+Shift+P or Cmd+Shift+P)
2. Select "Tasks: Run Task"
3. Choose "Run Integration Tests"

## Test Workflow

1. **Discovery Phase** (5 seconds)
   - Scans network for VegeHub devices
   - Displays all found devices

2. **Device Selection**
   - Choose which device to test from the list
   - Option to quit if no suitable device found

3. **Configuration**
   - Choose whether to test actuator functionality
   - Review test configuration
   - Confirm to proceed

4. **Test Execution**
   - Runs 8 comprehensive tests
   - Displays real-time progress with ✅/❌/⏭️ indicators
   - Shows detailed information about each test

5. **Results Summary**
   - Total tests run
   - Pass/Fail/Skip counts
   - Final status

## Safety Features

### Safe Actuator Testing

If you choose to test actuators, the script uses the safest possible parameters:
- `state=0` (off state)
- `duration=0` (no duration)
- `slot=0` (first actuator only)

This minimizes the chance of unintended activation, but you should still:
- Only test when it's safe to do so
- Know what's connected to your actuators
- Be prepared to manually intervene if needed

### Non-Destructive Tests

Most tests are read-only:
- Device info retrieval
- MAC address lookup
- Configuration reading
- Status checks

The only potentially state-changing operations are:
- Actuator control (optional, can be skipped)

## Understanding Test Results

### Success (✅)

```
✅ Retrieve MAC address: MAC: AABBCCDDEEFF
```

The test passed and retrieved the expected data.

### Failure (❌)

```
❌ Request update: Failed to get device info
```

The test encountered an error. Check:
- Network connectivity
- Device is powered on
- Device firmware version compatibility

### Skipped (⏭️)

```
⏭️ Actuator control: User chose not to test actuators
```

The test was intentionally skipped.

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed
- `130`: Tests interrupted by user (Ctrl+C)

## Troubleshooting

### No Devices Found

**Symptoms**: "No VegeHub devices found on the network"

**Solutions**:
- Verify VegeHub is powered on
- Check both devices are on the same network
- Wait a few seconds for device to boot
- Temporarily disable firewall/VPN
- Check that mDNS is working on your network

### Connection Errors

**Symptoms**: "Connection error" or timeout messages

**Solutions**:
- Verify IP address is correct
- Check network connectivity with `ping <ip>`
- Ensure no firewall blocking port 80
- Try running tests from a different machine

### Import Errors

**Symptoms**: "Import 'zeroconf' could not be resolved"

**Solutions**:
```bash
poetry install
```

## Integration with CI/CD

These tests are **not** suitable for automated CI/CD pipelines because they require:
- Physical hardware access
- Local network connectivity
- Manual intervention

Keep your unit tests (in `tests/`) for automated testing. Use integration tests for:
- Manual verification before releases
- Testing on actual hardware
- Validating new firmware versions
- Debugging real-world issues

## Adding More Tests

To add additional test cases to the integration suite:

1. Open `integration_test.py`
2. Find the `run_integration_tests()` function
3. Add your test following this pattern:

```python
# Test N: Your Test Name
print("\n📋 Test N: Your Test Name")
try:
    # Your test code here
    result = await hub.your_method()
    if result:
        results.test_pass("Your test name", "Success details")
    else:
        results.test_fail("Your test name", "Failure reason")
except Exception as e:
    results.test_fail("Your test name", str(e))
```

## Comparison with Unit Tests

| Aspect | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| Speed | Fast (seconds) | Slower (device I/O) |
| Hardware | Not required | Required |
| Isolation | Fully mocked | Real network calls |
| CI/CD | Automated | Manual only |
| Coverage | Code paths | Real-world behavior |
| Reliability | Always same | Network dependent |

**Use both**: Unit tests for development and CI/CD, integration tests for hardware validation.
