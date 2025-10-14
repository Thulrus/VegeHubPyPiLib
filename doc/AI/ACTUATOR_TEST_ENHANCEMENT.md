# Actuator Test Enhancement

## Overview
Enhanced Test 6 (Actuator Control) to include command verification and proper cleanup.

## Changes Made

### Previous Behavior
- Test 6 only sent a single command to turn actuator 0 OFF (state=0)
- No verification that the command actually worked
- No cleanup after testing

### New Behavior
Test 6 now performs a complete 4-step test cycle:

#### Step 0: Turn All Actuators OFF (Clean Start)
```python
for slot_num in range(actuator_count):
    await hub.set_actuator(state=0, slot=slot_num, duration=0, retries=2)
```
- Ensures clean starting state regardless of previous actuator states
- Turns OFF all actuators before testing
- Waits 0.5 seconds for device to settle
- Displays: `✓ All N actuator(s) turned OFF`
- Warns if any fail: `⚠ Some actuators may still be on`

#### Step 1: Turn ON Actuator
```python
await hub.set_actuator(state=1, slot=0, duration=0, retries=2)
```
- Sends command to turn actuator 0 ON
- Verifies command was sent successfully
- Displays: `✓ Command sent successfully`

#### Step 2: Verify State Change
```python
await asyncio.sleep(0.5)  # Brief delay for device update
verify_states = await hub.actuator_states(retries=2)
```
- Waits 0.5 seconds for device to update
- Retrieves actuator states
- Checks if actuator 0 is actually ON (state=1)
- Displays result:
  - `✓ Actuator 0 state verified: ON` (success)
  - `⚠ Actuator 0 state: X (expected 1)` (mismatch)

#### Step 3: Turn All Actuators OFF
```python
for slot_num in range(actuator_count):
    await hub.set_actuator(state=0, slot=slot_num, duration=0, retries=2)
```
- Iterates through all actuators on the device
- Sends OFF command to each one
- Verifies all commands succeeded
- Displays: `✓ All N actuator(s) turned OFF`

### Error Handling
Enhanced error handling with cleanup:
- If any step fails, still attempts to turn all actuators OFF
- Exception handler includes best-effort cleanup:
  ```python
  try:
      print("Exception occurred, attempting to turn all actuators OFF...")
      for slot_num in range(actuator_count):
          await hub.set_actuator(state=0, slot=slot_num, duration=0, retries=2)
  except Exception:
      pass  # Best effort cleanup
  ```

## Test Results

### Success Case
```
✓ Pass - Actuator control
  Command sent, verified, and cleaned up (N actuator(s))
```

### Failure Cases
- Command fails: `✗ Fail - Command to turn ON returned failure`
- Verification fails: `✗ Fail - State verification: expected 1, got X`
- Cleanup fails: `✗ Fail - Some actuators failed to turn OFF`
- Exception: `✗ Fail - Exception: <error message>`

### Skip Cases (Unchanged)
- User declined testing: `⊘ Skip - User chose not to test actuators`
- No actuators present: `⊘ Skip - No actuators on this device`

## Console Output Example

```
📋 Test 6: Actuator Control
     Step 0: Turning all actuators OFF (clean start)...
     ✓ All 2 actuator(s) turned OFF
     Step 1: Turning on actuator 0...
     ✓ Command sent successfully
     Step 2: Verifying actuator state...
     ✓ Actuator 0 state verified: ON
     Step 3: Turning all actuators OFF...
     ✓ All 2 actuator(s) turned OFF

Test 6: Actuator Control
Status: ✓ Pass - Command sent, verified, and cleaned up (2 actuator(s))
```

## Safety Features

1. **Clean Start**: Turns all actuators OFF before testing to ensure predictable starting state
2. **Minimal Duration**: All commands use `duration=0` to minimize actuator runtime
3. **Automatic Cleanup**: All actuators turned OFF after testing
4. **Exception Cleanup**: Best-effort cleanup even if test throws exception
5. **User Consent**: Only runs if user explicitly chose to test actuators

## Technical Details

### Timing
- 0.5 second delay after initial OFF commands (let device settle)
- 0.5 second delay between ON command and verification (let device update)
- Configurable if needed for different device response times

### State Verification
- Retrieves full actuator states after command
- Searches for slot 0 in returned states
- Compares actual state to expected state (1 = ON)
- Handles missing or malformed state data gracefully

### Cleanup Loop
- Uses `actuator_count` from Test 5 results
- Sends OFF command to all slots (0 to actuator_count-1)
- Tracks success of each command
- Reports partial failures if some actuators don't respond

## Benefits

1. **Clean Start**: Ensures predictable test behavior by turning everything OFF first
2. **Confidence**: Verifies commands actually work, not just that they were sent
3. **Safety**: Ensures all actuators are OFF after testing
4. **Debugging**: Provides detailed feedback about each step
5. **Robustness**: Cleanup happens even if test fails
6. **Transparency**: User sees exactly what's happening at each step

## Related Files
- `integration_test.py` - Main test script (Test 6 enhanced)
- `INTEGRATION_TESTS.md` - User guide (may need update)
- `vegehub/vegehub.py` - Library being tested
