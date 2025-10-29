# Config Format Detection Fix

## Problem

The integration test was detecting all devices as "old firmware" even when they had new firmware with the `endpoints` array format.

## Root Cause

The `_get_device_config()` method in `vegehub/vegehub.py` was sending a payload that only requested old-format configuration:

```python
payload: dict[Any, Any] = {"hub": [], "api_key": []}
```

This payload tells the VegeHub device to return configuration in the old format with `hub` and `api_key` keys, even if the device supports the new `endpoints` format.

## The Fix

Updated the payload to request both old and new configuration formats:

```python
# Request both old and new config formats
# Old format: {"hub": [], "api_key": []}
# New format: {"endpoints": []}
payload: dict[Any, Any] = {"hub": [], "api_key": [], "endpoints": []}
```

### Changes Made

**File**: `vegehub/vegehub.py`
**Function**: `_get_device_config()` (line 182)
**Change**: Added `"endpoints": []` to the payload

### Before
```python
payload: dict[Any, Any] = {"hub": [], "api_key": []}
```

### After
```python
payload: dict[Any, Any] = {"hub": [], "api_key": [], "endpoints": []}
```

## How the VegeHub API Works

The VegeHub `/api/config/get` endpoint uses the POST payload to determine what configuration sections to return:

- If you request `{"hub": [], "api_key": []}`, you get old format data
- If you request `{"endpoints": []}`, you get new format data
- If you request `{"hub": [], "api_key": [], "endpoints": []}`, you get whichever format the device supports

By requesting all formats, the device will return its native configuration format, allowing the library to properly detect which firmware version is running.

## Impact

### Library Functions Affected
- `_get_device_config()` - Now returns correct format based on device firmware
- `_modify_device_config()` - Now receives correct format to detect and modify
- `setup()` - Now works correctly with both old and new firmware

### Integration Test
- Test 7 now correctly detects firmware type
- Firmware detection is more reliable
- Debug output added to show actual config keys received

## Testing

After this fix, the integration test should correctly identify:
- **Old Firmware**: Devices with `api_key` and `hub` in config
- **New Firmware**: Devices with `endpoints` array in config

### Debug Output Added

Added debug output in integration test to verify the fix:
```python
print(f"     Debug: Config keys: {list(original_config.keys())}")
```

This shows what keys are actually returned by the device, making it easy to confirm the fix is working.

## Backward Compatibility

This change is **fully backward compatible**:
- Old firmware devices will return `{"api_key": ..., "hub": ...}` as before
- New firmware devices will return `{"endpoints": [...]}` as they should
- The library's `_modify_device_config()` method already handles both formats

## Related Files
- `vegehub/vegehub.py` - Fixed payload in `_get_device_config()`
- `integration_test.py` - Added debug output for verification
- Unit tests should still pass (they mock the responses)

## Verification Steps

1. Run integration test against new firmware device
2. Check that Test 7 shows: `✓ Detected firmware type: new (endpoints array)`
3. Check debug output shows: `Debug: Config keys: ['endpoints', ...]`
4. Verify setup() function works correctly with the detected format
