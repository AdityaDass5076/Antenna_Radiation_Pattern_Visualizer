import streamlit as st
import numpy as np
import plotly.graph_objs as go
import matplotlib.pyplot as plt

# -------------------- Page Configuration --------------------
st.set_page_config(
    page_title="Antenna Radiation Pattern Visualizer",
    layout="wide",
    page_icon="📡"
)

# -------------------- Antenna Pattern Functions --------------------
def dipole_pattern(length_lambda, theta):
    k = 2 * np.pi
    epsilon = 1e-9
    numerator = np.abs(np.cos(k * length_lambda / 2 * np.cos(theta)) - np.cos(k * length_lambda / 2))
    denominator = np.sin(theta) + epsilon
    pattern = numerator / denominator
    return np.nan_to_num(pattern)

def ula_array_pattern(num_elements, spacing, phase_deg, theta):
    psi = 2 * np.pi * spacing * np.cos(theta) + np.deg2rad(phase_deg)
    numerator = np.sin(num_elements * psi / 2)
    denominator = np.sin(psi / 2) + 1e-9
    af = np.abs(numerator / denominator)
    af = np.nan_to_num(af)
    return af / np.max(af)

def yagi_pattern_stub():
    theta = np.linspace(0, np.pi, 360)
    return np.sin(theta) ** 10

# -------------------- Antenna Configurations --------------------
ANTENNAS = {
    "Half-wave Dipole": {
        "calc": dipole_pattern,
        "params": ["Length (λ)"],
        "description": "Two quarter-wavelength elements, omnidirectional in azimuth."
    },
    "Custom Dipole": {
        "calc": dipole_pattern,
        "params": ["Length (λ)"],
        "description": "Dipole with custom length."
    },
    "Uniform Linear Array (ULA)": {
        "calc": ula_array_pattern,
        "params": ["Number of Elements", "Spacing (λ)", "Progressive Phase (deg)"],
        "description": "Linearly spaced elements for directional beams."
    },
    "Yagi-Uda (Stub)": {
        "calc": yagi_pattern_stub,
        "params": [],
        "description": "Simplified Yagi directional antenna."
    }
}

# -------------------- Sidebar --------------------
st.sidebar.title("Antenna Parameters")

antenna_choice = st.sidebar.selectbox("Select Antenna", list(ANTENNAS.keys()))
freq = st.sidebar.slider("Frequency (MHz)", 100, 3000, 900, 10)
wavelength = 3e8 / (freq * 1e6)

show_2d = st.sidebar.checkbox("Show 2D Polar Plot", value=True)
show_3d = st.sidebar.checkbox("Show 3D Pattern", value=True)
normalize = st.sidebar.checkbox("Normalize Pattern", value=True)

# Parameter inputs
params = ANTENNAS[antenna_choice]["params"]
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

# -------------------- Main --------------------
st.title("📡 Antenna Radiation Pattern Visualizer")
st.markdown(f"**Antenna:** {antenna_choice}")
st.markdown(f"**Frequency:** {freq} MHz | **Wavelength:** {wavelength:.2f} m")

theta = np.linspace(0, np.pi, 360)

if antenna_choice == "Half-wave Dipole":
    pattern = dipole_pattern(0.5, theta)
elif antenna_choice == "Custom Dipole":
    pattern = dipole_pattern(param_values.get("Length (λ)", 0.5), theta)
elif antenna_choice == "Uniform Linear Array (ULA)":
    n = param_values.get("Number of Elements", 4)
    d = param_values.get("Spacing (λ)", 0.5)
    beta = param_values.get("Progressive Phase (deg)", 0)
    pattern = ula_array_pattern(n, d, beta, theta)
elif antenna_choice == "Yagi-Uda (Stub)":
    pattern = yagi_pattern_stub()
else:
    pattern = np.ones_like(theta)

if normalize and np.max(pattern) != 0:
    pattern /= np.max(pattern)

# Beamwidth and Directivity
directivity = np.max(pattern)
half_power = np.where(pattern >= 0.5 * np.max(pattern))[0]
beamwidth = np.rad2deg(theta[half_power[-1]] - theta[half_power[0]]) if len(half_power) > 1 else None

# -------------------- Layout --------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Radiation Pattern")
    if show_2d:
        fig2, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.plot(theta, pattern, color="blue", linewidth=2)
        ax.fill_between(theta, 0, pattern, color="skyblue", alpha=0.4)
        ax.set_title("2D Polar Radiation Pattern")
        st.pyplot(fig2, use_container_width=True)

    if show_3d:
        phi = np.linspace(0, 2 * np.pi, 180)
        THETA, PHI = np.meshgrid(theta, phi)
        R = np.tile(pattern, (len(phi), 1))
        X = R * np.sin(THETA) * np.cos(PHI)
        Y = R * np.sin(THETA) * np.sin(PHI)
        Z = R * np.cos(THETA)

        surf = go.Surface(x=X, y=Y, z=Z, surfacecolor=R, colorscale="Viridis", showscale=False)
        fig3d = go.Figure(data=[surf])
        fig3d.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
        )
        st.plotly_chart(fig3d, use_container_width=True)

with col2:
    st.subheader("Performance Metrics")
    st.markdown(f"**Directivity (normalized gain):** {directivity:.2f}")
    st.markdown(f"**HPBW:** {beamwidth:.2f}°" if beamwidth else "**HPBW:** N/A")
    st.markdown("---")
    st.subheader("Description")
    st.markdown(ANTENNAS[antenna_choice]["description"])

# -------------------- Footer --------------------
st.markdown("---")
st.caption("Developed by Aditya Dass - Streamlit App")

