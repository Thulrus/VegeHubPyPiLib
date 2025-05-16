"""Helper file containing data transformations."""
from typing import Any

def vh400_transform(value: int | str | float) -> float | None:
    """Perform a piecewise linear transformation on the input value.

    The transform is based on the following pairs of points:
    (0,0), (1.1000, 10.0000), (1.3000, 15.0000), (1.8200, 40.0000),
    (2.2000, 50.0000), (3.0000, 100.0000)
    """

    float_value = None

    if isinstance(value, float):
        float_value = value

    if isinstance(value, (int, str)):
        try:
            float_value = float(value)
        except ValueError:
            return None

    if not isinstance(float_value, float):
        return None

    ret = 100.0

    if float_value <= 0.0100:
        # Below 0.01V is just noise and should be reported as 0
        ret = 0
    elif float_value <= 1.1000:
        # Linear interpolation between (0.0000, 0.0000) and (1.1000, 10.0000)
        ret = (10.0000 - 0.0000) / (1.1000 - 0.0000) * (float_value - 0.0000) + 0.0000
    elif float_value <= 1.3000:
        # Linear interpolation between (1.1000, 10.0000) and (1.3000, 15.0000)
        ret = (15.0000 - 10.0000) / (1.3000 - 1.1000) * (float_value - 1.1000) + 10.0000
    elif float_value <= 1.8200:
        # Linear interpolation between (1.3000, 15.0000) and (1.8200, 40.0000)
        ret = (40.0000 - 15.0000) / (1.8200 - 1.3000) * (float_value - 1.3000) + 15.0000
    elif float_value <= 2.2000:
        # Linear interpolation between (1.8200, 40.0000) and (2.2000, 50.0000)
        ret = (50.0000 - 40.0000) / (2.2000 - 1.8200) * (float_value - 1.8200) + 40.0000
    elif float_value <= 3.0000:
        # Linear interpolation between (2.2000, 50.0000) and (3.0000, 100.0000)
        ret = (100.0000 - 50.0000) / (3.0000 - 2.2000) * (float_value - 2.2000) + 50.0000

    # For values greater than 3.0000, return 100.0000
    return ret

def therm200_transform(value: int | str | float) -> float | None:
    """Transform to change voltage into degrees celsius."""
    if not isinstance(value, (int, str, float)):
        return None
    try:
        float_value = float(value)
    except ValueError:
        return None

    return (41.6700 * float_value) - 40.0000

def update_data_to_latest_dict(data: dict[str,Any]) -> dict[str,Any]:
    """Accepts raw update data and returns a dict of the latest values of each sensor."""
    sensor_data = {}
    # Process sensor data
    if "sensors" in data and "mac" in data:
        for sensor in data["sensors"]:
            slot = sensor.get("slot")
            latest_sample = sensor["samples"][-1]
            value = latest_sample["v"]
            entity_id = f"{data['mac']}_{slot}".lower()
            sensor_data[entity_id] = value
    return sensor_data

def update_data_to_ha_dict(
    data: dict[str, Any],
    num_sensors: int,
    num_actuators: int
) -> dict[str, Any]:
    """Transform raw update data into a dictionary of sensor and actuator values.
    
    Args:
        data: Raw data dictionary containing sensors and mac address
        num_sensors: Number of analog sensors to process
        num_actuators: Number of actuators to process
    
    Returns:
        Dictionary mapping entity IDs to their values
    """
    if not ("sensors" in data and "mac" in data):
        return {}

    sensor_data = {}
    sensors = sorted(data["sensors"], key=lambda x: x.get("slot", 0))
    current_position = 0

    # Process analog sensors
    for i in range(num_sensors):
        value = sensors[current_position]["samples"][-1]["v"]
        sensor_data[f"analog_{i}"] = value
        current_position += 1

    # Process battery if present
    remaining_items = len(sensors) - current_position
    if remaining_items > num_actuators:
        value = sensors[current_position]["samples"][-1]["v"]
        sensor_data["battery"] = value
        current_position += 1

    # Process actuators
    for i in range(num_actuators):
        value = sensors[current_position]["samples"][-1]["v"]
        sensor_data[f"actuator_{i}"] = value
        current_position += 1

    return sensor_data
