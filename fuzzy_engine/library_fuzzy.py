import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from .manual_fuzzy import create_rule_base


def build_fuzzy_system():

    # 1. Define input and output universes

    soil = ctrl.Antecedent(
        np.arange(0, 101, 1),
        "soil_moisture"
    )

    temperature = ctrl.Antecedent(
        np.arange(0, 51, 1),
        "temperature"
    )

    humidity = ctrl.Antecedent(
        np.arange(0, 101, 1),
        "humidity"
    )

    irrigation = ctrl.Consequent(
        np.arange(0, 61, 1),
        "irrigation_duration"
    )

    # 2. Define soil membership functions

    soil["Dry"] = fuzz.trapmf(
        soil.universe, [0, 0, 0, 50]
    )

    soil["Moderate"] = fuzz.trimf(
        soil.universe, [25, 50, 75]
    )

    soil["Wet"] = fuzz.trapmf(
        soil.universe, [50, 100, 100, 100]
    )

    # 3. Define temperature membership functions

    temperature["Cool"] = fuzz.trapmf(
        temperature.universe, [0, 0, 0, 25]
    )

    temperature["Normal"] = fuzz.trimf(
        temperature.universe, [15, 25, 35]
    )

    temperature["Hot"] = fuzz.trapmf(
        temperature.universe, [25, 50, 50, 50]
    )

    # 4. Define humidity membership functions

    humidity["Low"] = fuzz.trapmf(
        humidity.universe, [0, 0, 0, 50]
    )

    humidity["Medium"] = fuzz.trimf(
        humidity.universe, [25, 50, 75]
    )

    humidity["High"] = fuzz.trapmf(
        humidity.universe, [50, 100, 100, 100]
    )

    # 5. Define output membership functions

    irrigation["Very Low"] = fuzz.trapmf(
        irrigation.universe, [0, 0, 0, 15]
    )

    irrigation["Low"] = fuzz.trimf(
        irrigation.universe, [0, 15, 30]
    )

    irrigation["Medium"] = fuzz.trimf(
        irrigation.universe, [15, 30, 45]
    )

    irrigation["High"] = fuzz.trimf(
        irrigation.universe, [30, 45, 60]
    )

    irrigation["Very High"] = fuzz.trapmf(
        irrigation.universe, [45, 60, 60, 60]
    )

    # 6. Generate all 27 rules

    rules = []

    for item in create_rule_base():

        rule = ctrl.Rule(
            soil[item["soil"]]
            & temperature[item["temperature"]]
            & humidity[item["humidity"]],
            irrigation[item["output"]]
        )

        rules.append(rule)

    # 7. Create fuzzy control system

    system = ctrl.ControlSystem(rules)

    return system


def predict_with_library(soil_value, temperature_value, humidity_value):

    system = build_fuzzy_system()

    simulation = ctrl.ControlSystemSimulation(system)

    simulation.input["soil_moisture"] = soil_value
    simulation.input["temperature"] = temperature_value
    simulation.input["humidity"] = humidity_value

    simulation.compute()

    return round(
        simulation.output["irrigation_duration"],
        2
    )


# TESTING

if __name__ == "__main__":

    result = predict_with_library(
        soil_value=35,
        temperature_value=35,
        humidity_value=40
    )

    print("LIBRARY FUZZY ENGINE")
    print("Recommended irrigation:", result, "minutes")