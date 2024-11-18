"""Helper file containing data transformations."""

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
