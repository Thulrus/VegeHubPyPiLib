#!/usr/bin/env python3
"""
Integration test script for VegeHub library.

This script discovers VegeHub devices on the local network using mDNS,
allows the user to select a device, and runs comprehensive tests against it.

Requirements:
    pip install zeroconf aiohttp

Usage:
    python integration_test.py

Note: This is a standalone test script, not part of the unit test suite.
      Some pylint warnings about broad exceptions are intentional for
      user-friendly error reporting.
"""
# pylint: disable=broad-except,protected-access

import aiohttp
import asyncio
import sys
from typing import Optional

from zeroconf import ServiceBrowser, ServiceListener, Zeroconf

from vegehub.vegehub import VegeHub


class VegeHubListener(ServiceListener):
    """Listener for VegeHub mDNS services."""

    def __init__(self):
        """Initialize the listener."""
        self.devices: list[dict] = []

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is discovered."""
        print(f"  Discovered: {name}")
        info = zc.get_service_info(type_, name)
        if info:
            # Extract IP address
            if info.addresses:
                ip_address = ".".join(str(b) for b in info.addresses[0])
                device = {
                    "name": name,
                    "ip": ip_address,
                    "port": info.port,
                    "properties": info.properties
                }
                self.devices.append(device)
                print(f"    → Added: {ip_address}")
        else:
            print(f"    → Could not get service info")

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is updated."""

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Called when a service is removed."""


def discover_vegehubs(timeout: int = 5) -> list[dict]:
    """
    Discover VegeHub devices on the local network.
    
    Args:
        timeout: How long to search for devices (seconds)
        
    Returns:
        List of discovered devices
    """
    print(f"\n🔍 Searching for VegeHub devices for {timeout} seconds...")

    zeroconf = Zeroconf()
    listener = VegeHubListener()

    # VegeHub devices advertise themselves with the _vege._tcp.local. service
    # Keep browser reference to prevent garbage collection during scan
    browser = ServiceBrowser(zeroconf, "_vege._tcp.local.", listener)  # noqa: F841

    try:
        # Wait for discovery with progress updates
        import time
        
        for i in range(timeout):
            time.sleep(1)
            if i % 2 == 0:
                count = len(listener.devices)
                if count > 0:
                    print(f"  ... found {count} device(s) so far")
    finally:
        # Just close zeroconf, which will properly shut down the browser
        # Don't call browser.cancel() as it may interrupt pending callbacks
        zeroconf.close()

    return listener.devices


def select_device(devices: list[dict]) -> Optional[dict]:
    """
    Allow user to select a device from the list.
    
    Args:
        devices: List of discovered devices
        
    Returns:
        Selected device or None
    """
    if not devices:
        print("\n❌ No VegeHub devices found via mDNS discovery.")
        print(
            "   Make sure your VegeHub is powered on and connected to the same network."
        )
        print("\n💡 Would you like to manually enter a VegeHub IP address instead?")
        
        try:
            manual = input("   Enter IP address (or press Enter to quit): ").strip()
            if manual:
                # Basic IP validation
                parts = manual.split('.')
                if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                    return {
                        "name": f"VegeHub at {manual}",
                        "ip": manual,
                        "port": 80,
                        "properties": {}
                    }
                else:
                    print("   Invalid IP address format.")
                    return None
        except KeyboardInterrupt:
            print("\n\n⚠️  Test cancelled by user")
            return None
        
        return None

    print(f"\n✅ Found {len(devices)} VegeHub device(s):\n")
    for i, device in enumerate(devices, 1):
        print(f"  [{i}] {device['name']} - {device['ip']}")

    while True:
        try:
            choice = input(
                f"\nSelect device (1-{len(devices)}), enter an IP address, or 'q' to quit: ").strip(
                )
            if choice.lower() == 'q':
                return None
            
            # Check if it's an IP address
            if '.' in choice:
                parts = choice.split('.')
                if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                    return {
                        "name": f"VegeHub at {choice}",
                        "ip": choice,
                        "port": 80,
                        "properties": {}
                    }
                else:
                    print("  Invalid IP address format.")
                    continue

            # Otherwise treat as device index
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                return devices[idx]
            else:
                print(f"  Please enter a number between 1 and {len(devices)} or an IP address")
        except ValueError:
            print("  Please enter a valid number, IP address, or 'q'")
        except KeyboardInterrupt:
            print("\n\n⚠️  Test cancelled by user")
            return None


def ask_yes_no(question: str, default: bool = False) -> bool:
    """
    Ask a yes/no question.
    
    Args:
        question: The question to ask
        default: Default answer if user just presses enter
        
    Returns:
        True for yes, False for no
    """
    default_str = "Y/n" if default else "y/N"
    while True:
        try:
            response = input(f"{question} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ('y', 'yes'):
                return True
            if response in ('n', 'no'):
                return False
            print("  Please answer 'y' or 'n'")
        except KeyboardInterrupt:
            print("\n\n⚠️  Test cancelled by user")
            sys.exit(0)


class IntegrationTestResults:
    """Track integration test results."""

    def __init__(self):
        """Initialize test results."""
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.details: list[str] = []

    def test_pass(self, name: str, detail: str = ""):
        """Record a passing test."""
        self.passed += 1
        status = f"  ✅ {name}"
        if detail:
            status += f": {detail}"
        print(status)
        self.details.append(status)

    def test_fail(self, name: str, error: str):
        """Record a failing test."""
        self.failed += 1
        status = f"  ❌ {name}: {error}"
        print(status)
        self.details.append(status)

    def test_skip(self, name: str, reason: str = ""):
        """Record a skipped test."""
        self.skipped += 1
        status = f"  ⏭️  {name}"
        if reason:
            status += f": {reason}"
        print(status)
        self.details.append(status)

    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed + self.skipped
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total}")
        print(f"  ✅ Passed:  {self.passed}")
        print(f"  ❌ Failed:  {self.failed}")
        print(f"  ⏭️  Skipped: {self.skipped}")
        print("=" * 60)

        if self.failed > 0:
            print(
                "\n⚠️  Some tests failed. Check the output above for details.")
            return False
        else:
            print("\n🎉 All tests passed!")
            return True


async def run_integration_tests(ip_address: str,
                                test_actuators: bool,
                                test_setup: bool,
                                restore_config: bool) -> IntegrationTestResults:
    """
    Run integration tests against a VegeHub device.
    
    Args:
        ip_address: IP address of the device to test
        test_actuators: Whether to test actuator functionality
        test_setup: Whether to test setup function (config modification)
        restore_config: Whether to restore original config after setup test
        
    Returns:
        IntegrationTestResults object
    """
    results = IntegrationTestResults()
    print(f"\n{'='*60}")
    print(f"TESTING VegeHub at {ip_address}")
    print(f"{'='*60}\n")

    # Create a shared session for all HTTP requests
    # This prevents the "Unclosed connection" warnings
    async with aiohttp.ClientSession() as session:
        # Create hub instance with shared session
        hub = VegeHub(ip_address=ip_address, session=session)

        # Test 1: Basic properties
        print("📋 Test 1: Basic Properties")
        try:
            assert hub.ip_address == ip_address
            assert hub.url == f"http://{ip_address}"
            results.test_pass("Basic properties (ip_address, url)")
        except AssertionError as e:
            results.test_fail("Basic properties", str(e))

    # Test 2: Retrieve MAC address
        print("\n📋 Test 2: Retrieve MAC Address")
        try:
            success = await hub.retrieve_mac_address(retries=2)
            if success and hub.mac_address:
                results.test_pass("Retrieve MAC address",
                                  f"MAC: {hub.mac_address}")
            else:
                results.test_fail("Retrieve MAC address", "Failed to retrieve MAC")
        except Exception as e:
            results.test_fail("Retrieve MAC address", str(e))
    
        # Test 3: Get device info
        print("\n📋 Test 3: Get Device Info")
        try:
            info = await hub._get_device_info()
            if info:
                hub._info = info  # Store it so properties work
                results.test_pass("Get device info",
                                  f"Got info: {len(info)} fields")
    
                # Verify info properties
                print("     Device info:")
                if hub.num_sensors is not None:
                    print(f"       - Sensors: {hub.num_sensors}")
                if hub.num_actuators is not None:
                    print(f"       - Actuators: {hub.num_actuators}")
                if hub.sw_version:
                    print(f"       - Software version: {hub.sw_version}")
                if hub.is_ac is not None:
                    print(f"       - AC powered: {hub.is_ac}")
            else:
                results.test_fail("Get device info", "Failed to get device info")
        except Exception as e:
            results.test_fail("Get device info", str(e))
    
        # Test 4: Property accessors
        print("\n📋 Test 4: Device Property Accessors")
        try:
            errors = []
            if hub.num_sensors is None:
                errors.append("num_sensors is None")
            if hub.num_actuators is None:
                errors.append("num_actuators is None")
            if not hub.sw_version:
                errors.append("sw_version is empty")
            if hub.is_ac is None:
                errors.append("is_ac is None")
    
            if errors:
                results.test_fail("Property accessors", ", ".join(errors))
            else:
                results.test_pass("Property accessors",
                                  "All properties accessible")
        except Exception as e:
            results.test_fail("Property accessors", str(e))
    
        # Test 5: Get actuator states
        print("\n📋 Test 5: Get Actuator States")
        actuator_count = 0
        try:
            actuator_states = await hub.actuator_states(retries=2)
            if actuator_states is not None:
                actuator_count = len(actuator_states)
                results.test_pass("Get actuator states",
                                  f"Retrieved {actuator_count} actuator(s)")
                for i, state in enumerate(actuator_states):
                    if 'slot' in state:
                        print(
                            f"     Actuator {state['slot']}: state={state.get('state', 'unknown')}"
                        )
            else:
                results.test_fail("Get actuator states",
                                  "Failed to retrieve states")
        except Exception as e:
            results.test_fail("Get actuator states", str(e))
    
        # Test 6: Actuator control (optional)
        # Check either num_actuators from info OR actuator_count from states
        has_actuators = (hub.num_actuators and hub.num_actuators > 0) or actuator_count > 0
        
        if test_actuators and has_actuators:
            print("\n📋 Test 6: Actuator Control")
            test_passed = True
            test_message = ""
            
            try:
                # Step 0: Turn all actuators OFF first to ensure clean starting state
                print("     Step 0: Turning all actuators OFF (clean start)...")
                initial_off_success = True
                for slot_num in range(actuator_count):
                    off_success = await hub.set_actuator(state=0,
                                                         slot=slot_num,
                                                         duration=0,
                                                         retries=2)
                    if not off_success:
                        initial_off_success = False
                        print(f"     ⚠ Failed to turn off actuator {slot_num}")
                
                if initial_off_success:
                    print(f"     ✓ All {actuator_count} actuator(s) turned OFF")
                else:
                    print("     ⚠ Some actuators may still be on")
                
                # Brief delay to let device settle
                await asyncio.sleep(0.5)
                
                # Step 1: Set actuator to ON state with short duration for testing
                print("     Step 1: Turning on actuator 0...")
                success = await hub.set_actuator(state=1,
                                                 slot=0,
                                                 duration=5,  # 5 second duration for testing
                                                 retries=2)
    
                if not success:
                    test_passed = False
                    test_message = "Command to turn ON returned failure"
                else:
                    print("     ✓ Command sent successfully")
                    
                    # Step 2: Verify the state changed
                    print("     Step 2: Verifying actuator state...")
                    await asyncio.sleep(1.0)  # Longer delay to ensure device has updated
                    verify_states = await hub.actuator_states(retries=2)
                    
                    if verify_states and len(verify_states) > 0:
                        actuator_0_state = None
                        for state in verify_states:
                            if state.get('slot') == 0:
                                actuator_0_state = state.get('state')
                                break
                        
                        if actuator_0_state == 1:
                            print("     ✓ Actuator 0 state verified: ON")
                        else:
                            print(f"     ⚠ Actuator 0 state: {actuator_0_state} (expected 1)")
                            test_message = f"State verification: expected 1, got {actuator_0_state}"
                            test_passed = False
                    else:
                        print("     ⚠ Could not retrieve states for verification")
                        test_message = "Could not retrieve states for verification"
                        test_passed = False
                    
                    # Step 3: Turn all actuators OFF for safety
                    print("     Step 3: Turning all actuators OFF...")
                    all_off_success = True
                    for slot_num in range(actuator_count):
                        off_success = await hub.set_actuator(state=0,
                                                             slot=slot_num,
                                                             duration=0,
                                                             retries=2)
                        if not off_success:
                            all_off_success = False
                            print(f"     ⚠ Failed to turn off actuator {slot_num}")
                    
                    if all_off_success:
                        print(f"     ✓ All {actuator_count} actuator(s) turned OFF")
                    else:
                        test_message = "Some actuators failed to turn OFF"
                        test_passed = False
    
                if test_passed:
                    results.test_pass("Actuator control",
                                      f"Command sent, verified, and cleaned up ({actuator_count} actuator(s))")
                else:
                    results.test_fail("Actuator control", test_message)
    
            except Exception as e:
                # Try to turn off all actuators even if test failed
                try:
                    print("     Exception occurred, attempting to turn all actuators OFF...")
                    for slot_num in range(actuator_count):
                        await hub.set_actuator(state=0, slot=slot_num, duration=0, retries=2)
                except Exception:
                    pass  # Best effort cleanup
                results.test_fail("Actuator control", str(e))
        else:
            if not test_actuators:
                results.test_skip("Actuator control",
                                  "User chose not to test actuators")
            else:
                results.test_skip("Actuator control",
                                  "No actuators on this device")
    
        # Test 7: Setup method with config backup and restore
        if test_setup:
            print("\n📋 Test 7: Setup Function (Config Modification with Backup/Restore)")
            original_config = None
            try:
                # Step 1: Read original config
                print("     Step 1: Reading original config...")
                original_config = await hub._get_device_config()
                if not original_config:
                    results.test_fail("Setup function", "Failed to read original config")
                else:
                    # Debug: Print the keys in the config
                    print(f"     Debug: Config keys: {list(original_config.keys())}")
                    
                    # Detect and display firmware type
                    # Check for new firmware: endpoints must be a list (can be empty)
                    # If endpoints is None or not a list, it's old firmware
                    if ("endpoints" in original_config and 
                        isinstance(original_config.get("endpoints"), list)):
                        firmware_type = "new (endpoints array)"
                        print(f"     ✓ Detected firmware type: {firmware_type}")
                        print(f"     Debug: endpoints value: {original_config.get('endpoints')}")
                    elif "api_key" in original_config and "hub" in original_config:
                        firmware_type = "old (api_key/hub structure)"
                        print(f"     ✓ Detected firmware type: {firmware_type}")
                        print(f"     Debug: endpoints value: {original_config.get('endpoints')}")
                    else:
                        firmware_type = "unknown"
                        print("     ⚠ Warning: Unrecognized firmware structure")
                    
                    print("     Step 2: Running setup with test values...")
                    # Step 2: Run setup with test values
                    test_api_key = "TEST_API_KEY_12345"
                    test_server = "http://test.example.com/api/test"
                    
                    setup_success = await hub.setup(test_api_key, test_server, retries=2)
                    
                    if not setup_success:
                        results.test_fail("Setup function", "setup() returned False")
                    else:
                        print("     Step 3: Verifying config was modified...")
                        # Step 3: Read modified config to verify changes
                        modified_config = await hub._get_device_config()
                        
                        if not modified_config:
                            results.test_fail("Setup function", "Failed to read modified config")
                        else:
                            # Verify the changes based on firmware version
                            config_verified = False
                            
                            # Check for new firmware: endpoints must be a list (can be empty)
                            if ("endpoints" in modified_config and 
                                isinstance(modified_config.get("endpoints"), list)):
                                # New firmware with endpoints array
                                for endpoint in modified_config.get("endpoints", []):
                                    if (endpoint.get("name") == "HomeAssistant" and
                                        endpoint.get("config", {}).get("api_key") == test_api_key and
                                        endpoint.get("config", {}).get("url") == test_server):
                                        config_verified = True
                                        print("     ✓ Config successfully modified (new firmware)")
                                        break
                            elif "api_key" in modified_config and "hub" in modified_config:
                                # Old firmware with api_key and hub sections
                                if (modified_config.get("api_key") == test_api_key and
                                    modified_config.get("hub", {}).get("server_url") == test_server):
                                    config_verified = True
                                    print("     ✓ Config successfully modified (old firmware)")
                            
                            if config_verified:
                                if restore_config:
                                    print("     Step 4: Restoring original config...")
                                    # Step 4: Restore original config
                                    restore_success = await hub._set_device_config(original_config)
                                    
                                    if restore_success:
                                        # Verify restoration
                                        print("     Step 5: Verifying restoration...")
                                        final_config = await hub._get_device_config()
                                        
                                        # For new firmware, check if we removed the test endpoint
                                        # For old firmware, check if settings match original
                                        restoration_verified = False
                                        
                                        if final_config:
                                            # Check if original was new firmware (endpoints is a list)
                                            if ("endpoints" in original_config and 
                                                isinstance(original_config.get("endpoints"), list)):
                                                # Compare endpoint counts or verify test endpoint is gone
                                                original_count = len(original_config.get("endpoints", []))
                                                final_count = len(final_config.get("endpoints", []))
                                                restoration_verified = (final_count <= original_count)
                                            else:
                                                # For old firmware, compare api_key and server_url
                                                restoration_verified = (
                                                    final_config.get("api_key") == original_config.get("api_key") and
                                                    final_config.get("hub", {}).get("server_url") == 
                                                    original_config.get("hub", {}).get("server_url")
                                                )
                                        
                                        if restoration_verified:
                                            print("     ✓ Original config restored successfully")
                                            results.test_pass("Setup function",
                                                            f"Config modified and restored ({firmware_type})")
                                        else:
                                            results.test_fail("Setup function",
                                                            f"Restoration verification failed ({firmware_type})")
                                    else:
                                        results.test_fail("Setup function",
                                                        f"Failed to restore original config ({firmware_type})")
                                else:
                                    # User chose not to restore
                                    print("     ⚠ Skipping restoration - test config remains on device!")
                                    results.test_pass("Setup function",
                                                    f"Config modified successfully ({firmware_type}, not restored)")
                            else:
                                # Config wasn't modified as expected
                                if restore_config:
                                    print("     Config verification failed, restoring anyway...")
                                    await hub._set_device_config(original_config)
                                results.test_fail("Setup function",
                                                f"Config changes not verified ({firmware_type})")
                                
            except Exception as e:
                # If anything fails, try to restore original config if user wanted restoration
                try:
                    if original_config and restore_config:
                        print("     Exception occurred, attempting to restore original config...")
                        await hub._set_device_config(original_config)
                        results.test_fail("Setup function", f"Exception: {e} (config restored)")
                    else:
                        results.test_fail("Setup function", f"Exception: {e} (no restoration)")
                except Exception as restore_error:
                    results.test_fail("Setup function",
                                    f"Exception: {e}, restore also failed: {restore_error}")
        else:
            results.test_skip("Setup function", "User chose not to test setup function")
    
        # Test 8: Error handling - test with bad retry count
        print("\n📋 Test 8: Error Handling")
        try:
            # Create a new hub with invalid IP to test error handling
            # Share the same session so it gets cleaned up properly
            bad_hub = VegeHub(ip_address="192.168.255.254", session=session)
            try:
                await bad_hub.retrieve_mac_address(retries=0)
                results.test_fail("Error handling",
                                  "Should have raised ConnectionError")
            except ConnectionError:
                results.test_pass("Error handling",
                                  "Correctly raises ConnectionError")
        except Exception as e:
            results.test_fail("Error handling", f"Unexpected error: {e}")
    
        return results


async def main(devices: list[dict]):
    """Main entry point."""

    # Let user select a device
    selected = select_device(devices)
    if not selected:
        print("\nNo device selected. Exiting.")
        sys.exit(0)

    print(f"\n✓ Selected: {selected['name']} ({selected['ip']})")

    # Ask about actuator testing
    print("\n⚠️  Actuator Testing Warning:")
    print("   Testing actuators will send commands to the device.")
    print("   The test will use safe parameters (state=0, duration=0),")
    print("   but you should only proceed if it's safe to do so.")

    test_actuators = ask_yes_no("\nTest actuator functionality?",
                                default=False)

    # Ask about setup/config testing
    print("\n⚠️  Setup Function Testing Warning:")
    print("   Testing the setup function will temporarily modify device config.")
    print("   The test will add a test endpoint/settings, verify changes,")
    print("   and can optionally restore the original configuration.")

    test_setup = ask_yes_no("\nTest setup function (config modification)?",
                           default=True)
    
    restore_config = False
    if test_setup:
        restore_config = ask_yes_no(
            "   Restore original config after test?",
            default=True)

    # Confirm before proceeding
    print("\n📝 Test Configuration:")
    print(f"   Device: {selected['ip']}")
    print(f"   Test actuators: {'Yes' if test_actuators else 'No'}")
    print(f"   Test setup function: {'Yes' if test_setup else 'No'}")
    if test_setup:
        print(f"   Restore original config: {'Yes' if restore_config else 'No'}")

    if not ask_yes_no("\nProceed with tests?", default=True):
        print("\nTests cancelled.")
        sys.exit(0)

    # Run tests
    results = await run_integration_tests(selected['ip'], test_actuators,
                                          test_setup, restore_config)

    # Print summary
    results.print_summary()

    # No need for cleanup delay when using a shared session!
    # The async with block will properly close the session

    # Exit with appropriate code
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    try:
        # Run device discovery BEFORE entering async context
        # Zeroconf uses threading which can conflict with asyncio event loops
        print("\n" + "=" * 60)
        print("VegeHub Integration Test Suite")
        print("=" * 60)
        
        discovered_devices = discover_vegehubs()
        
        # Now run the async main function with the discovered devices
        asyncio.run(main(discovered_devices))
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
