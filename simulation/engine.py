CROP_DATA = {
    "Cotton": {
        "base_yield": 8,
        "water_need": 100,
        "input_cost": 9000,
        "price_per_quintal": 7000
    },
    "Wheat": {
        "base_yield": 12,
        "water_need": 70,
        "input_cost": 7000,
        "price_per_quintal": 2500
    },
    "Soybean": {
        "base_yield": 10,
        "water_need": 60,
        "input_cost": 6500,
        "price_per_quintal": 4500
    },
    "Sugarcane": {
        "base_yield": 35,
        "water_need": 140,
        "input_cost": 12000,
        "price_per_quintal": 350
    }
}


def simulate(crop, area, water, rainfall, planting, inputs):
    data = CROP_DATA[crop]

    water_ratio = water / data["water_need"]

    water_risk = 0
    weather_risk = 0
    planting_risk = 0
    input_risk = 0

    yield_factor = 1.0
    reasons = []

    if water_ratio < 0.6:
        yield_factor -= 0.25
        water_risk = 35
        reasons.append("Severe water stress")

    elif water_ratio < 0.8:
        yield_factor -= 0.10
        water_risk = 20
        reasons.append("Moderate water stress")

    elif water_ratio < 1.0:
        water_risk = 10
        reasons.append("Slight water limitation")

    if rainfall == "Low":
        yield_factor -= 0.15
        weather_risk = 25
        reasons.append("Low rainfall")

    elif rainfall == "High":
        yield_factor -= 0.05
        weather_risk = 15
        reasons.append("Excess rainfall")

    if planting == "Delayed":
        yield_factor -= 0.10
        planting_risk = 20
        reasons.append("Delayed planting")

    input_multiplier = {
        "Low": 0.85,
        "Normal": 1.0,
        "High": 1.10
    }

    yield_factor *= input_multiplier[inputs]

    if inputs == "Low":
        input_risk = 15
        reasons.append("Low input usage")

    risk_score = (
        water_risk
        + weather_risk
        + planting_risk
        + input_risk
    )

    risk_score = min(risk_score, 100)

    if risk_score < 30:
        risk_level = "Low"

    elif risk_score < 60:
        risk_level = "Medium"

    else:
        risk_level = "High"

    expected_yield = data["base_yield"] * area * yield_factor

    input_cost = data["input_cost"] * area

    if inputs == "Low":
        input_cost *= 0.85

    elif inputs == "High":
        input_cost *= 1.15

    water_required = data["water_need"] * area
    water_available = water * area

    water_used = min(water_required, water_available)
    water_deficit = max(water_required - water_available, 0)

    expected_revenue = expected_yield * data["price_per_quintal"]

    total_cost = input_cost

    expected_profit = expected_revenue - total_cost

    if not reasons:
        reasons.append("Favorable farming conditions")

    return {
        "yield": round(expected_yield, 2),
        "water_used": round(water_used, 2),
        "water_required": round(water_required, 2),
        "water_available": round(water_available, 2),
        "water_deficit": round(water_deficit, 2),
        "cost": round(total_cost, 2),
        "revenue": round(expected_revenue, 2),
        "profit": round(expected_profit, 2),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_breakdown": {
            "Water Stress": water_risk,
            "Weather": weather_risk,
            "Planting": planting_risk,
            "Input Usage": input_risk
        },
        "reasons": reasons
    }


def calculate_factor_impacts(scenario_a, scenario_b):
    factor_names = [
        "Water Availability",
        "Rainfall Condition",
        "Planting Schedule",
        "Input Usage"
    ]

    impacts = []

    baseline = simulate(*scenario_a)

    for index, factor in zip([2, 3, 4, 5], factor_names):

        if scenario_a[index] == scenario_b[index]:
            continue

        test_scenario = list(scenario_a)
        test_scenario[index] = scenario_b[index]

        changed = simulate(*test_scenario)

        yield_impact = changed["yield"] - baseline["yield"]
        profit_impact = changed["profit"] - baseline["profit"]
        risk_impact = changed["risk_score"] - baseline["risk_score"]

        yield_percentage = 0

        if baseline["yield"] != 0:
            yield_percentage = (
                yield_impact / baseline["yield"]
            ) * 100

        impacts.append({
            "factor": factor,
            "yield_impact": round(yield_impact, 2),
            "yield_percentage": round(yield_percentage, 1),
            "profit_impact": round(profit_impact, 2),
            "risk_impact": risk_impact
        })

    impacts.sort(
        key=lambda x: abs(x["yield_percentage"]),
        reverse=True
    )

    return impacts