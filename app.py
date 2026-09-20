import streamlit as st
import plotly.graph_objects as go
from simulation.engine import (
    simulate,
    CROP_DATA,
    calculate_factor_impacts
)

st.set_page_config(
    page_title="FarmWise",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 FarmWise")
st.subheader("Smart Farming Scenario & Decision Simulator")

st.write(
    "Create and compare farming scenarios to understand "
    "yield, water, cost, profit, and risk."
)

st.caption(
    "FarmWise is a simulation-based decision-support prototype. "
    "Results are based on model assumptions and are not agricultural forecasts."
)

st.divider()


def scenario_inputs(title, key):
    st.header(title)

    col1, col2 = st.columns(2)

    with col1:
        crop = st.selectbox(
            "Select Crop",
            list(CROP_DATA.keys()),
            key=f"crop_{key}"
        )

        area = st.number_input(
            "Farm Area (acres)",
            min_value=1.0,
            max_value=100.0,
            value=5.0,
            step=1.0,
            key=f"area_{key}"
        )

        water = st.slider(
            "Water Availability (units/acre)",
            min_value=0,
            max_value=150,
            value=100,
            key=f"water_{key}"
        )

    with col2:
        rainfall = st.selectbox(
            "Rainfall Condition",
            ["Low", "Normal", "High"],
            key=f"rainfall_{key}"
        )

        planting = st.selectbox(
            "Planting Schedule",
            ["On Time", "Delayed"],
            key=f"planting_{key}"
        )

        inputs = st.selectbox(
            "Input Usage",
            ["Low", "Normal", "High"],
            key=f"inputs_{key}"
        )

    return crop, area, water, rainfall, planting, inputs


scenario_a = scenario_inputs("🌱 Scenario A", "a")

st.divider()

scenario_b = scenario_inputs("🌾 Scenario B", "b")

st.divider()


if st.button("🔍 Compare Scenarios", type="primary"):

    result_a = simulate(*scenario_a)
    result_b = simulate(*scenario_b)

    st.header("📊 Scenario Comparison")

    comparison = st.columns(5)

    comparison[0].metric(
        "Expected Yield",
        f"{result_b['yield']} q",
        f"{result_b['yield'] - result_a['yield']:+.2f} q"
    )

    comparison[1].metric(
        "Water Used",
        f"{result_b['water_used']} units",
        f"{result_b['water_used'] - result_a['water_used']:+.2f}"
    )

    comparison[2].metric(
        "Estimated Cost",
        f"₹{result_b['cost']:,.0f}",
        f"₹{result_b['cost'] - result_a['cost']:+,.0f}"
    )

    comparison[3].metric(
        "Expected Profit",
        f"₹{result_b['profit']:,.0f}",
        f"₹{result_b['profit'] - result_a['profit']:+,.0f}"
    )

    comparison[4].metric(
        "Risk Score",
        f"{result_b['risk_score']}/100",
        f"{result_b['risk_score'] - result_a['risk_score']:+d}"
    )

    st.divider()

    st.subheader("📋 Detailed Comparison")

    rows = {
        "Metric": [
            "Crop",
            "Yield (q)",
            "Water Required",
            "Water Available",
            "Water Used",
            "Water Deficit",
            "Cost (₹)",
            "Revenue (₹)",
            "Profit (₹)",
            "Risk Score",
            "Risk Level"
        ],
        "Scenario A": [
            scenario_a[0],
            result_a["yield"],
            result_a["water_required"],
            result_a["water_available"],
            result_a["water_used"],
            result_a["water_deficit"],
            result_a["cost"],
            result_a["revenue"],
            result_a["profit"],
            result_a["risk_score"],
            result_a["risk_level"]
        ],
        "Scenario B": [
            scenario_b[0],
            result_b["yield"],
            result_b["water_required"],
            result_b["water_available"],
            result_b["water_used"],
            result_b["water_deficit"],
            result_b["cost"],
            result_b["revenue"],
            result_b["profit"],
            result_b["risk_score"],
            result_b["risk_level"]
        ]
    }

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("💰 Cost Breakdown")

    cost_rows = {
        "Cost Component": [
            "Input Cost",
            "Irrigation Cost",
            "Labor Cost",
            "Planting Cost",
            "Total Cost"
        ],
        "Scenario A": [
            f"₹{result_a['input_cost']:,.0f}",
            f"₹{result_a['irrigation_cost']:,.0f}",
            f"₹{result_a['labor_cost']:,.0f}",
            f"₹{result_a['planting_cost']:,.0f}",
            f"₹{result_a['cost']:,.0f}"
        ],
        "Scenario B": [
            f"₹{result_b['input_cost']:,.0f}",
            f"₹{result_b['irrigation_cost']:,.0f}",
            f"₹{result_b['labor_cost']:,.0f}",
            f"₹{result_b['planting_cost']:,.0f}",
            f"₹{result_b['cost']:,.0f}"
        ]
    }

    st.dataframe(
        cost_rows,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("💧 Water Resource Analysis")

    water_col1, water_col2, water_col3 = st.columns(3)

    water_col1.metric(
        "Scenario A Water Deficit",
        f"{result_a['water_deficit']:.0f} units"
    )

    water_col2.metric(
        "Scenario B Water Deficit",
        f"{result_b['water_deficit']:.0f} units",
        f"{result_b['water_deficit'] - result_a['water_deficit']:+.0f}"
    )

    water_col3.metric(
        "Scenario B Water Availability",
        f"{result_b['water_available']:.0f} units"
    )

    if result_b["water_deficit"] > 0:
        st.warning(
            f"Scenario B has a water deficit of "
            f"**{result_b['water_deficit']:.0f} units**."
        )
    else:
        st.success(
            "Scenario B has sufficient simulated water availability."
        )

    st.divider()

    st.subheader("📈 Visual Comparison")

    yield_col, water_col = st.columns(2)

    with yield_col:
        yield_chart = go.Figure()

        yield_chart.add_trace(
            go.Bar(
                name="Scenario A",
                x=["Scenario A"],
                y=[result_a["yield"]]
            )
        )

        yield_chart.add_trace(
            go.Bar(
                name="Scenario B",
                x=["Scenario B"],
                y=[result_b["yield"]]
            )
        )

        yield_chart.update_layout(
            title="Expected Yield Comparison",
            yaxis_title="Yield (quintals)",
            showlegend=False
        )

        st.plotly_chart(
            yield_chart,
            use_container_width=True
        )

    with water_col:
        water_chart = go.Figure()

        water_chart.add_trace(
            go.Bar(
                name="Required",
                x=["Scenario A", "Scenario B"],
                y=[
                    result_a["water_required"],
                    result_b["water_required"]
                ]
            )
        )

        water_chart.add_trace(
            go.Bar(
                name="Available",
                x=["Scenario A", "Scenario B"],
                y=[
                    result_a["water_available"],
                    result_b["water_available"]
                ]
            )
        )

        water_chart.update_layout(
            title="Water Requirement vs Availability",
            yaxis_title="Water Units",
            barmode="group"
        )

        st.plotly_chart(
            water_chart,
            use_container_width=True
        )

    financial_chart = go.Figure()

    financial_chart.add_trace(
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

    financial_chart.add_trace(
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

    financial_chart.update_layout(
        title="Financial Comparison",
        barmode="group",
        yaxis_title="₹"
    )

    st.plotly_chart(
        financial_chart,
        use_container_width=True
    )

    st.divider()

    st.subheader("🔍 What Caused the Difference?")

    differences = []

    if scenario_a[0] != scenario_b[0]:
        differences.append(
            f"Crop changed from {scenario_a[0]} to {scenario_b[0]}"
        )

    if scenario_a[1] != scenario_b[1]:
        differences.append(
            f"Farm area changed from {scenario_a[1]} to {scenario_b[1]} acres"
        )

    if scenario_a[2] != scenario_b[2]:
        differences.append(
            f"Water availability changed from {scenario_a[2]} to {scenario_b[2]}"
        )

    if scenario_a[3] != scenario_b[3]:
        differences.append(
            f"Rainfall changed from {scenario_a[3]} to {scenario_b[3]}"
        )

    if scenario_a[4] != scenario_b[4]:
        differences.append(
            f"Planting schedule changed from {scenario_a[4]} to {scenario_b[4]}"
        )

    if scenario_a[5] != scenario_b[5]:
        differences.append(
            f"Input usage changed from {scenario_a[5]} to {scenario_b[5]}"
        )

    if differences:
        st.write(
            "The following factors changed between the two scenarios:"
        )

        for difference in differences:
            st.write(f"• {difference}")

    else:
        st.info(
            "Both scenarios use the same farming conditions."
        )

    yield_difference = result_b["yield"] - result_a["yield"]
    profit_difference = result_b["profit"] - result_a["profit"]
    risk_difference = result_b["risk_score"] - result_a["risk_score"]
    water_difference = result_b["water_used"] - result_a["water_used"]

    st.write("### 📌 Impact Summary")

    if yield_difference > 0:
        st.success(
            f"Scenario B produces **{abs(yield_difference):.2f} q more yield**."
        )

    elif yield_difference < 0:
        st.warning(
            f"Scenario B produces **{abs(yield_difference):.2f} q less yield**."
        )

    else:
        st.info(
            "Both scenarios have the same expected yield."
        )

    if profit_difference > 0:
        st.success(
            f"Scenario B generates **₹{abs(profit_difference):,.0f} more profit**."
        )

    elif profit_difference < 0:
        st.warning(
            f"Scenario B generates **₹{abs(profit_difference):,.0f} less profit**."
        )

    else:
        st.info(
            "Both scenarios have the same expected profit."
        )

    if risk_difference > 0:
        st.warning(
            f"Scenario B has a **{abs(risk_difference)} point higher risk score**."
        )

    elif risk_difference < 0:
        st.success(
            f"Scenario B has a **{abs(risk_difference)} point lower risk score**."
        )

    else:
        st.info(
            "Both scenarios have the same risk score."
        )

    st.divider()

    st.subheader("🧠 Decision Insight")

    if (
        profit_difference > 0
        and risk_difference <= 0
        and result_b["water_deficit"] <= result_a["water_deficit"]
    ):
        st.success(
            "Scenario B shows higher simulated profit with no increase "
            "in simulated risk or water deficit."
        )

    elif (
        profit_difference < 0
        and risk_difference > 0
    ):
        st.warning(
            "Scenario B has lower simulated profit and higher simulated "
            "risk compared with Scenario A."
        )

    elif (
        profit_difference > 0
        and risk_difference > 0
    ):
        st.warning(
            "Scenario B increases simulated profit but also increases "
            "simulated risk. This represents a profit-risk trade-off."
        )

    elif (
        profit_difference < 0
        and risk_difference <= 0
    ):
        st.info(
            "Scenario B reduces simulated profit while also reducing "
            "simulated risk. This represents a risk-return trade-off."
        )

    else:
        st.info(
            "Scenario B produces a mixed result across the simulated "
            "yield, profit, water, and risk measures."
        )

    insight_points = []

    if result_b["water_deficit"] > result_a["water_deficit"]:
        insight_points.append(
            f"Water deficit increases by "
            f"{result_b['water_deficit'] - result_a['water_deficit']:.0f} units."
        )

    elif result_b["water_deficit"] < result_a["water_deficit"]:
        insight_points.append(
            f"Water deficit decreases by "
            f"{result_a['water_deficit'] - result_b['water_deficit']:.0f} units."
        )

    if water_difference > 0:
        insight_points.append(
            f"Water usage increases by {water_difference:.0f} units."
        )

    elif water_difference < 0:
        insight_points.append(
            f"Water usage decreases by {abs(water_difference):.0f} units."
        )

    if result_b["cost"] > result_a["cost"]:
        insight_points.append(
            f"Total simulated cost increases by "
            f"₹{result_b['cost'] - result_a['cost']:,.0f}."
        )

    elif result_b["cost"] < result_a["cost"]:
        insight_points.append(
            f"Total simulated cost decreases by "
            f"₹{result_a['cost'] - result_b['cost']:,.0f}."
        )

    if insight_points:
        st.write("**Key trade-offs:**")

        for point in insight_points:
            st.write(f"• {point}")

    st.divider()

    st.subheader("🔬 Factor Impact Analysis")

    factor_impacts = calculate_factor_impacts(
        scenario_a,
        scenario_b
    )

    if factor_impacts:

        impact_rows = []

        for impact in factor_impacts:
            impact_rows.append({
                "Factor": impact["factor"],
                "Yield Impact (q)": impact["yield_impact"],
                "Yield Change (%)": f"{impact['yield_percentage']:+.1f}%",
                "Profit Impact (₹)": impact["profit_impact"],
                "Risk Impact": f"{impact['risk_impact']:+d}"
            })

        st.dataframe(
            impact_rows,
            use_container_width=True,
            hide_index=True
        )

        top_factor = factor_impacts[0]

        st.info(
            f"**Largest individual yield impact:** "
            f"{top_factor['factor']} "
            f"({top_factor['yield_percentage']:+.1f}% yield)"
        )

    else:
        st.info(
            "No individual factors changed between the scenarios."
        )

    st.divider()

    st.subheader("📊 Risk Breakdown")

    risk_factors = [
        "Water Stress",
        "Weather",
        "Planting",
        "Input Usage"
    ]

    risk_breakdown_rows = []

    for factor in risk_factors:
        risk_breakdown_rows.append({
            "Risk Factor": factor,
            "Scenario A": result_a["risk_breakdown"][factor],
            "Scenario B": result_b["risk_breakdown"][factor]
        })

    risk_breakdown_rows.append({
        "Risk Factor": "Total Risk",
        "Scenario A": result_a["risk_score"],
        "Scenario B": result_b["risk_score"]
    })

    st.dataframe(
        risk_breakdown_rows,
        use_container_width=True,
        hide_index=True
    )

    risk_chart = go.Figure()

    risk_chart.add_trace(
        go.Bar(
            name="Scenario A",
            x=risk_factors,
            y=[
                result_a["risk_breakdown"][factor]
                for factor in risk_factors
            ]
        )
    )

    risk_chart.add_trace(
        go.Bar(
            name="Scenario B",
            x=risk_factors,
            y=[
                result_b["risk_breakdown"][factor]
                for factor in risk_factors
            ]
        )
    )

    risk_chart.update_layout(
        title="Risk Contribution by Factor",
        xaxis_title="Risk Factor",
        yaxis_title="Risk Points",
        barmode="group"
    )

    st.plotly_chart(
        risk_chart,
        use_container_width=True
    )

    st.divider()

    st.subheader("⚠️ Risk & Explanation")

    risk_col1, risk_col2 = st.columns(2)

    with risk_col1:
        st.write("**Scenario A**")

        st.write(
            f"Risk: **{result_a['risk_level']} "
            f"({result_a['risk_score']}/100)**"
        )

        for reason in result_a["reasons"]:
            st.write(f"• {reason}")

    with risk_col2:
        st.write("**Scenario B**")

        st.write(
            f"Risk: **{result_b['risk_level']} "
            f"({result_b['risk_score']}/100)**"
        )

        for reason in result_b["reasons"]:
            st.write(f"• {reason}")

    st.divider()

    with st.expander("ℹ️ Model Assumptions & Limitations"):

        st.write("### Simulation Assumptions")

        st.write(
            "• Water requirement is represented using simulated "
            "water units per acre."
        )

        st.write(
            "• Irrigation cost is assumed at ₹8 per water unit used."
        )

        st.write(
            "• Labor cost is assumed at ₹2,500 per acre."
        )

        st.write(
            "• Planting and field preparation cost is assumed at "
            "₹500 per acre."
        )

        st.write(
            "• Input usage affects both simulated yield and input cost."
        )

        st.write(
            "• Rainfall, planting schedule, water availability and "
            "input usage affect the simulated risk score."
        )

        st.write("### Limitations")

        st.write(
            "• Yield and risk values are model-based estimates "
            "for scenario comparison."
        )

        st.write(
            "• The simulator is not an agricultural forecasting system."
        )

        st.write(
            "• Real farm outcomes depend on soil, location, crop variety, "
            "season, pests, market prices and other factors."
        )