import streamlit as st
import numpy as np
import plotly.graph_objs as go
import matplotlib.pyplot as plt

# Page config and theming
st.set_page_config(page_title="Advanced Antenna Radiation Pattern Visualizer",
                   layout="wide", page_icon="📡")

# ---------- Helper functions for antenna calculations ----------

def dipole_pattern(length_lambda, theta):
    k = 2 * np.pi
    # Avoid zero division with small epsilon
    epsilon = 1e-9
    numerator = np.abs(np.cos(k * length_lambda / 2 * np.cos(theta)) - np.cos(k * length_lambda / 2))
    denominator = np.sin(theta) + epsilon
    pattern = numerator / denominator
    pattern = np.nan_to_num(pattern)
    return pattern

def ula_array_pattern(num_elements, spacing, phase_deg, theta):
    psi = 2 * np.pi * spacing * np.cos(theta) + np.deg2rad(phase_deg)
    numerator = np.sin(num_elements * psi / 2)
    denominator = np.sin(psi / 2) + 1e-9
    af = np.abs(numerator / denominator)
    af = np.nan_to_num(af)
    return af / np.max(af)

def yagi_pattern_stub():  # Placeholder for simplicity
    # Complex pattern, so we use a dummy pattern here
    theta = np.linspace(0, np.pi, 360)
    pattern = np.sin(theta) ** 10
    return pattern

ANTENNAS = {
    "Half-wave Dipole": {
        "calc": dipole_pattern,
        "params": ["Length (λ)"],
        "description": "A fundamental antenna consisting of two quarter-wavelength elements, omnidirectional in azimuth."
    },
    "Custom Dipole": {
        "calc": dipole_pattern,
        "params": ["Length (λ)"],
        "description": "Similar to half-wave but user-controlled length for learning."
    },
    "Uniform Linear Array (ULA)": {
        "calc": ula_array_pattern,
        "params": ["Number of Elements", "Spacing (λ)", "Progressive Phase (deg)"],
        "description": "Multiple elements spaced linearly to produce directional beams."
    },
    "Yagi-Uda Antenna (Stub)": {
        "calc": yagi_pattern_stub,
        "params": [],
        "description": "Directional antenna with elements acting as reflector/director. (Simplified)"
    },
    # More antennas can be added similarly...
}

# ---------- UI Controls in sidebar ----------

st.sidebar.title("Antenna Parameters & Settings")

antenna_choice = st.sidebar.selectbox("Select Antenna Type", list(ANTENNAS.keys()))
freq = st.sidebar.slider("Frequency (MHz)", 100, 3000, 900, 10)
wavelength = 3e8 / (freq * 1e6)

show_2d = st.sidebar.checkbox("Show 2D Polar Pattern", value=True)
show_3d = st.sidebar.checkbox("Show 3D Pattern", value=True)
normalize = st.sidebar.checkbox("Normalize Pattern (max=1)", value=True)
show_calculations = st.sidebar.checkbox("Show Calculation Details", value=False)
educational_mode = st.sidebar.checkbox("Educational Mode (Step-By-Step)", value=False)
theme_choice = st.sidebar.radio("Choose Theme", ["Light", "Dark"])

# Theme styles
if theme_choice == "Dark":
    bg_color = "#222222"
    fg_color = "#eeeeee"
else:
    bg_color = "#fafafa"
    fg_color = "#111111"

st.markdown(f"""
    <style>
        .reportview-container {{background-color: {bg_color}; color: {fg_color};}}
        .sidebar .sidebar-content {{background-color: {'#333' if theme_choice=='Dark' else '#f5f5f5'}; color: {fg_color};}}
        .stButton>button {{background-color: {'#0a9396' if theme_choice=='Dark' else '#0077b6'}; color: white;}}
    </style>
""", unsafe_allow_html=True)

# ---------- Parameter input per antenna ----------

params = ANTENNAS[antenna_choice]['params']
param_values = {}

for param in params:
    if param == "Length (λ)":
        param_values[param] = st.sidebar.slider(param, 0.1, 2.0, 0.5, 0.01)
    elif param == "Number of Elements":
        param_values[param] = st.sidebar.slider(param, 2, 16, 4, 1)
    elif param == "Spacing (λ)":
        param_values[param] = st.sidebar.slider(param, 0.1, 2.0, 0.5, 0.01)
    elif param == "Progressive Phase (deg)":
        param_values[param] = st.sidebar.slider(param, -180, 180, 0, 1)

# ---------- Main content ----------

st.title("📡 Advanced Antenna Radiation Pattern Visualizer")
st.markdown(f"### Antenna type: **{antenna_choice}**")
st.markdown(f"Frequency: **{freq} MHz** | Wavelength: **{wavelength:.2f} m**")

# Calculate the radiation pattern
theta = np.linspace(0, np.pi, 360)

if antenna_choice == "Half-wave Dipole":
    length_lambda = 0.5
    pattern = dipole_pattern(length_lambda, theta)
elif antenna_choice == "Custom Dipole":
    length_lambda = param_values.get("Length (λ)", 0.5)
    pattern = dipole_pattern(length_lambda, theta)
elif antenna_choice == "Uniform Linear Array (ULA)":
    n = param_values.get("Number of Elements", 4)
    d = param_values.get("Spacing (λ)", 0.5)
    beta = param_values.get("Progressive Phase (deg)", 0)
    pattern = ula_array_pattern(n, d, beta, theta)
elif antenna_choice == "Yagi-Uda Antenna (Stub)":
    pattern = yagi_pattern_stub()
else:
    pattern = np.ones_like(theta)

if normalize:
    pattern /= np.max(pattern)

# Beamwidth and directivity calculations (simplified)
directivity = np.max(pattern)
half_power_indices = np.where(pattern >= 0.5 * np.max(pattern))[0]
if len(half_power_indices) > 1:
    beamwidth = np.rad2deg(theta[half_power_indices[-1]] - theta[half_power_indices[0]])
else:
    beamwidth = None

# Show parameters explanation
with st.expander("Parameters Explanation"):
    for p in params:
        explanation = {
            "Length (λ)": "Normalized antenna length in wavelength units.",
            "Number of Elements": "Number of elements in the antenna array.",
            "Spacing (λ)": "Element spacing in wavelengths.",
            "Progressive Phase (deg)": "Phase difference between elements in degrees."
        }.get(p, "Parameter description not available.")
        st.markdown(f"**{p}:** {explanation}")

# ---------- Show calculation details----------

if show_calculations:
    st.markdown("### Calculation Formulas & Details")
    if antenna_choice in ["Half-wave Dipole", "Custom Dipole"]:
        st.latex(r"""
        E(\theta) = \left| \frac{\cos(\frac{\pi L}{\lambda}\cos\theta ) - \cos(\frac{\pi L}{\lambda})}{\sin\theta} \right|
        """)
        st.markdown(f"Antenna length \(L = {param_values.get('Length (λ)', 0.5)} \lambda\) (or half-wave if fixed)")
    elif antenna_choice == "Uniform Linear Array (ULA)":
        st.latex(r"""
        AF(\theta) = \left| \frac{\sin\left(N \frac{\psi}{2}\right)}{\sin\left(\frac{\psi}{2}\right)} \right|, \quad \psi = 2 \pi d \cos \theta + \beta
        """)
        st.markdown(f"Number of elements \(N = {param_values.get('Number of Elements', 4)}\)")
        st.markdown(f"Spacing \(d = {param_values.get('Spacing (λ)', 0.5)} \lambda\)")
        st.markdown(f"Progressive Phase \(\beta = {param_values.get('Progressive Phase (deg)', 0)}^\circ\)")
    else:
        st.markdown("Calculation formulas not available for this antenna.")

# ---------- Plotting ----------

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Radiation Pattern Visualization")

    tabs = st.tabs(["2D Polar Plot", "3D Pattern", "Theta/Azimuth Cuts"])

    with tabs[0]:
        if show_2d:
            fig2, ax = plt.subplots(subplot_kw={'projection': 'polar'})
            ax.plot(theta, pattern, color='#0077b6', linewidth=2, label=antenna_choice)
            ax.fill_between(theta, 0, pattern, color='#b5e6fa', alpha=0.4)
            ax.set_rticks([])
            ax.set_title(f"2D Polar Radiation Pattern")
            ax.legend(loc="upper right")
            fig2.set_facecolor(bg_color)
            st.pyplot(fig2, use_container_width=True)

    with tabs[1]:
        if show_3d:
            phi = np.linspace(0, 2 * np.pi, 180)
            THETA, PHI = np.meshgrid(theta, phi)
            R = np.tile(pattern, (len(phi), 1))
            X = R * np.sin(THETA) * np.cos(PHI)
            Y = R * np.sin(THETA) * np.sin(PHI)
            Z = R * np.cos(THETA)

            surf = go.Surface(
                x=X, y=Y, z=Z, surfacecolor=R,
                colorscale="Viridis", showscale=True,
                lighting=dict(ambient=0.5, diffuse=0.5, specular=0.1, roughness=0.5, fresnel=0.2),
                lightposition=dict(x=100, y=200, z=0),
            )
            fig3d = go.Figure(data=[surf])
            fig3d.update_layout(
                title=f"3D Radiation Pattern ({antenna_choice})",
                margin=dict(l=0, r=0, t=30, b=0),
                scene=dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    zaxis=dict(visible=False),
                    bgcolor=bg_color,
                ),
                paper_bgcolor=bg_color,
                font_color=fg_color,
            )
            st.plotly_chart(fig3d, use_container_width=True)

    with tabs[2]:
        st.markdown("This shows cross-sections (Azimuth/Theta angle cuts) of the radiation.")
        st.line_chart({"Radiation Pattern": pattern})

with col2:
    st.subheader("Performance Metrics")
    st.markdown(f"**Directivity (normalized gain):** {directivity:.2f}")
    st.markdown(f"**Half-Power Beamwidth (HPBW):** {beamwidth:.2f}°" if beamwidth is not None else "**HPBW:** N/A")
    st.markdown("**Other metrics can be added here...**")

    st.markdown("---")
    st.subheader("Description")
    st.markdown(ANTENNAS[antenna_choice]["description"])

    if educational_mode:
        st.markdown("### Educational Step-By-Step")
        st.markdown("Adjust parameters to see real-time effects on antenna patterns and metrics.")
        st.markdown("""
        - **Frequency:** Controls wavelength and overall size.
        - **Length & Spacing:** Determine beam shape and directionality.
        - **Phase shifts:** Control beam steering in arrays.
        """)

# ---------- AI-powered suggestion (basic) ----------
st.sidebar.markdown("---")
st.sidebar.subheader("AI-Powered Suggestion (Basic)")
if freq < 500:
    st.sidebar.info("Low frequency: consider Dipole or Monopole for simplicity.")
elif freq < 2000:
    st.sidebar.info("Mid frequency: Uniform Linear Array or Yagi recommended.")
else:
    st.sidebar.info("High frequency: Patch or Horn antennas suit best.")

# ---------- Footer ----------
st.markdown("---")
st.markdown("<center>Developed by Aditya Dass - Advanced Streamlit App</center>", unsafe_allow_html=True)
