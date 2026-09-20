
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

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

    yield_difference = result_b["yield"] - result_a["yield"]
    water_difference = result_b["water_used"] - result_a["water_used"]
    cost_difference = result_b["cost"] - result_a["cost"]
    profit_difference = result_b["profit"] - result_a["profit"]
    risk_difference = result_b["risk_score"] - result_a["risk_score"]

    st.divider()

    st.header("📊 Scenario Comparison")

    st.caption(
        "Scenario A is the baseline. Scenario B shows the alternative outcome."
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Expected Yield",
            f"{result_a['yield']:.2f} q",
            f"{yield_difference:+.2f} q"
        )

    with col2:
        st.metric(
            "Water Used",
            f"{result_a['water_used']:.0f}",
            f"{water_difference:+.0f}"
        )

    with col3:
        if cost_difference < 0:
            cost_delta = f"-₹{abs(cost_difference):,.0f}"
        elif cost_difference > 0:
            cost_delta = f"+₹{cost_difference:,.0f}"
        else:
            cost_delta = "₹0"

        st.metric(
            "Estimated Cost",
            f"₹{result_a['cost']:,.0f}",
            cost_delta
        )

    with col4:
        if profit_difference < 0:
            profit_delta = f"-₹{abs(profit_difference):,.0f}"
        elif profit_difference > 0:
            profit_delta = f"+₹{profit_difference:,.0f}"
        else:
            profit_delta = "₹0"

        st.metric(
            "Expected Profit",
            f"₹{result_a['profit']:,.0f}",
            profit_delta
        )

    with col5:
        st.metric(
            "Risk Score",
            f"{result_a['risk_score']}/100",
            f"{risk_difference:+}"
        )

    st.subheader("📋 Detailed Comparison")

    comparison_data = pd.DataFrame({
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
    })

    st.dataframe(
        comparison_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("💰 Cost Breakdown")

    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:
        st.write("**Scenario A**")

        cost_a = pd.DataFrame({
            "Cost Component": [
                "Input Cost",
                "Irrigation Cost",
                "Labor Cost",
                "Planting Cost",
                "Total Cost"
            ],
            "Amount": [
                f"₹{result_a['input_cost']:,.0f}",
                f"₹{result_a['irrigation_cost']:,.0f}",
                f"₹{result_a['labor_cost']:,.0f}",
                f"₹{result_a['planting_cost']:,.0f}",
                f"₹{result_a['cost']:,.0f}"
            ]
        })

        st.dataframe(
            cost_a,
            use_container_width=True,
            hide_index=True
        )

    with cost_col2:
        st.write("**Scenario B**")

        cost_b = pd.DataFrame({
            "Cost Component": [
                "Input Cost",
                "Irrigation Cost",
                "Labor Cost",
                "Planting Cost",
                "Total Cost"
            ],
            "Amount": [
                f"₹{result_b['input_cost']:,.0f}",
                f"₹{result_b['irrigation_cost']:,.0f}",
                f"₹{result_b['labor_cost']:,.0f}",
                f"₹{result_b['planting_cost']:,.0f}",
                f"₹{result_b['cost']:,.0f}"
            ]
        })

        st.dataframe(
            cost_b,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("💧 Water Resource Analysis")

    water_col1, water_col2 = st.columns(2)

    with water_col1:
        st.write("**Scenario A**")

        water_a = pd.DataFrame({
            "Water Metric": [
                "Required",
                "Available",
                "Used",
                "Deficit"
            ],
            "Amount": [
                f"{result_a['water_required']:.0f} units",
                f"{result_a['water_available']:.0f} units",
                f"{result_a['water_used']:.0f} units",
                f"{result_a['water_deficit']:.0f} units"
            ]
        })

        st.dataframe(
            water_a,
            use_container_width=True,
            hide_index=True
        )

    with water_col2:
        st.write("**Scenario B**")

        water_b = pd.DataFrame({
            "Water Metric": [
                "Required",
                "Available",
                "Used",
                "Deficit"
            ],
            "Amount": [
                f"{result_b['water_required']:.0f} units",
                f"{result_b['water_available']:.0f} units",
                f"{result_b['water_used']:.0f} units",
                f"{result_b['water_deficit']:.0f} units"
            ]
        })

        st.dataframe(
            water_b,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("📈 Visual Comparison")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        yield_fig = go.Figure()

        yield_fig.add_trace(
            go.Bar(
                name="Scenario A",
                x=["Expected Yield"],
                y=[result_a["yield"]]
            )
        )

        yield_fig.add_trace(
            go.Bar(
                name="Scenario B",
                x=["Expected Yield"],
                y=[result_b["yield"]]
            )
        )

        yield_fig.update_layout(
            barmode="group",
            title="Expected Yield",
            yaxis_title="Quintals",
            height=400
        )

        st.plotly_chart(
            yield_fig,
            use_container_width=True
        )

    with chart_col2:

        water_fig = go.Figure()

        water_fig.add_trace(
            go.Bar(
                name="Scenario A",
                x=["Water Used"],
                y=[result_a["water_used"]]
            )
        )

        water_fig.add_trace(
            go.Bar(
                name="Scenario B",
                x=["Water Used"],
                y=[result_b["water_used"]]
            )
        )

        water_fig.update_layout(
            barmode="group",
            title="Water Usage",
            yaxis_title="Water Units",
            height=400
        )

        st.plotly_chart(
            water_fig,
            use_container_width=True
        )

    financial_fig = go.Figure()

    financial_fig.add_trace(
        go.Bar(
            name="Scenario A",
            x=["Cost", "Revenue", "Profit"],
            y=[
                result_a["cost"],
                result_a["revenue"],
                result_a["profit"]
            ]
        )
    )

    financial_fig.add_trace(
        go.Bar(
            name="Scenario B",
            x=["Cost", "Revenue", "Profit"],
            y=[
                result_b["cost"],
                result_b["revenue"],
                result_b["profit"]
            ]
        )
    )

    financial_fig.update_layout(
        barmode="group",
        title="Financial Comparison",
        xaxis_title="Financial Metric",
        yaxis_title="Amount (₹)",
        height=450
    )

    st.plotly_chart(
        financial_fig,
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

    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)

    with impact_col1:
        st.metric(
            "Yield Change",
            f"{yield_difference:+.2f} q"
        )

    with impact_col2:
        if profit_difference < 0:
            impact_profit = f"-₹{abs(profit_difference):,.0f}"
        elif profit_difference > 0:
            impact_profit = f"+₹{profit_difference:,.0f}"
        else:
            impact_profit = "₹0"

        st.metric(
            "Profit Change",
            impact_profit
        )

    with impact_col3:
        st.metric(
            "Risk Change",
            f"{risk_difference:+} points"
        )

    with impact_col4:
        st.metric(
            "Water Usage Change",
            f"{water_difference:+.0f} units"
        )

    st.subheader("💡 Decision Insight")

    no_changes = scenario_a == scenario_b

    if no_changes:
        st.info(
            "Both scenarios have identical simulated outcomes because no factors were changed."
        )

    elif (
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

    if no_changes:
        st.write(
            "• No trade-offs — both scenarios use the same inputs."
        )

    else:
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
            cost_change = result_b["cost"] - result_a["cost"]

            if cost_change < 0:
                cost_text = f"-₹{abs(cost_change):,.0f}"
            else:
                cost_text = f"+₹{cost_change:,.0f}"

            st.write(
                f"• Estimated cost changes by {cost_text}."
            )

    st.subheader("🔎 Factor Impact Analysis")

    impacts = calculate_factor_impacts(
        scenario_a,
        scenario_b
    )

    if impacts:

        impact_data = pd.DataFrame({
            "Factor": [
                impact["factor"]
                for impact in impacts
            ],
            "Yield Impact": [
                f"{impact['yield_impact']:+.2f} q"
                for impact in impacts
            ],
            "Yield Change": [
                f"{impact['yield_percentage']:+.1f}%"
                for impact in impacts
            ],
            "Profit Impact": [
                f"₹{impact['profit_impact']:+,.0f}"
                for impact in impacts
            ],
            "Risk Impact": [
                f"{impact['risk_impact']:+}"
                for impact in impacts
            ]
        })

        st.dataframe(
            impact_data,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Factor impacts show each changed variable individually, "
            "so they do not necessarily add up to the total scenario change."
        )

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

