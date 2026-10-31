
from main import predict_irrigation
from fuzzy_engine.library_fuzzy import predict_with_library


test_cases = [
    {
        "name": "Very Dry Soil",
        "soil": 10,
        "temperature": 40,
        "humidity": 20
    },
    {
        "name": "Moderately Moist Soil",
        "soil": 50,
        "temperature": 25,
        "humidity": 50
    },
    {
        "name": "Very Wet Soil",
        "soil": 90,
        "temperature": 25,
        "humidity": 80
    },
    {
        "name": "Hot and Dry Weather",
        "soil": 25,
        "temperature": 45,
        "humidity": 20
    },
    {
        "name": "Cool and Humid Weather",
        "soil": 60,
        "temperature": 10,
        "humidity": 90
    }
]


print("\nFUZZY ENGINE COMPARISON")
print("=" * 65)

for case in test_cases:

    manual_result = predict_irrigation(
        case["soil"],
        case["temperature"],
        case["humidity"]
    )["irrigation_duration"]

    library_result = predict_with_library(
        case["soil"],
        case["temperature"],
        case["humidity"]
    )

    difference = abs(manual_result - library_result)

    print("\nTest Case:", case["name"])
    print("Manual Engine:", manual_result, "minutes")
    print("Library Engine:", library_result, "minutes")
    print("Difference:", round(difference, 2), "minutes")

    print("-" * 65)
