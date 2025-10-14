# Integration Test - Setup Function Testing

## Overview

Test 7 has been updated to comprehensively test the `setup()` function, which modifies the VegeHub configuration. This test safely modifies the config and then restores the original settings.

## Test Flow

### Step 1: Backup Original Config
```python
original_config = await hub._get_device_config()
```
Reads and saves the current configuration before making any changes.

### Step 2: Run Setup
```python
test_api_key = "TEST_API_KEY_12345"
test_server = "http://test.example.com/api/test"
setup_success = await hub.setup(test_api_key, test_server, retries=2)
```
Calls the `setup()` function with test values to modify the configuration.

### Step 3: Verify Modification
The test verifies the config was modified correctly based on firmware version:

#### New Firmware (with `endpoints` array):
```python
if "endpoints" in modified_config:
    # Look for new HomeAssistant endpoint with test values
    for endpoint in modified_config.get("endpoints", []):
        if (endpoint.get("name") == "HomeAssistant" and
            endpoint.get("config", {}).get("api_key") == test_api_key and
            endpoint.get("config", {}).get("url") == test_server):
            config_verified = True
```

#### Old Firmware (with `api_key` and `hub` sections):
```python
elif "api_key" in modified_config and "hub" in modified_config:
    if (modified_config.get("api_key") == test_api_key and
        modified_config.get("hub", {}).get("server_url") == test_server):
        config_verified = True
```

### Step 4: Restore Original Config
```python
restore_success = await hub._set_device_config(original_config)
```
Sends the original configuration back to the device.

### Step 5: Verify Restoration
Confirms the original settings were restored:

**New Firmware:**
- Checks that endpoint count returned to original (test endpoint removed)

**Old Firmware:**
- Verifies `api_key` and `server_url` match original values

## Safety Features

### Error Handling
If any exception occurs during the test:
1. Catches the exception
2. Attempts to restore original config
3. Reports the error with restoration status

```python
except Exception as e:
    if original_config:
        await hub._set_device_config(original_config)
        results.test_fail("Setup function", f"Exception: {e} (config restored)")
```

### Firmware Compatibility
The test handles both:
- **New firmware**: Uses `endpoints` array (VegeHub 5.0+)
- **Old firmware**: Uses `api_key` and `hub` sections (older versions)

The `_modify_device_config()` function returns `None` for old firmware when it can't create an endpoint. The test detects this and adjusts verification accordingly.

## Test Output

### Successful Test
```
📋 Test 7: Setup Function (Config Modification with Backup/Restore)
     Step 1: Reading original config...
     Step 2: Running setup with test values...
     Step 3: Verifying config was modified...
     Step 4: Restoring original config (new (endpoints))...
     Step 5: Verifying restoration...
  ✅ Setup function: Config modified and restored (new (endpoints))
```

### Failed Verification but Restored
```
📋 Test 7: Setup Function (Config Modification with Backup/Restore)
     Step 1: Reading original config...
     Step 2: Running setup with test values...
     Step 3: Verifying config was modified...
     Config verification failed (old (api_key/hub)), restoring anyway...
  ❌ Setup function: Config changes not verified (old (api_key/hub))
```

### Exception with Restoration
```
📋 Test 7: Setup Function (Config Modification with Backup/Restore)
     Step 1: Reading original config...
     Step 2: Running setup with test values...
     Exception occurred, attempting to restore original config...
  ❌ Setup function: Exception: ConnectionError (config restored)
```

## Configuration Comparison

### New Firmware Config Structure
```json
{
  "endpoints": [
    {
      "id": 1,
      "name": "HomeAssistant",
      "type": "custom",
      "enabled": true,
      "config": {
        "api_key": "TEST_API_KEY_12345",
        "url": "http://test.example.com/api/test"
      }
    }
  ]
}
```

### Old Firmware Config Structure
```json
{
  "api_key": "TEST_API_KEY_12345",
  "hub": {
    "server_url": "http://test.example.com/api/test",
    "server_type": 3
  }
}
```

## Why This Approach Works

1. **Non-destructive**: Always backs up before modifying
2. **Safe**: Restores original config even if test fails
3. **Comprehensive**: Tests actual config modification, not just API calls
4. **Compatible**: Works with both old and new firmware versions
5. **Informative**: Reports which firmware type was detected

## Running the Test

```bash
poetry run python integration_test.py
```

Select your device and choose to test actuators (optional). Test 7 will:
- Safely modify your VegeHub config
- Verify the changes took effect
- Restore your original settings
- Report success/failure with firmware type

Your VegeHub configuration will be unchanged after the test completes!

## Timeout Reduction

The mDNS discovery timeout has been reduced from 10 to 5 seconds now that the asyncio issue is fixed. Discovery should still happen within 1-2 seconds.

## Test Count

The test suite still has 8 tests total:
1. Basic properties
2. MAC address retrieval
3. Device info
4. Property accessors
5. Actuator states
6. Actuator control (optional)
7. Setup function with backup/restore (NEW!)
8. Error handling
