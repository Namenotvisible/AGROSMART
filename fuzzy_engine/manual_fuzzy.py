from itertools import product

from .membership import (
    soil_moisture_fuzzy,
    temperature_fuzzy,
    humidity_fuzzy
)


# Output categories
OUTPUT_LEVELS = {
    0: "Very Low",
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Very High"
}


# Input contribution scores
SOIL_SCORES = {
    "Dry": 3,
    "Moderate": 2,
    "Wet": 0
}

TEMPERATURE_SCORES = {
    "Cool": -1,
    "Normal": 0,
    "Hot": 1
}

HUMIDITY_SCORES = {
    "Low": 1,
    "Medium": 0,
    "High": -1
}


def create_rule_base():

    rules = []

    for soil, temperature, humidity in product(
        SOIL_SCORES,
        TEMPERATURE_SCORES,
        HUMIDITY_SCORES
    ):

        score = (
            SOIL_SCORES[soil]
            + TEMPERATURE_SCORES[temperature]
            + HUMIDITY_SCORES[humidity]
        )

        score = max(0, min(4, score))

        rules.append({
            "soil": soil,
            "temperature": temperature,
            "humidity": humidity,
            "output": OUTPUT_LEVELS[score]
        })

    return rules


def evaluate_rules(soil, temperature, humidity):

    # Fuzzification
    s = soil_moisture_fuzzy(soil)
    t = temperature_fuzzy(temperature)
    h = humidity_fuzzy(humidity)

    # Initialize output membership strengths
    output = {
        category: 0.0
        for category in OUTPUT_LEVELS.values()
    }

    activated_rules = []

    # Evaluate all 27 rules
    for rule in create_rule_base():

        strength = min(
            s[rule["soil"]],
            t[rule["temperature"]],
            h[rule["humidity"]]
        )

        # Mamdani aggregation: maximum
        category = rule["output"]

        output[category] = max(
            output[category],
            strength
        )

        if strength > 0:
            activated_rules.append({
                "rule": rule,
                "strength": strength
            })

    return output, activated_rules


# TESTING
if __name__ == "__main__":

    rules = create_rule_base()

    print("TOTAL RULES:", len(rules))

    result, activated = evaluate_rules(
        soil=35,
        temperature=35,
        humidity=40
    )

    print("\nFUZZY OUTPUT:")
    print(result)

    print("\nACTIVATED RULES:")

    for item in activated:
        print(
            item["rule"],
            "Strength:",
            round(item["strength"], 2)
        )