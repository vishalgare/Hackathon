CROP_DATA = {
    "Cotton": {
        "base_yield": 8,
        "water_need": 100,
        "input_cost": 9000,
        "price_per_quintal": 7000,
        "water_sensitivity": 1.0,
        "rainfall_sensitivity": 1.0,
        "planting_sensitivity": 1.0,
        "input_sensitivity": 1.0
    },
    "Wheat": {
        "base_yield": 12,
        "water_need": 70,
        "input_cost": 7000,
        "price_per_quintal": 2500,
        "water_sensitivity": 0.9,
        "rainfall_sensitivity": 0.8,
        "planting_sensitivity": 1.2,
        "input_sensitivity": 0.9
    },
    "Soybean": {
        "base_yield": 10,
        "water_need": 60,
        "input_cost": 6500,
        "price_per_quintal": 4500,
        "water_sensitivity": 0.8,
        "rainfall_sensitivity": 1.2,
        "planting_sensitivity": 1.1,
        "input_sensitivity": 0.9
    },
    "Sugarcane": {
        "base_yield": 35,
        "water_need": 140,
        "input_cost": 12000,
        "price_per_quintal": 350,
        "water_sensitivity": 1.3,
        "rainfall_sensitivity": 0.7,
        "planting_sensitivity": 0.8,
        "input_sensitivity": 1.1
    }
}


def simulate(crop, area, water, rainfall, planting, inputs):
    data = CROP_DATA[crop]

    water_required_per_acre = data["water_need"]
    water_available_per_acre = water

    water_required = water_required_per_acre * area
    water_available = water_available_per_acre * area

    water_ratio = (
        water_available_per_acre
        / water_required_per_acre
    )

    water_risk = 0
    weather_risk = 0
    planting_risk = 0
    input_risk = 0

    yield_factor = 1.0
    reasons = []

    if water_ratio < 0.6:
        water_penalty = 0.25 * data["water_sensitivity"]
        yield_factor -= water_penalty
        water_risk = round(35 * data["water_sensitivity"])
        reasons.append("Severe water stress")

    elif water_ratio < 0.8:
        water_penalty = 0.10 * data["water_sensitivity"]
        yield_factor -= water_penalty
        water_risk = round(20 * data["water_sensitivity"])
        reasons.append("Moderate water stress")

    elif water_ratio < 1.0:
        water_risk = round(10 * data["water_sensitivity"])
        reasons.append("Slight water limitation")

    if rainfall == "Low":
        rainfall_penalty = (
            0.15
            * data["rainfall_sensitivity"]
        )

        yield_factor -= rainfall_penalty

        weather_risk = round(
            25 * data["rainfall_sensitivity"]
        )

        reasons.append("Low rainfall")

    elif rainfall == "High":
        rainfall_penalty = (
            0.05
            * data["rainfall_sensitivity"]
        )

        yield_factor -= rainfall_penalty

        weather_risk = round(
            15 * data["rainfall_sensitivity"]
        )

        reasons.append("Excess rainfall")

    if planting == "Delayed":
        planting_penalty = (
            0.10
            * data["planting_sensitivity"]
        )

        yield_factor -= planting_penalty

        planting_risk = round(
            20 * data["planting_sensitivity"]
        )

        reasons.append("Delayed planting")

    input_multiplier = {
        "Low": 1 - (
            0.15
            * data["input_sensitivity"]
        ),
        "Normal": 1.0,
        "High": 1 + (
            0.10
            * data["input_sensitivity"]
        )
    }

    yield_factor *= input_multiplier[inputs]

    if inputs == "Low":
        input_risk = round(
            15 * data["input_sensitivity"]
        )

        reasons.append("Low input usage")

    water_deficit = max(
        water_required - water_available,
        0
    )

    water_used = min(
        water_required,
        water_available
    )

    irrigation_cost = water_used * 8

    input_cost = data["input_cost"] * area

    if inputs == "Low":
        input_cost *= 0.85

    elif inputs == "High":
        input_cost *= 1.15

    labor_cost = 2500 * area

    planting_cost = 500 * area

    total_cost = (
        input_cost
        + irrigation_cost
        + labor_cost
        + planting_cost
    )

    yield_factor = max(
        yield_factor,
        0
    )

    expected_yield = (
        data["base_yield"]
        * area
        * yield_factor
    )

    expected_revenue = (
        expected_yield
        * data["price_per_quintal"]
    )

    expected_profit = (
        expected_revenue
        - total_cost
    )

    risk_score = (
        water_risk
        + weather_risk
        + planting_risk
        + input_risk
    )

    risk_score = min(
        risk_score,
        100
    )

    if risk_score < 30:
        risk_level = "Low"

    elif risk_score < 60:
        risk_level = "Medium"

    else:
        risk_level = "High"

    if not reasons:
        reasons.append(
            "Favorable farming conditions"
        )

    return {
        "yield": round(
            expected_yield,
            2
        ),

        "water_used": round(
            water_used,
            2
        ),

        "water_required": round(
            water_required,
            2
        ),

        "water_available": round(
            water_available,
            2
        ),

        "water_deficit": round(
            water_deficit,
            2
        ),

        "input_cost": round(
            input_cost,
            2
        ),

        "irrigation_cost": round(
            irrigation_cost,
            2
        ),

        "labor_cost": round(
            labor_cost,
            2
        ),

        "planting_cost": round(
            planting_cost,
            2
        ),

        "cost": round(
            total_cost,
            2
        ),

        "revenue": round(
            expected_revenue,
            2
        ),

        "profit": round(
            expected_profit,
            2
        ),

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


def calculate_factor_impacts(
    scenario_a,
    scenario_b
):
    factor_names = [
        "Crop",
        "Farm Area",
        "Water Availability",
        "Rainfall Condition",
        "Planting Schedule",
        "Input Usage"
    ]

    impacts = []

    baseline = simulate(
        *scenario_a
    )

    for index, factor in zip(
        [0, 1, 2, 3, 4, 5],
        factor_names
    ):

        if scenario_a[index] == scenario_b[index]:
            continue

        test_scenario = list(
            scenario_a
        )

        test_scenario[index] = (
            scenario_b[index]
        )

        changed = simulate(
            *test_scenario
        )

        yield_impact = (
            changed["yield"]
            - baseline["yield"]
        )

        profit_impact = (
            changed["profit"]
            - baseline["profit"]
        )

        risk_impact = (
            changed["risk_score"]
            - baseline["risk_score"]
        )

        yield_percentage = 0

        if baseline["yield"] != 0:
            yield_percentage = (
                yield_impact
                / baseline["yield"]
            ) * 100

        impacts.append({
            "factor": factor,
            "yield_impact": round(
                yield_impact,
                2
            ),
            "yield_percentage": round(
                yield_percentage,
                1
            ),
            "profit_impact": round(
                profit_impact,
                2
            ),
            "risk_impact": risk_impact
        })

    impacts.sort(
        key=lambda x: abs(
            x["yield_percentage"]
        ),
        reverse=True
    )

    return impacts