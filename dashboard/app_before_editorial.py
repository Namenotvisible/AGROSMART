import sys
from pathlib import Path

# Make the main project folder accessible to Python
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
    humidity_fuzzy
)
from fuzzy_engine.output_membership import irrigation_output_fuzzy


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AgroSmart | Intelligent Irrigation",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM DESIGN / CSS
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #F5F6F0;
    color: #20392F;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: #173D32;
    border-right: 1px solid #315849;
}

section[data-testid="stSidebar"] * {
    color: #F0F5EF !important;
}

section[data-testid="stSidebar"] .stRadio label {
    padding: 10px 12px;
    border-radius: 10px;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: #20392F !important;
    letter-spacing: -0.7px;
}

p, label {
    color: #607368;
}

div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E6EBE3;
    padding: 18px;
    border-radius: 16px;
}

div[data-testid="stMetricValue"] {
    color: #245B43;
    font-weight: 800;
}

div[data-testid="stButton"] button {
    background: #245B43;
    color: white;
    border: 0;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 700;
}

div[data-testid="stButton"] button:hover {
    background: #347657;
    color: white;
    border: 0;
}

div[data-testid="stTabs"] button {
    font-weight: 700;
}

div[data-testid="stProgress"] > div > div {
    background-color: #4C9972;
}

.agro-eyebrow {
    color: #72917E;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.agro-subtitle {
    color: #718176;
    font-size: 15px;
}

.hero-card {
    background: linear-gradient(115deg, #173D32, #285D45);
    padding: 28px;
    border-radius: 22px;
    color: white;
    min-height: 220px;
    margin-bottom: 20px;
}

.hero-card h2 {
    color: white !important;
    font-size: 30px;
    margin-bottom: 8px;
}

.hero-card p {
    color: #D4E4D8;
    max-width: 480px;
}

.hero-tag {
    display: inline-block;
    background: #315F4B;
    color: #DDF1DF;
    border: 1px solid #648B70;
    border-radius: 30px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

.section-label {
    color: #789080;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border: 1px solid #E6EBE3;
    border-radius: 16px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("# 🌱 AGROSMART")
    st.caption("INTELLIGENT FARMING SYSTEM")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Fuzzy Logic Lab",
            "Engine Comparison"
        ]
    )

    st.divider()

    st.markdown("### SYSTEM STATUS")
    st.success("Fuzzy engine operational")

    st.caption("Mamdani inference system")
    st.caption("Manual + scikit-fuzzy")


# --------------------------------------------------
# INPUT CONTROLS
# --------------------------------------------------

st.markdown('<div class="agro-eyebrow">SMART AGRICULTURE / CONTROL CENTRE</div>',
            unsafe_allow_html=True)

st.title("Smart Irrigation System")

st.markdown(
    '<p class="agro-subtitle">Intelligent water management powered by Mamdani fuzzy logic.</p>',
    unsafe_allow_html=True
)

with st.sidebar:

    st.markdown("## 🌦️ Environmental Inputs")

    soil = st.slider(
        "Soil moisture (%)",
        0, 100, 35
    )

    temperature = st.slider(
        "Temperature (°C)",
        0, 50, 35
    )

    humidity = st.slider(
        "Humidity (%)",
        0, 100, 40
    )

    st.divider()

    st.caption("Adjust the inputs to update the prediction.")


# Run the existing manual fuzzy engine
result = predict_irrigation(
    soil,
    temperature,
    humidity
)

duration = result["irrigation_duration"]
fuzzy_output = result["fuzzy_output"]
activated_rules = result["activated_rules"]


# --------------------------------------------------
# HELPER: PLOT MEMBERSHIP FUNCTIONS
# --------------------------------------------------

def membership_chart(title, x_values, membership_functions,
                     current_value=None, x_title="Input value"):

    fig = go.Figure()

    for label, function in membership_functions.items():

        y_values = [function(x) for x in x_values]

        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines",
            name=label,
            line=dict(width=3)
        ))

    if current_value is not None:
        fig.add_vline(
            x=current_value,
            line_dash="dash",
            line_width=2,
            line_color="#D18B43"
        )

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title="Membership degree",
        yaxis=dict(range=[0, 1.05]),
        template="plotly_white",
        height=320,
        margin=dict(l=15, r=15, t=55, b=35),
        legend=dict(orientation="h", y=-0.25),
        font=dict(family="DM Sans", color="#40594B"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF"
    )

    return fig


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    # Illustrated farm scene
    farm_svg = """
    <div style="background:linear-gradient(110deg,#173D32,#285D45);
                border-radius:20px;padding:22px;color:white;overflow:hidden;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:11px;letter-spacing:2px;color:#B7D6BD;">
            YOUR FARM / LIVE OVERVIEW
          </div>
          <div style="font-size:27px;font-weight:800;margin-top:8px;">
            Grow smarter. Save water.
          </div>
          <div style="color:#D4E4D8;font-size:14px;margin-top:7px;">
            Let fuzzy intelligence guide your irrigation decisions.
          </div>
        </div>
        <div style="font-size:55px;">🌤️</div>
      </div>
      <svg viewBox="0 0 900 190" width="100%" xmlns="http://www.w3.org/2000/svg">
        <path d="M0 100 Q180 10 360 95 T720 80 T900 90 L900 190 L0 190Z"
              fill="#477A50"/>
        <path d="M0 130 Q180 55 360 130 T720 110 T900 120 L900 190 L0 190Z"
              fill="#6C985A"/>
        <path d="M0 160 Q200 105 400 155 T800 145 L900 150 L900 190 L0 190Z"
              fill="#A3B978"/>
        <g fill="#D5E6B5">
          <path d="M100 130 Q85 95 100 70 Q115 95 100 130Z"/>
          <path d="M100 130 Q70 105 60 85 Q90 90 100 130Z"/>
          <path d="M100 130 Q130 105 140 85 Q110 90 100 130Z"/>
          <path d="M100 130 L100 165" stroke="#D5E6B5" stroke-width="4"/>
          <path d="M260 145 Q245 110 260 85 Q275 110 260 145Z"/>
          <path d="M260 145 Q230 120 220 100 Q250 105 260 145Z"/>
          <path d="M260 145 Q290 120 300 100 Q270 105 260 145Z"/>
          <path d="M260 145 L260 175" stroke="#D5E6B5" stroke-width="4"/>
          <path d="M470 130 Q455 95 470 70 Q485 95 470 130Z"/>
          <path d="M470 130 Q440 105 430 85 Q460 90 470 130Z"/>
          <path d="M470 130 Q500 105 510 85 Q480 90 470 130Z"/>
          <path d="M470 130 L470 165" stroke="#D5E6B5" stroke-width="4"/>
          <path d="M700 145 Q685 110 700 85 Q715 110 700 145Z"/>
          <path d="M700 145 Q670 120 660 100 Q690 105 700 145Z"/>
          <path d="M700 145 Q730 120 740 100 Q710 105 700 145Z"/>
          <path d="M700 145 L700 175" stroke="#D5E6B5" stroke-width="4"/>
        </g>
        <path d="M20 174 Q220 155 420 174 T880 170"
              stroke="#D9E7C2" stroke-width="3" fill="none" opacity=".8"/>
        <path d="M20 185 Q220 166 420 185 T880 181"
              stroke="#D9E7C2" stroke-width="3" fill="none" opacity=".8"/>
      </svg>
    </div>
    """

    st.markdown(farm_svg, unsafe_allow_html=True)

    st.markdown("### Environmental conditions")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("💧 Soil moisture", f"{soil}%")

    with c2:
        st.metric("🌡️ Temperature", f"{temperature}°C")

    with c3:
        st.metric("☁️ Humidity", f"{humidity}%")

    st.markdown("### Irrigation recommendation")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=duration,
        number={
            "suffix": " min",
            "font": {"size": 38, "color": "#245B43"}
        },
        title={
            "text": "Recommended irrigation duration",
            "font": {"size": 16, "color": "#526B5D"}
        },
        gauge={
            "axis": {
                "range": [0, 60],
                "tickwidth": 1,
                "tickcolor": "#8A9B8E"
            },
            "bar": {"color": "#397D5B"},
            "bgcolor": "#F0F4ED",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 15], "color": "#E5EFE3"},
                {"range": [15, 30], "color": "#D0E4D1"},
                {"range": [30, 45], "color": "#B4D5BA"},
                {"range": [45, 60], "color": "#8FB99B"}
            ]
        }
    ))

    gauge.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=60, b=20),
        paper_bgcolor="#FFFFFF",
        font=dict(family="DM Sans")
    )

    st.plotly_chart(gauge, use_container_width=True)

    st.info(
        "This is a prototype recommendation based on the current "
        "membership functions and rule base, not a calibrated farm prescription."
    )

    st.markdown("### Active fuzzy rules")

    if activated_rules:

        for item in activated_rules:

            rule = item["rule"]
            strength = item["strength"]

            with st.container(border=True):

                st.write(
                    f"**IF** soil is {rule['soil']} AND "
                    f"temperature is {rule['temperature']} AND "
                    f"humidity is {rule['humidity']} **THEN** "
                    f"irrigation is {rule['output']}"
                )

                st.progress(float(strength))
                st.caption(f"Activation strength: {strength:.2f}")

    else:
        st.warning("No fuzzy rules were activated for these inputs.")


# --------------------------------------------------
# FUZZY LOGIC LAB PAGE
# --------------------------------------------------

elif page == "Fuzzy Logic Lab":

    st.markdown("Explore how numerical inputs become fuzzy values.")

    st.markdown("### 1. Input membership functions")

    soil_functions = {
        "Dry": lambda x: triangular_membership(x, 0, 0, 50),
        "Moderate": lambda x: triangular_membership(x, 25, 50, 75),
        "Wet": lambda x: triangular_membership(x, 50, 100, 100)
    }

    temperature_functions = {
        "Cool": lambda x: triangular_membership(x, 0, 0, 25),
        "Normal": lambda x: triangular_membership(x, 15, 25, 35),
        "Hot": lambda x: triangular_membership(x, 25, 50, 50)
    }

    humidity_functions = {
        "Low": lambda x: triangular_membership(x, 0, 0, 50),
        "Medium": lambda x: triangular_membership(x, 25, 50, 75),
        "High": lambda x: triangular_membership(x, 50, 100, 100)
    }

    st.plotly_chart(
        membership_chart(
            "Soil moisture",
            list(range(101)),
            soil_functions,
            soil,
            "Soil moisture (%)"
        ),
        use_container_width=True
    )

    st.plotly_chart(
        membership_chart(
            "Temperature",
            list(range(51)),
            temperature_functions,
            temperature,
            "Temperature (°C)"
        ),
        use_container_width=True
    )

    st.plotly_chart(
        membership_chart(
            "Humidity",
            list(range(101)),
            humidity_functions,
            humidity,
            "Humidity (%)"
        ),
        use_container_width=True
    )

    st.markdown("### 2. Fuzzification results")

    soil_values = soil_moisture_fuzzy(soil)
    temperature_values = temperature_fuzzy(temperature)
    humidity_values = humidity_fuzzy(humidity)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Soil moisture**")
        st.json(soil_values)

    with col2:
        st.write("**Temperature**")
        st.json(temperature_values)

    with col3:
        st.write("**Humidity**")
        st.json(humidity_values)

    st.markdown("### 3. Output membership functions")

    output_functions = {
        "Very Low": lambda x: triangular_membership(x, 0, 0, 15),
        "Low": lambda x: triangular_membership(x, 0, 15, 30),
        "Medium": lambda x: triangular_membership(x, 15, 30, 45),
        "High": lambda x: triangular_membership(x, 30, 45, 60),
        "Very High": lambda x: triangular_membership(x, 45, 60, 60)
    }

    st.plotly_chart(
        membership_chart(
            "Irrigation duration",
            list(range(61)),
            output_functions,
            None,
            "Duration (minutes)"
        ),
        use_container_width=True
    )

    st.markdown("### 4. Aggregated fuzzy output")

    output_fig = go.Figure()

    x_values = list(range(61))
    aggregated = []

    for x in x_values:

        membership = irrigation_output_fuzzy(x)
        activated = [
            min(fuzzy_output[category], membership[category])
            for category in fuzzy_output
        ]

        aggregated.append(max(activated))

    output_fig.add_trace(go.Scatter(
        x=x_values,
        y=aggregated,
        mode="lines",
        fill="tozeroy",
        name="Aggregated output",
        line=dict(color="#397D5B", width=3)
    ))

    output_fig.add_vline(
        x=duration,
        line_dash="dash",
        line_color="#D18B43",
        annotation_text=f"Centroid: {duration} min"
    )

    output_fig.update_layout(
        title="Mamdani aggregation and centroid result",
        xaxis_title="Irrigation duration (minutes)",
        yaxis_title="Membership degree",
        yaxis=dict(range=[0, 1.05]),
        template="plotly_white",
        height=350
    )

    st.plotly_chart(output_fig, use_container_width=True)


# --------------------------------------------------
# ENGINE COMPARISON PAGE
# --------------------------------------------------

elif page == "Engine Comparison":

    st.markdown(
        "Compare the manually implemented fuzzy engine "
        "with the scikit-fuzzy implementation."
    )

    test_cases = [
        ("Very Dry Soil", 10, 40, 20),
        ("Moderately Moist Soil", 50, 25, 50),
        ("Very Wet Soil", 90, 25, 80),
        ("Hot and Dry Weather", 25, 45, 20),
        ("Cool and Humid Weather", 60, 10, 90)
    ]

    comparison_data = []

    for name, s, t, h in test_cases:

        manual = predict_irrigation(s, t, h)["irrigation_duration"]

        library = predict_with_library(s, t, h)

        difference = abs(manual - library)

        comparison_data.append({
            "Test case": name,
            "Manual engine (min)": manual,
            "Library engine (min)": library,
            "Difference (min)": round(difference, 2)
        })

    df = pd.DataFrame(comparison_data)

    st.markdown("### Results")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    average_difference = df["Difference (min)"].mean()

    st.metric(
        "Average absolute difference",
        f"{average_difference:.3f} minutes"
    )

    comparison_fig = go.Figure()

    comparison_fig.add_trace(go.Bar(
        x=df["Test case"],
        y=df["Manual engine (min)"],
        name="Manual engine",
        marker_color="#397D5B"
    ))

    comparison_fig.add_trace(go.Bar(
        x=df["Test case"],
        y=df["Library engine (min)"],
        name="scikit-fuzzy",
        marker_color="#D4A45D"
    ))

    comparison_fig.update_layout(
        title="Manual vs library recommendations",
        yaxis_title="Irrigation duration (minutes)",
        barmode="group",
        template="plotly_white",
        height=400
    )

    st.plotly_chart(comparison_fig, use_container_width=True)

    st.caption(
        "Small numerical differences can arise from implementation "
        "and numerical-resolution details. Agreement is not proof "
        "of real-world irrigation accuracy."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AGROSMART | Mamdani Fuzzy Logic-Based Smart Irrigation "
    "Recommendation System | Academic prototype"
)