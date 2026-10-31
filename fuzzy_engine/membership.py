def triangular_membership(x, a, b, c):

    # Left shoulder: maximum membership at the left boundary
    if a == b:
        if x <= b:
            return 1.0
        elif x >= c:
            return 0.0
        else:
            return (c - x) / (c - b)

    # Right shoulder: maximum membership at the right boundary
    if b == c:
        if x >= b:
            return 1.0
        elif x <= a:
            return 0.0
        else:
            return (x - a) / (b - a)

    # Ordinary triangular membership
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif x < b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)


# SOIL MOISTURE MEMBERSHIP FUNCTIONS

def soil_moisture_fuzzy(value):

    return {
        "Dry": triangular_membership(value, 0, 0, 50),
        "Moderate": triangular_membership(value, 25, 50, 75),
        "Wet": triangular_membership(value, 50, 100, 100)
    }


# TEMPERATURE MEMBERSHIP FUNCTIONS

def temperature_fuzzy(value):

    return {
        "Cool": triangular_membership(value, 0, 0, 25),
        "Normal": triangular_membership(value, 15, 25, 35),
        "Hot": triangular_membership(value, 25, 50, 50)
    }


# HUMIDITY MEMBERSHIP FUNCTIONS

def humidity_fuzzy(value):

    return {
        "Low": triangular_membership(value, 0, 0, 50),
        "Medium": triangular_membership(value, 25, 50, 75),
        "High": triangular_membership(value, 50, 100, 100)
    }

