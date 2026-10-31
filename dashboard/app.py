import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from main import predict_irrigation
from fuzzy_engine.library_fuzzy import predict_with_library
from fuzzy_engine.membership import (
    triangular_membership,
    soil_moisture_fuzzy,
    temperature_fuzzy,
    humidity_fuzzy,
)
from fuzzy_engine.output_membership import irrigation_output_fuzzy


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(
    page_title="AgroSmart | Smart Irrigation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# EDITORIAL DESIGN SYSTEM
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    :root {
        --ink: #20372D;
        --muted: #718077;
        --green: #285B43;
        --green-2: #3F795A;
        --sage: #E6EEE4;
        --paper: #F7F7F1;
        --line: #E3E8DF;
        --white: #FFFFFF;
        --gold: #B8894D;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp { background: var(--paper); color: var(--ink); }
    header[data-testid="stHeader"] { background: rgba(247,247,241,.88); }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px; }

    h1, h2, h3 {
        color: var(--ink) !important;
        letter-spacing: -0.5px;
    }
    h1, h2 { font-family: 'Playfair Display', serif !important; }
    p, label, .stCaption { color: var(--muted); }

    section[data-testid="stSidebar"] {
        background: #F0F2EA;
        border-right: 1px solid #DDE4D9;
    }
    section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 7px 10px;
        border-radius: 9px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--white);
        border: 1px solid var(--line);
        border-radius: 17px;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 16px 18px;
    }
    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div[data-testid="stMetricValue"] {
        color: var(--green);
        font-weight: 700;
    }

    .eyebrow {
        color: #728578;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 10px;
        font-weight: 700;
        margin-bottom: 7px;
    }
    .page-subtitle {
        color: #758178;
        font-size: 15px;
        margin-top: -8px;
        margin-bottom: 22px;
    }
    .hero {
        background: linear-gradient(115deg, #1F4936 0%, #32694B 100%);
        border-radius: 22px;
        padding: 30px 32px;
        color: white;
        margin: 8px 0 22px 0;
        position: relative;
        overflow: hidden;
    }
    .hero-kicker {
        color: #C4D8C8;
        letter-spacing: 2px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(28px, 3vw, 42px);
        line-height: 1.12;
        color: #FFFFFF;
        margin: 10px 0 9px 0;
    }
    .hero-copy {
        color: #DCE9DE;
        max-width: 650px;
        font-size: 14px;
        line-height: 1.65;
    }
    .hero-mark {
        font-size: 68px;
        opacity: .9;
        text-align: right;
    }
    .recommendation {
        background: #FFFFFF;
        border: 1px solid #DCE6DA;
        border-radius: 20px;
        padding: 24px;
        min-height: 210px;
    }
    .recommendation-number {
        font-family: 'Playfair Display', serif;
        color: #285B43;
        font-size: 54px;
        font-weight: 600;
        line-height: 1.05;
    }
    .recommendation-label {
        color: #77857A;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .status-pill {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 30px;
        background: #E7F1E7;
        color: #2E6848;
        font-size: 11px;
        font-weight: 700;
        margin-top: 12px;
    }
    .section-kicker {
        color: #839187;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .small-note {
        color: #7B887E;
        font-size: 12px;
        line-height: 1.5;
    }
    div.stButton > button {
        background: #285B43;
        color: white;
        border: 1px solid #285B43;
        border-radius: 10px;
        padding: 10px 17px;
        font-weight: 700;
    }
    div.stButton > button:hover {
        background: #3F795A;
        border-color: #3F795A;
        color: white;
    }
    div[data-testid="stDownloadButton"] button {
        border-radius: 10px;
        border: 1px solid #CBD8CB;
        color: #285B43;
        background: white;
        font-weight: 600;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] { padding-top: 8px; }
    .footer {
        color: #89948B;
        font-size: 11px;
        text-align: center;
        padding: 18px 0 4px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------
if "soil" not in st.session_state:
    st.session_state.soil = 35
if "temperature" not in st.session_state:
    st.session_state.temperature = 35
if "humidity" not in st.session_state:
    st.session_state.humidity = 40
if "history" not in st.session_state:
    st.session_state.history = []
if "scenario_name" not in st.session_state:
    st.session_state.scenario_name = "Custom readings"


SCENARIOS = {
    "Custom readings": None,
    "Very dry soil": (10, 40, 20),
    "Moderately moist soil": (50, 25, 50),
    "Very wet soil": (90, 25, 80),
    "Hot and dry weather": (25, 45, 20),
    "Cool and humid weather": (60, 10, 90),
}


# ------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="font-family:'Playfair Display',serif;font-size:25px;
                    color:#244B36;font-weight:700;">🌿 AgroSmart</div>
        <div style="font-size:9px;letter-spacing:2px;color:#829084;
                    font-weight:700;margin-top:2px;">INTELLIGENT WATER MANAGEMENT</div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**WORKSPACE & ADVANCED ANALYSIS**")
    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Irrigation Control",
            "Recommendation History",
            "Fuzzy Logic Lab",
            "Membership Functions",
            "Rule Activation",
            "Defuzzification",
            "Engine Comparison",
            "Test Cases & Reports",
        ],
        label_visibility="collapsed",
        key="navigation",
    )
    st.divider()
    st.markdown("**SYSTEM STATUS**")
    st.success("Fuzzy engine operational")
    st.caption("Mamdani inference · Manual + scikit-fuzzy")
    st.caption("Academic prototype · Manual sensor inputs")


# ------------------------------------------------------------
# COMMON CALCULATIONS AND HELPERS
# ------------------------------------------------------------
soil = int(st.session_state.soil)
temperature = int(st.session_state.temperature)
humidity = int(st.session_state.humidity)

result = predict_irrigation(soil, temperature, humidity)
duration = result["irrigation_duration"]
fuzzy_output = result["fuzzy_output"]
activated_rules = result["activated_rules"]


def make_membership_chart(title, x_values, functions, current_value=None, x_title="Input"):
    fig = go.Figure()
    for label, function in functions.items():
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=[function(x) for x in x_values],
                mode="lines",
                name=label,
                line=dict(width=3),
            )
        )
    if current_value is not None:
        fig.add_vline(
            x=current_value,
            line_dash="dash",
            line_width=2,
            line_color="#B8894D",
            annotation_text=f"Current: {current_value}",
        )
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title=x_title,
        yaxis_title="Membership degree",
        yaxis=dict(range=[0, 1.05], gridcolor="#EDF0EA"),
        xaxis=dict(gridcolor="#EDF0EA"),
        template="plotly_white",
        height=310,
        margin=dict(l=15, r=15, t=55, b=35),
        legend=dict(orientation="h", y=-0.25),
        font=dict(family="DM Sans", color="#52675A"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )
    return fig


def output_aggregation_chart(show_centroid=True):
    x_values = list(range(61))
    aggregated = []
    for x in x_values:
        memberships = irrigation_output_fuzzy(x)
        clipped = [
            min(fuzzy_output[name], memberships[name])
            for name in fuzzy_output
        ]
        aggregated.append(max(clipped) if clipped else 0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=aggregated,
            mode="lines",
            fill="tozeroy",
            name="Aggregated output",
            line=dict(color="#397D5B", width=3),
            fillcolor="rgba(57,125,91,0.18)",
        )
    )
    if show_centroid:
        fig.add_vline(
            x=duration,
            line_dash="dash",
            line_color="#B8894D",
            line_width=2,
            annotation_text=f"Centroid {duration:.2f} min",
        )
    fig.update_layout(
        title="Aggregated output and centroid",
        xaxis_title="Irrigation duration (minutes)",
        yaxis_title="Membership degree",
        yaxis=dict(range=[0, 1.05], gridcolor="#EDF0EA"),
        xaxis=dict(gridcolor="#EDF0EA"),
        template="plotly_white",
        height=340,
        margin=dict(l=15, r=15, t=55, b=35),
        font=dict(family="DM Sans", color="#52675A"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )
    return fig


def save_current_result(label=None):
    record = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Scenario": label or st.session_state.scenario_name,
        "Soil moisture (%)": soil,
        "Temperature (°C)": temperature,
        "Humidity (%)": humidity,
        "Recommendation (min)": duration,
    }
    st.session_state.history.insert(0, record)
    st.session_state.history = st.session_state.history[:100]


def apply_scenario(name):
    values = SCENARIOS.get(name)
    if values:
        st.session_state.soil = values[0]
        st.session_state.temperature = values[1]
        st.session_state.humidity = values[2]
    st.session_state.scenario_name = name


def show_sensor_cards():
    a, b, c = st.columns(3)
    with a:
        st.metric("Soil moisture", f"{soil}%", "Input reading")
    with b:
        st.metric("Temperature", f"{temperature} °C", "Input reading")
    with c:
        st.metric("Relative humidity", f"{humidity}%", "Input reading")


def show_rule_list():
    if not activated_rules:
        st.info("No rules were activated for the current readings.")
        return
    for item in activated_rules:
        rule = item["rule"]
        strength = float(item["strength"])
        with st.container(border=True):
            st.markdown(
                f"**IF** soil is {rule['soil']} AND temperature is "
                f"{rule['temperature']} AND humidity is {rule['humidity']} "
                f"**THEN** irrigation is **{rule['output']}**"
            )
            st.progress(max(0.0, min(1.0, strength)))
            st.caption(f"Activation strength: {strength:.3f}")


# ------------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------------
st.markdown('<div class="eyebrow">SMART AGRICULTURE / WATER MANAGEMENT</div>', unsafe_allow_html=True)


# ============================================================
# OVERVIEW — USER-FIRST LANDING PAGE
# ============================================================
if page == "Overview":
    st.title("Good decisions start with better readings.")
    st.markdown(
        '<div class="page-subtitle">Your irrigation overview, powered by a Mamdani fuzzy inference system.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">
          <div class="hero-kicker">AGROSMART · IRRIGATION INTELLIGENCE</div>
          <div class="hero-title">Grow thoughtfully.<br>Use every drop wisely.</div>
          <div class="hero-copy">A decision-support prototype that translates soil and weather
          conditions into an understandable irrigation recommendation.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-kicker">CURRENT ENVIRONMENT</div>', unsafe_allow_html=True)
    show_sensor_cards()

    st.markdown("")
    left, right = st.columns([1.12, 0.88], gap="large")

    with left:
        status = "Irrigation may be needed" if duration >= 15 else "Low irrigation demand"
        st.markdown(
            f"""
            <div class="recommendation">
              <div class="recommendation-label">SYSTEM RECOMMENDATION</div>
              <div class="recommendation-number">{duration:.2f}<span style="font-size:20px;"> min</span></div>
              <div style="color:#66776B;font-size:13px;margin-top:8px;">
                Suggested irrigation duration for the current sensor readings.
              </div>
              <div class="status-pill">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "This duration is a model output, not a direct measurement of water volume. "
            "Actual delivery depends on flow rate and irrigation equipment."
        )

    with right:
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=duration,
                number={"suffix": " min", "font": {"size": 34, "color": "#285B43"}},
                title={"text": "Recommended duration", "font": {"size": 14, "color": "#718077"}},
                gauge={
                    "axis": {"range": [0, 60], "tickcolor": "#829084"},
                    "bar": {"color": "#397D5B"},
                    "bgcolor": "#F1F4EE",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 15], "color": "#EAF0E7"},
                        {"range": [15, 30], "color": "#DCE9D9"},
                        {"range": [30, 45], "color": "#C6DDC8"},
                        {"range": [45, 60], "color": "#A7CBAE"},
                    ],
                },
            )
        )
        gauge.update_layout(
            height=235,
            margin=dict(l=18, r=18, t=45, b=10),
            paper_bgcolor="#F7F7F1",
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

    st.markdown("### What is influencing the decision?")
    explain_col, rules_col = st.columns([0.85, 1.15], gap="large")
    with explain_col:
        if soil < 30:
            soil_text = "Soil moisture is in the dry region."
        elif soil < 70:
            soil_text = "Soil moisture is around the moderate region."
        else:
            soil_text = "Soil moisture is in the wet region."
        if temperature >= 35:
            temp_text = "Temperature is relatively high."
        elif temperature <= 15:
            temp_text = "Temperature is relatively cool."
        else:
            temp_text = "Temperature is in a moderate range."
        if humidity < 35:
            humidity_text = "Humidity is low."
        elif humidity > 65:
            humidity_text = "Humidity is high."
        else:
            humidity_text = "Humidity is in a middle range."
        with st.container(border=True):
            st.markdown("**Reading summary**")
            st.write(soil_text)
            st.write(temp_text)
            st.write(humidity_text)
            st.caption("These are plain-language descriptions of the entered values.")
    with rules_col:
        with st.container(border=True):
            st.markdown("**Most relevant activated rules**")
            if activated_rules:
                for item in sorted(activated_rules, key=lambda x: x["strength"], reverse=True)[:3]:
                    rule = item["rule"]
                    st.write(
                        f"IF soil = {rule['soil']}, temperature = {rule['temperature']}, "
                        f"humidity = {rule['humidity']} → {rule['output']} "
                        f"({item['strength']:.2f})"
                    )
            else:
                st.write("No rules activated.")

    st.markdown("### Quick actions")
    qa, qb, qc = st.columns([1, 1, 1])
    with qa:
        if st.button("Adjust sensor readings", use_container_width=True):
            st.session_state["navigation"] = "Irrigation Control"
            st.rerun()
    with qb:
        if st.button("Explore fuzzy logic", use_container_width=True):
            st.session_state["navigation"] = "Fuzzy Logic Lab"
            st.rerun()
    with qc:
        if st.button("Save this recommendation", use_container_width=True):
            save_current_result()
            st.success("Recommendation saved to session history.")

    st.info(
        "Academic prototype: the membership functions and rule base are heuristic assumptions. "
        "The recommendation has not been calibrated against field measurements."
    )


# ============================================================
# IRRIGATION CONTROL
# ============================================================
elif page == "Irrigation Control":
    st.title("Irrigation control")
    st.markdown(
        '<div class="page-subtitle">Enter current environmental readings and calculate a fresh recommendation.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### Start with a scenario")
        selected = st.selectbox("Choose a preset or use custom readings", list(SCENARIOS.keys()))
        if st.button("Load selected scenario"):
            apply_scenario(selected)
            st.rerun()

    st.markdown("### Environmental readings")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.slider("Soil moisture (%)", 0, 100, key="soil", help="0 = very dry, 100 = very wet.")
    with c2:
        st.slider("Temperature (°C)", 0, 50, key="temperature", help="Supported input range: 0–50°C.")
    with c3:
        st.slider("Humidity (%)", 0, 100, key="humidity", help="Relative humidity input, from 0–100%.")

    soil = int(st.session_state.soil)
    temperature = int(st.session_state.temperature)
    humidity = int(st.session_state.humidity)
    result = predict_irrigation(soil, temperature, humidity)
    duration = result["irrigation_duration"]
    fuzzy_output = result["fuzzy_output"]
    activated_rules = result["activated_rules"]

    st.markdown("### Your recommendation")
    x, y = st.columns([1, 1.2], gap="large")
    with x:
        st.markdown(
            f"""
            <div class="recommendation">
              <div class="recommendation-label">CALCULATED IRRIGATION DURATION</div>
              <div class="recommendation-number">{duration:.2f}<span style="font-size:20px;"> min</span></div>
              <div style="color:#66776B;font-size:13px;margin-top:8px;">
                Based on the current inputs and the project's fuzzy rule base.
              </div>
              <div class="status-pill">Calculation complete</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with y:
        st.markdown("**Input summary**")
        show_sensor_cards()

    if st.button("Save recommendation to history", type="primary"):
        save_current_result()
        st.success("Saved. Open Recommendation History from the sidebar.")

    st.markdown("### Decision explanation")
    st.write(
        f"The model converted soil moisture ({soil}%), temperature ({temperature}°C), "
        f"and humidity ({humidity}%) into fuzzy membership values, evaluated the rules, "
        f"aggregated the output sets, and calculated a crisp duration of {duration:.2f} minutes."
    )
    with st.expander("View activated rules"):
        show_rule_list()


# ============================================================
# RECOMMENDATION HISTORY
# ============================================================
elif page == "Recommendation History":
    st.title("Recommendation history")
    st.markdown(
        '<div class="page-subtitle">Calculations saved during this browser session.</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download history as CSV",
            data=history_df.to_csv(index=False).encode("utf-8"),
            file_name="agrosmart_recommendation_history.csv",
            mime="text/csv",
        )
        if st.button("Clear session history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No saved recommendations yet. Calculate and save one from Irrigation Control.")


# ============================================================
# ADVANCED: FUZZY LOGIC LAB
# ============================================================
elif page == "Fuzzy Logic Lab":
    st.title("Fuzzy logic laboratory")
    st.markdown(
        '<div class="page-subtitle">Inspect how crisp sensor readings are transformed and processed by the Mamdani system.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Current sensor readings")
    show_sensor_cards()

    soil_functions = {
        "Dry": lambda x: triangular_membership(x, 0, 0, 50),
        "Moderate": lambda x: triangular_membership(x, 25, 50, 75),
        "Wet": lambda x: triangular_membership(x, 50, 100, 100),
    }
    temperature_functions = {
        "Cool": lambda x: triangular_membership(x, 0, 0, 25),
        "Normal": lambda x: triangular_membership(x, 15, 25, 35),
        "Hot": lambda x: triangular_membership(x, 25, 50, 50),
    }
    humidity_functions = {
        "Low": lambda x: triangular_membership(x, 0, 0, 50),
        "Medium": lambda x: triangular_membership(x, 25, 50, 75),
        "High": lambda x: triangular_membership(x, 50, 100, 100),
    }

    st.markdown("### 1 · Fuzzification")
    a, b = st.columns(2)
    with a:
        st.plotly_chart(
            make_membership_chart("Soil moisture membership", range(101), soil_functions, soil, "Soil moisture (%)"),
            use_container_width=True,
        )
        st.plotly_chart(
            make_membership_chart("Temperature membership", range(51), temperature_functions, temperature, "Temperature (°C)"),
            use_container_width=True,
        )
    with b:
        st.plotly_chart(
            make_membership_chart("Humidity membership", range(101), humidity_functions, humidity, "Humidity (%)"),
            use_container_width=True,
        )
        with st.container(border=True):
            st.markdown("**Fuzzification values**")
            st.write("Soil moisture")
            st.json(soil_moisture_fuzzy(soil))
            st.write("Temperature")
            st.json(temperature_fuzzy(temperature))
            st.write("Humidity")
            st.json(humidity_fuzzy(humidity))

    st.markdown("### 2 · Rule evaluation")
    show_rule_list()

    st.markdown("### 3 · Aggregation and defuzzification")
    st.plotly_chart(output_aggregation_chart(), use_container_width=True)
    st.metric("Centroid output", f"{duration:.2f} minutes")


# ============================================================
# ADVANCED: MEMBERSHIP FUNCTIONS
# ============================================================
elif page == "Membership Functions":
    st.title("Membership functions")
    st.markdown(
        '<div class="page-subtitle">Explore the triangular and shoulder-shaped fuzzy sets used by the system.</div>',
        unsafe_allow_html=True,
    )
    soil_functions = {
        "Dry": lambda x: triangular_membership(x, 0, 0, 50),
        "Moderate": lambda x: triangular_membership(x, 25, 50, 75),
        "Wet": lambda x: triangular_membership(x, 50, 100, 100),
    }
    temperature_functions = {
        "Cool": lambda x: triangular_membership(x, 0, 0, 25),
        "Normal": lambda x: triangular_membership(x, 15, 25, 35),
        "Hot": lambda x: triangular_membership(x, 25, 50, 50),
    }
    humidity_functions = {
        "Low": lambda x: triangular_membership(x, 0, 0, 50),
        "Medium": lambda x: triangular_membership(x, 25, 50, 75),
        "High": lambda x: triangular_membership(x, 50, 100, 100),
    }
    output_functions = {
        "Very Low": lambda x: triangular_membership(x, 0, 0, 15),
        "Low": lambda x: triangular_membership(x, 0, 15, 30),
        "Medium": lambda x: triangular_membership(x, 15, 30, 45),
        "High": lambda x: triangular_membership(x, 30, 45, 60),
        "Very High": lambda x: triangular_membership(x, 45, 60, 60),
    }
    st.plotly_chart(make_membership_chart("Soil moisture", range(101), soil_functions, soil, "Soil moisture (%)"), use_container_width=True)
    st.plotly_chart(make_membership_chart("Temperature", range(51), temperature_functions, temperature, "Temperature (°C)"), use_container_width=True)
    st.plotly_chart(make_membership_chart("Humidity", range(101), humidity_functions, humidity, "Humidity (%)"), use_container_width=True)
    st.plotly_chart(make_membership_chart("Irrigation output", range(61), output_functions, duration, "Duration (minutes)"), use_container_width=True)


# ============================================================
# ADVANCED: RULE ACTIVATION
# ============================================================
elif page == "Rule Activation":
    st.title("Rule activation")
    st.markdown(
        '<div class="page-subtitle">See which of the 27 generated rules contribute to the current recommendation.</div>',
        unsafe_allow_html=True,
    )
    st.write(f"Current inputs: soil {soil}%, temperature {temperature}°C, humidity {humidity}%.")
    show_rule_list()
    if activated_rules:
        rules_df = pd.DataFrame(
            [
                {
                    "Soil": item["rule"]["soil"],
                    "Temperature": item["rule"]["temperature"],
                    "Humidity": item["rule"]["humidity"],
                    "Output": item["rule"]["output"],
                    "Activation strength": round(float(item["strength"]), 4),
                }
                for item in activated_rules
            ]
        )
        st.markdown("### Rule activation table")
        st.dataframe(rules_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download activated rules",
            data=rules_df.to_csv(index=False).encode("utf-8"),
            file_name="activated_fuzzy_rules.csv",
            mime="text/csv",
        )


# ============================================================
# ADVANCED: DEFUZZIFICATION
# ============================================================
elif page == "Defuzzification":
    st.title("Defuzzification")
    st.markdown(
        '<div class="page-subtitle">Inspect the aggregated output fuzzy set and its centroid crisp value.</div>',
        unsafe_allow_html=True,
    )
    st.latex(r"z^* = \frac{\sum_i z_i\mu(z_i)}{\sum_i \mu(z_i)}")
    st.write(
        "The system samples the output universe from 0 to 60 minutes, clips each output membership "
        "function by its activation strength, combines the clipped sets using maximum, and computes "
        "the discrete centroid."
    )
    st.plotly_chart(output_aggregation_chart(), use_container_width=True)
    st.metric("Defuzzified irrigation duration", f"{duration:.2f} minutes")
    st.markdown("### Aggregated output strengths")
    st.json(fuzzy_output)


# ============================================================
# ADVANCED: ENGINE COMPARISON
# ============================================================
elif page == "Engine Comparison":
    st.title("Fuzzy engine comparison")
    st.markdown(
        '<div class="page-subtitle">Compare the hand-coded Mamdani engine with the scikit-fuzzy implementation.</div>',
        unsafe_allow_html=True,
    )
    test_cases = [
        ("Very Dry Soil", 10, 40, 20),
        ("Moderately Moist Soil", 50, 25, 50),
        ("Very Wet Soil", 90, 25, 80),
        ("Hot and Dry Weather", 25, 45, 20),
        ("Cool and Humid Weather", 60, 10, 90),
    ]
    comparison_data = []
    for name, s, t, h in test_cases:
        manual = predict_irrigation(s, t, h)["irrigation_duration"]
        library = predict_with_library(s, t, h)
        comparison_data.append(
            {
                "Test case": name,
                "Soil (%)": s,
                "Temperature (°C)": t,
                "Humidity (%)": h,
                "Manual engine (min)": manual,
                "scikit-fuzzy (min)": library,
                "Absolute difference (min)": round(abs(manual - library), 2),
            }
        )
    df = pd.DataFrame(comparison_data)
    c1, c2, c3 = st.columns(3)
    c1.metric("Test scenarios", len(df))
    c2.metric("Average absolute difference", f"{df['Absolute difference (min)'].mean():.3f} min")
    c3.metric("Largest difference", f"{df['Absolute difference (min)'].max():.2f} min")
    st.dataframe(df, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Test case"], y=df["Manual engine (min)"], name="Manual engine", marker_color="#397D5B"))
    fig.add_trace(go.Bar(x=df["Test case"], y=df["scikit-fuzzy (min)"], name="scikit-fuzzy", marker_color="#C39A62"))
    fig.update_layout(
        title="Manual vs. scikit-fuzzy recommendations",
        yaxis_title="Duration (minutes)",
        barmode="group",
        template="plotly_white",
        height=390,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="DM Sans", color="#52675A"),
        margin=dict(l=15, r=15, t=55, b=80),
        xaxis=dict(tickangle=-12),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.download_button(
        "Download comparison report",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="fuzzy_engine_comparison.csv",
        mime="text/csv",
    )
    st.caption(
        "Close numerical agreement indicates implementation consistency for these test inputs. "
        "It does not establish real-world irrigation accuracy."
    )


# ============================================================
# ADVANCED: TEST CASES & REPORTS
# ============================================================
elif page == "Test Cases & Reports":
    st.title("Test cases and reports")
    st.markdown(
        "<div class=\"page-subtitle\">Run the project's five predefined environmental scenarios and export the outcomes.</div>",
        unsafe_allow_html=True,
    )
    test_cases = [
        ("Very Dry Soil", 10, 40, 20),
        ("Moderately Moist Soil", 50, 25, 50),
        ("Very Wet Soil", 90, 25, 80),
        ("Hot and Dry Weather", 25, 45, 20),
        ("Cool and Humid Weather", 60, 10, 90),
    ]
    rows = []
    for name, s, t, h in test_cases:
        prediction = predict_irrigation(s, t, h)
        rows.append(
            {
                "Test case": name,
                "Soil moisture (%)": s,
                "Temperature (°C)": t,
                "Humidity (%)": h,
                "Recommended duration (min)": prediction["irrigation_duration"],
                "Activated rules": len(prediction["activated_rules"]),
            }
        )
    test_df = pd.DataFrame(rows)
    st.dataframe(test_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download test report (CSV)",
        data=test_df.to_csv(index=False).encode("utf-8"),
        file_name="smart_irrigation_test_report.csv",
        mime="text/csv",
    )
    st.caption(
        "These are predefined software test scenarios used to inspect expected system behaviour. "
        "They are not field trials or evidence of agronomic performance."
    )


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.divider()
st.markdown(
    '<div class="footer">AGROSMART · Mamdani Fuzzy Logic-Based Smart Irrigation Recommendation System · Academic prototype</div>',
    unsafe_allow_html=True,
)
