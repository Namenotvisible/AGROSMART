from main import predict_irrigation


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


for case in test_cases:

    result = predict_irrigation(
        case["soil"],
        case["temperature"],
        case["humidity"]
    )

    print("\n", case["name"])
    print("Inputs:", case["soil"], case["temperature"], case["humidity"])
    print("Irrigation:", result["irrigation_duration"], "minutes")