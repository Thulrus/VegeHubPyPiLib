# Vegetronix VegeHub

This package is intended to simplify interactions with the [Vegetronix VegeHub](https://www.vegetronix.com/Products/VG-HUB-RELAY/). It allows remote setup of the API key and target server address, as well as simplifying retrieval of information about the Hub, including its MAC address.

This package was written for use with the VegeHub integration for [Home Assistant](https://www.home-assistant.io/), but may be used in other projects as well.

Development on this library was done using Python Poetry for dependency management and building/publishing. Find more info about how to use it [here](https://python-poetry.org/docs/basic-usage/).

## Development

### Running Unit Tests

The library includes comprehensive unit tests that use mocked HTTP responses:

```bash
poetry run pytest
```

### Running Integration Tests

Integration tests are available to test the library against real VegeHub devices on your local network. These tests:

- Automatically discover VegeHub devices using mDNS
- Allow you to select which device to test
- Optionally test actuator functionality (with safety warnings)
- Cover all major library features

To run integration tests:

1. Install the optional test dependency:

   ```bash
   poetry install  # zeroconf is included in dev dependencies
   ```

2. Ensure your VegeHub device is powered on and connected to the same network

3. Run the integration test script:

   ```bash
   poetry run python integration_test.py
   ```

4. Or use the VS Code task: **Terminal > Run Task > Run Integration Tests**

The integration tests will:

- Scan for VegeHub devices on your network
- Let you choose which device to test
- Ask if you want to test actuator control (optional)
- Run comprehensive tests covering all library functionality
- Provide a detailed report of test results

**Note:** Integration tests are separate from unit tests and require physical hardware. They are designed to be run manually when you have access to a VegeHub device.

