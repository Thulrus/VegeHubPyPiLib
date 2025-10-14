"""Tests for helpers.py."""

import pytest
from vegehub.helpers import (update_data_to_ha_dict,
                              update_data_to_latest_dict,
                              therm200_transform, vh400_transform)

UPDATE_DATA = {
    "api_key":
    "",
    "mac":
    "7C9EBD4B49D8",
    "error_code":
    0,
    "sensors": [{
        "slot": 1,
        "samples": [{
            "v": 1.5,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 2,
        "samples": [{
            "v": 1.45599997,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 3,
        "samples": [{
            "v": 1.330000043,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 4,
        "samples": [{
            "v": 0.075999998,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 5,
        "samples": [{
            "v": 9.314800262,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 6,
        "samples": [{
            "v": 1,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 7,
        "samples": [{
            "v": 0,
            "t": "2025-01-15T16:51:23Z"
        }]
    }],
    "send_time":
    1736959883,
    "wifi_str":
    -27
}
UPDATE_DATA_2 = {
    'api_key':
    '',
    'mac':
    '7C9EBD4B49D8',
    'error_code':
    0,
    'sensors': [{
        'slot': 1,
        'samples': [{
            'v': 1.518,
            't': '2025-05-16T20:38:40Z'
        }]
    }, {
        'slot': 2,
        'samples': [{
            'v': 1.498,
            't': '2025-05-16T20:38:40Z'
        }]
    }, {
        'slot': 3,
        'samples': [{
            'v': 0.026,
            't': '2025-05-16T20:38:40Z'
        }]
    }, {
        'slot': 4,
        'samples': [{
            'v': 2.346,
            't': '2025-05-16T20:38:40Z'
        }]
    }, {
        'slot': 5,
        'samples': [{
            'v': 9.3588,
            't': '2025-05-16T20:38:40Z'
        }]
    }],
    'send_time':
    1747427920,
    'wifi_str':
    -28
}
UPDATE_DATA_ALL_ACTUATORS = {
    "api_key":
    "",
    "mac":
    "7C9EBD4B49D8",
    "error_code":
    0,
    "sensors": [{
        "slot": 1,
        "samples": [{
            "v": 1,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 2,
        "samples": [{
            "v": 0,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 3,
        "samples": [{
            "v": 1,
            "t": "2025-01-15T16:51:23Z"
        }]
    }, {
        "slot": 4,
        "samples": [{
            "v": 0,
            "t": "2025-01-15T16:51:23Z"
        }]
    }],
    "send_time":
    1736959883,
    "wifi_str":
    -27
}


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (0.005, 0.0),  # Below noise threshold
        (0.011, 0.09999),  # Just above the noise threshold
        (1, 9.09090909091),  # Within the first segment
        (1.1, 10.0),  # First segment boundary
        (1.2, 12.5),  # Within the second segment
        (1.3, 15.0),  # Second segment boundary
        (1.5, 24.615),  # Within the third segment
        (1.82, 40.0),  # Third segment boundary
        (2, 44.736),  # Within the fourth segment
        (2.2, 50.0),  # Fourth segment boundary
        (2.6, 75.0),  # Within the fifth segment
        (3, 100.0),  # Fifth segment boundary
        (3.5, 100.0),  # Beyond the last segment
        ("1.5", 24.615),  # String input, valid conversion
        ("invalid", None),  # Invalid string input
        (None, None),  # None input
        ([], None),  # Invalid type (list)
    ],
)
def test_vh400_transform(input_value, expected_output):
    """Test for basic values."""
    result = vh400_transform(input_value)
    assert pytest.approx(result, rel=1e-4) == expected_output


def test_vh400_transform_large_input():
    """Test values significantly larger than 3.0."""
    assert vh400_transform(10) == 100.0


def test_vh400_transform_negative_input():
    """Test negative input, which should result in 0.0."""
    assert vh400_transform(-1) == 0.0


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (0, -40.0),  # Zero voltage
        (1, 1.6700),  # Integer input
        (2, 43.3400),  # Integer input
        (0.5, -19.165),  # Float input
        ("0.5", -19.165),  # String representation of a float
        ("2", 43.3400),  # String representation of an integer
        ("invalid", None),  # Invalid string input
        (None, None),  # None input
        ([], None),  # Invalid type (list)
        (True, 1.6700),  # Boolean input (interpreted as int)
        (-1, -81.6700),  # Negative input
        (1000, 41630.0),  # Large value input
    ],
)
def test_therm200_transform(input_value, expected_output):
    """Test basic input values."""
    result = therm200_transform(input_value)
    if expected_output is None:
        assert result is None
    else:
        assert pytest.approx(result, rel=1e-4) == expected_output


def test_therm200_transform_large_negative_input():
    """Test very large negative inputs."""
    assert therm200_transform(-1000) == -41710.0


def test_therm200_transform_non_numeric_types():
    """Test non-numeric inputs explicitly."""
    assert therm200_transform({"key": "value"}) is None
    assert therm200_transform([1, 2, 3]) is None
    assert therm200_transform((1, 2)) is None


def test_therm200_transform_extreme_floats():
    """Test extreme float values."""
    assert pytest.approx(therm200_transform(1e-10), rel=1e-4) == -40.0
    assert pytest.approx(therm200_transform(1e10), rel=1e1) == 416699999.960


def test_update_data_converter():
    """Test the update data converter."""
    data = update_data_to_latest_dict(UPDATE_DATA)
    assert data["7c9ebd4b49d8_1"] == 1.5
    assert data["7c9ebd4b49d8_5"] == 9.314800262


def test_update_ha_data_converter():
    """Test the home assistant update data converter."""
    data = update_data_to_ha_dict(UPDATE_DATA, 4, 2, False)
    assert data["analog_0"] == 1.5
    assert data["battery"] == 9.314800262
    assert data["actuator_0"] == 1
    assert data["actuator_1"] == 0


def test_update_ha_data_converter_2():
    """Test the home assistant update data converter."""
    # Test with UPDATE_DATA_2, which has no actuators in it,
    # even though this Hub has actuators defined
    data = update_data_to_ha_dict(UPDATE_DATA_2, 4, 1, False)
    assert data["analog_0"] == 1.518
    assert data["battery"] == 9.3588


def test_update_ha_data_converter_bad_data():
    """Test the update data converter."""
    data = update_data_to_ha_dict({}, 4, 2, False)
    assert not data
    assert "battery" not in data


def test_update_ha_data_converter_no_sensors():
    """Test the update data converter."""
    data = update_data_to_ha_dict({
        "mac": "7C9EBD4B49D8",
        "sensors": []
    }, 4, 2, False)
    assert not data
    assert "battery" not in data


def test_update_ha_data_converter_no_samples():
    """Test the update data converter."""
    data = update_data_to_ha_dict(
        {
            "mac": "7C9EBD4B49D8",
            "sensors": [{
                "slot": 1,
                "samples": []
            }]
        }, 4, 2, False)
    assert not data
    assert "battery" not in data


def test_update_ha_data_converter_all_actuators():
    """Test the update data converter."""
    data = update_data_to_ha_dict(UPDATE_DATA_ALL_ACTUATORS, 0, 4, True)
    assert "battery" not in data
    assert "analog_0" not in data
    assert data["actuator_0"] == 1
    assert data["actuator_1"] == 0
    assert data["actuator_3"] == 0
    assert "actuator_4" not in data
