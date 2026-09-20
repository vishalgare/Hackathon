import streamlit as st
import plotly.graph_objects as go

from simulation.engine import (
    simulate,
    calculate_factor_impacts,
    generate_explanation
)


st.set_page_config(
    page_title="FarmWise",
    page_icon="🌾",
    layout="wide"
)


st.title("🌾 FarmWise")
st.subheader("Smart Farming Scenario & Decision Simulator")

st.write(
    "Compare farming decisions based on crop, water, weather, "
    "planting schedule, farm area, and input usage."
)

st.caption(
    "Simulation-based decision support prototype — results are based on predefined model assumptions."
)


def scenario_inputs(title, key, description):
    with st.container(border=True):
        st.subheader(title)
        st.caption(description)

        col1, col2, col3 = st.columns(3)

        with col1:
            crop = st.selectbox(
                "Crop",
                ["Cotton", "Wheat", "Soybean", "Sugarcane"],
                key=f"{key}_crop"
            )

            area = st.number_input(
                "Farm Area (acres)",
                min_value=1.0,
                max_value=100.0,
                value=5.0,
                step=1.0,
                key=f"{key}_area"
            )

        with col2:
            water = st.number_input(
                "Water Availability (units/acre)",
                min_value=0.0,
                max_value=200.0,
                value=100.0,
                step=10.0,
                key=f"{key}_water"
            )

            rainfall = st.selectbox(
                "Rainfall Condition",
                ["Low", "Normal", "High"],
                index=1,
                key=f"{key}_rainfall"
            )

        with col3:
            planting = st.selectbox(
                "Planting Schedule",
                ["On Time", "Delayed"],
                key=f"{key}_planting"
            )

            inputs = st.selectbox(
                "Input Usage",
                ["Low", "Normal", "High"],
                index=1,
                key=f"{key}_inputs"
            )

    return (
        crop,
        area,
        water,
        rainfall,
        planting,
        inputs
    )


scenario_a = scenario_inputs(
    "🅰️ Scenario A — Baseline",
    "a",
    "Use this as the baseline farming plan for comparison."
)

scenario_b = scenario_inputs(
    "🅱️ Scenario B — Alternative",
    "b",
    "Modify one or more conditions to explore an alternative plan."
)


compare_col1, compare_col2, compare_col3 = st.columns([1, 2, 1])

with compare_col2:
    compare_button = st.button(
        "🔍 Compare Scenarios",
        type="primary",
        use_container_width=True
    )


if compare_button:

    result_a = simulate(*scenario_a)
    result_b = simulate(*scenario_b)

    st.divider()

    st.header("📊 Scenario Comparison")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Expected Yield",
            f"{result_a['yield']:.2f} q",
            f"{result_b['yield'] - result_a['yield']:+.2f} q"
        )

    with col2:
        st.metric(
            "Water Used",
            f"{result_a['water_used']:.0f}",
            f"{result_b['water_used'] - result_a['water_used']:+.0f}"
        )

    with col3:
        st.metric(
            "Estimated Cost",
            f"₹{result_a['cost']:,.0f}",
            f"₹{result_b['cost'] - result_a['cost']:+,.0f}"
        )

    with col4:
        st.metric(
            "Expected Profit",
            f"₹{result_a['profit']:,.0f}",
            f"₹{result_b['profit'] - result_a['profit']:+,.0f}"
        )

    with col5:
        st.metric(
            "Risk Score",
            f"{result_a['risk_score']}/100",
            f"{result_b['risk_score'] - result_a['risk_score']:+}"
        )

    st.subheader("📋 Detailed Comparison")

    comparison_data = {
        "Metric": [
            "Expected Yield",
            "Water Used",
            "Water Required",
            "Water Available",
            "Water Deficit",
            "Estimated Cost",
            "Expected Revenue",
            "Expected Profit",
            "Risk Score",
            "Risk Level"
        ],
        "Scenario A": [
            f"{result_a['yield']:.2f} q",
            f"{result_a['water_used']:.0f}",
            f"{result_a['water_required']:.0f}",
            f"{result_a['water_available']:.0f}",
            f"{result_a['water_deficit']:.0f}",
            f"₹{result_a['cost']:,.0f}",
            f"₹{result_a['revenue']:,.0f}",
            f"₹{result_a['profit']:,.0f}",
            f"{result_a['risk_score']}/100",
            result_a["risk_level"]
        ],
        "Scenario B": [
            f"{result_b['yield']:.2f} q",
            f"{result_b['water_used']:.0f}",
            f"{result_b['water_required']:.0f}",
            f"{result_b['water_available']:.0f}",
            f"{result_b['water_deficit']:.0f}",
            f"₹{result_b['cost']:,.0f}",
            f"₹{result_b['revenue']:,.0f}",
            f"₹{result_b['profit']:,.0f}",
            f"{result_b['risk_score']}/100",
            result_b["risk_level"]
        ]
    }

    st.table(comparison_data)

    st.subheader("💰 Cost Breakdown")

    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:
        st.write("**Scenario A**")

        st.write(
            f"Input Cost: ₹{result_a['input_cost']:,.0f}"
        )
        st.write(
            f"Irrigation Cost: ₹{result_a['irrigation_cost']:,.0f}"
        )
        st.write(
            f"Labor Cost: ₹{result_a['labor_cost']:,.0f}"
        )
        st.write(
            f"Planting Cost: ₹{result_a['planting_cost']:,.0f}"
        )

        st.write(
            f"**Total Cost: ₹{result_a['cost']:,.0f}**"
        )

    with cost_col2:
        st.write("**Scenario B**")

        st.write(
            f"Input Cost: ₹{result_b['input_cost']:,.0f}"
        )
        st.write(
            f"Irrigation Cost: ₹{result_b['irrigation_cost']:,.0f}"
        )
        st.write(
            f"Labor Cost: ₹{result_b['labor_cost']:,.0f}"
        )
        st.write(
            f"Planting Cost: ₹{result_b['planting_cost']:,.0f}"
        )

        st.write(
            f"**Total Cost: ₹{result_b['cost']:,.0f}**"
        )

    st.subheader("💧 Water Resource Analysis")

    water_col1, water_col2 = st.columns(2)

    with water_col1:
        st.write("**Scenario A**")
        st.write(
            f"Required: {result_a['water_required']:.0f} units"
        )
        st.write(
            f"Available: {result_a['water_available']:.0f} units"
        )
        st.write(
            f"Used: {result_a['water_used']:.0f} units"
        )
        st.write(
            f"Deficit: {result_a['water_deficit']:.0f} units"
        )

    with water_col2:
        st.write("**Scenario B**")
        st.write(
            f"Required: {result_b['water_required']:.0f} units"
        )
        st.write(
            f"Available: {result_b['water_available']:.0f} units"
        )
        st.write(
            f"Used: {result_b['water_used']:.0f} units"
        )
        st.write(
            f"Deficit: {result_b['water_deficit']:.0f} units"
        )

    st.subheader("📈 Visual Comparison")

    metrics = [
        "Yield",
        "Water Used",
        "Cost",
        "Revenue",
        "Profit"
    ]

    values_a = [
        result_a["yield"],
        result_a["water_used"],
        result_a["cost"],
        result_a["revenue"],
        result_a["profit"]
    ]

    values_b = [
        result_b["yield"],
        result_b["water_used"],
        result_b["cost"],
        result_b["revenue"],
        result_b["profit"]
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Scenario A",
            x=metrics,
            y=values_a
        )
    )

    fig.add_trace(
        go.Bar(
            name="Scenario B",
            x=metrics,
            y=values_b
        )
    )

    fig.update_layout(
        barmode="group",
        title="Scenario A vs Scenario B",
        xaxis_title="Metric",
        yaxis_title="Value",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("🧠 Why Did the Results Change?")

    explanation = generate_explanation(
        scenario_a,
        scenario_b,
        result_a,
        result_b
    )

    if explanation["factors"]:
        for factor in explanation["factors"]:
            st.write("• " + factor)

    st.write(
        "**Yield:** " +
        explanation["yield_summary"]
    )

    st.write(
        "**Profit:** " +
        explanation["profit_summary"]
    )

    st.write(
        "**Risk:** " +
        explanation["risk_summary"]
    )

    st.subheader("🎯 Impact Summary")

    yield_difference = result_b["yield"] - result_a["yield"]
    profit_difference = result_b["profit"] - result_a["profit"]
    risk_difference = result_b["risk_score"] - result_a["risk_score"]
    water_difference = result_b["water_used"] - result_a["water_used"]

    st.write(
        f"**Yield change:** {yield_difference:+.2f} q"
    )

    st.write(
        f"**Profit change:** ₹{profit_difference:+,.0f}"
    )

    st.write(
        f"**Risk change:** {risk_difference:+} points"
    )

    st.write(
        f"**Water usage change:** {water_difference:+.0f} units"
    )

    st.subheader("💡 Decision Insight")

    if (
        result_b["profit"] > result_a["profit"]
        and result_b["risk_score"] <= result_a["risk_score"]
        and result_b["water_deficit"] <= result_a["water_deficit"]
    ):
        st.success(
            "Scenario B shows higher simulated profit without increasing simulated risk or water deficit."
        )

    elif (
        result_b["profit"] < result_a["profit"]
        and result_b["risk_score"] > result_a["risk_score"]
    ):
        st.warning(
            "Scenario B has lower simulated profit and higher simulated risk compared with Scenario A."
        )

    elif (
        result_b["profit"] > result_a["profit"]
        and result_b["risk_score"] > result_a["risk_score"]
    ):
        st.warning(
            "Scenario B increases simulated profit but also increases simulated risk, creating a trade-off."
        )

    elif (
        result_b["profit"] < result_a["profit"]
        and result_b["risk_score"] <= result_a["risk_score"]
    ):
        st.info(
            "Scenario B reduces simulated profit but also reduces or maintains simulated risk."
        )

    else:
        st.info(
            "Scenario B produces a mixed result across profit, resources, and risk."
        )

    st.write("**Key Trade-offs:**")

    if result_b["water_deficit"] != result_a["water_deficit"]:
        st.write(
            f"• Water deficit changes by "
            f"{result_b['water_deficit'] - result_a['water_deficit']:+.0f} units."
        )

    if result_b["water_used"] != result_a["water_used"]:
        st.write(
            f"• Water usage changes by "
            f"{result_b['water_used'] - result_a['water_used']:+.0f} units."
        )

    if result_b["cost"] != result_a["cost"]:
        st.write(
            f"• Estimated cost changes by "
            f"₹{result_b['cost'] - result_a['cost']:+,.0f}."
        )

    st.subheader("🔎 Factor Impact Analysis")

    impacts = calculate_factor_impacts(
        scenario_a,
        scenario_b
    )

    if impacts:

        impact_data = {
            "Factor": [],
            "Yield Impact": [],
            "Yield Change": [],
            "Profit Impact": [],
            "Risk Impact": []
        }

        for impact in impacts:
            impact_data["Factor"].append(
                impact["factor"]
            )

            impact_data["Yield Impact"].append(
                f"{impact['yield_impact']:+.2f} q"
            )

            impact_data["Yield Change"].append(
                f"{impact['yield_percentage']:+.1f}%"
            )

            impact_data["Profit Impact"].append(
                f"₹{impact['profit_impact']:+,.0f}"
            )

            impact_data["Risk Impact"].append(
                f"{impact['risk_impact']:+}"
            )

        st.table(impact_data)

        top_factor = impacts[0]

        st.info(
            f"**Largest individual yield impact:** "
            f"{top_factor['factor']} "
            f"({top_factor['yield_percentage']:+.1f}% simulated yield)"
        )

    else:
        st.info(
            "No scenario factors were changed."
        )

    st.subheader("⚠️ Risk Breakdown")

    risk_col1, risk_col2 = st.columns(2)

    with risk_col1:
        st.write("**Scenario A**")

        st.write(
            f"Risk Level: **{result_a['risk_level']}**"
        )

        st.write(
            f"Risk Score: **{result_a['risk_score']}/100**"
        )

        for factor, value in result_a["risk_breakdown"].items():
            st.write(
                f"• {factor}: {value}"
            )

    with risk_col2:
        st.write("**Scenario B**")

        st.write(
            f"Risk Level: **{result_b['risk_level']}**"
        )

        st.write(
            f"Risk Score: **{result_b['risk_score']}/100**"
        )

        for factor, value in result_b["risk_breakdown"].items():
            st.write(
                f"• {factor}: {value}"
            )

    risk_factors = list(
        result_a["risk_breakdown"].keys()
    )

    risk_a = [
        result_a["risk_breakdown"][factor]
        for factor in risk_factors
    ]

    risk_b = [
        result_b["risk_breakdown"][factor]
        for factor in risk_factors
    ]

    risk_fig = go.Figure()

    risk_fig.add_trace(
        go.Bar(
            name="Scenario A",
            x=risk_factors,
            y=risk_a
        )
    )

    risk_fig.add_trace(
        go.Bar(
            name="Scenario B",
            x=risk_factors,
            y=risk_b
        )
    )

    risk_fig.update_layout(
        barmode="group",
        title="Risk Factor Comparison",
        xaxis_title="Risk Factor",
        yaxis_title="Risk Contribution",
        height=450
    )

    st.plotly_chart(
        risk_fig,
        use_container_width=True
    )

    st.subheader("📚 Model Assumptions & Limitations")

    st.write(
        "FarmWise uses predefined simulation assumptions to demonstrate "
        "how different farming conditions can affect simulated outcomes."
    )

    st.write(
        "The model does not use real-time weather, soil, market, "
        "or location-specific agricultural data."
    )

    st.write(
        "Results should not be treated as agricultural forecasts "
        "or professional farming recommendations."
    )