from .membership import triangular_membership


def irrigation_output_fuzzy(value):

    return {
        "Very Low": triangular_membership(value, 0, 0, 15),

        "Low": triangular_membership(value, 0, 15, 30),

        "Medium": triangular_membership(value, 15, 30, 45),

        "High": triangular_membership(value, 30, 45, 60),

        "Very High": triangular_membership(value, 45, 60, 60)
    }


def defuzzify(output_strengths):

    numerator = 0.0
    denominator = 0.0

    # Evaluate output over 0 to 60 minutes
    for duration in range(61):

        aggregated_membership = 0.0

        for category, strength in output_strengths.items():

            membership = irrigation_output_fuzzy(duration)[category]

            # Mamdani implication: minimum
            activated_membership = min(strength, membership)

            # Aggregation: maximum
            aggregated_membership = max(
                aggregated_membership,
                activated_membership
            )

        numerator += duration * aggregated_membership
        denominator += aggregated_membership

    if denominator == 0:
        return 0.0

    return numerator / denominator

