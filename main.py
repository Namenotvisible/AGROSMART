from fuzzy_engine.manual_fuzzy import evaluate_rules
from fuzzy_engine.output_membership import defuzzify


def predict_irrigation(soil, temperature, humidity):

    # Step 1: Evaluate all fuzzy rules
    fuzzy_output, activated_rules = evaluate_rules(
        soil,
        temperature,
        humidity
    )

    # Step 2: Defuzzification
    duration = defuzzify(fuzzy_output)

    # Step 3: Return complete result
    return {
        "soil_moisture": soil,
        "temperature": temperature,
        "humidity": humidity,
        "fuzzy_output": fuzzy_output,
        "irrigation_duration": round(duration, 2),
        "activated_rules": activated_rules
    }


# TESTING

if __name__ == "__main__":

    result = predict_irrigation(
        soil=35,
        temperature=35,
        humidity=40
    )

    print("\nSMART IRRIGATION RECOMMENDATION")
    print("--------------------------------")

    print("Soil Moisture:", result["soil_moisture"], "%")
    print("Temperature:", result["temperature"], "°C")
    print("Humidity:", result["humidity"], "%")

    print("\nFuzzy Output:")
    print(result["fuzzy_output"])

    print("\nRecommended Irrigation Duration:")
    print(result["irrigation_duration"], "minutes")

    print("\nActivated Rules:")

    for item in result["activated_rules"]:
        print(item)