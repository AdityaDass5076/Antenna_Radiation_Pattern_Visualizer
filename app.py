import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Antenna Simulator", layout="wide", page_icon="📡")

# ============================================================
# THEME
# ============================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at center, #0c2d65 0%, #000000 90%);
    color: #c9d1d9;
    font-family: Consolas, monospace;
}
h1,h2,h3 { color:#60a5fa; }
</style>
""", unsafe_allow_html=True)

/* Tables */
table {
    color: white !important;
    background-color: rgba(0,0,0,0.6) !important;
}

thead tr th {
    background-color: #1f2937 !important;
    color: #ffffff !important;
}

tbody tr td {
    color: #ffffff !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    color: white !important;
}

/* Metrics & captions */
.css-1v0mbdj, .css-1wivap2, .stCaption {
    color: #ffffff !important;
}

</style>
""", unsafe_allow_html=True)
# ============================================================
# ANTENNA LIBRARY
# ============================================================
ANTENNAS = {
    "Wire Antennas": ["Half-wave Dipole","Rod / Whip Monopole","Small Loop","Large Loop","Helical","Rubber Duck","Inverted-F (IFA)","PIFA"],
    "Aperture Antennas": ["Waveguide Opening","Horn (Pyramidal)","Horn (Conical)","Slot"],
    "Reflector Antennas": ["Parabolic Dish","Corner Reflector","Flat Sheet Reflector"],
    "Microstrip Patch": ["Rectangular Patch","Patch Array"],
    "Antenna Arrays": ["Yagi-Uda","Log-Periodic Dipole Array","Phased Array","Bow-Tie"],
    "Lens Antennas": ["Convex-Plane","Concave-Plane","Convex-Convex"],
    "Special Antennas": ["Ground Plane","Mast Radiator","Omni-Directional"]
}

# ============================================================
# SIDEBAR CONTROLS
# ============================================================
st.sidebar.title("📡 Antenna Controls")

family = st.sidebar.selectbox("Antenna Family", list(ANTENNAS.keys()))
model = st.sidebar.selectbox("Model", ANTENNAS[family])
frequency = st.sidebar.slider("Frequency (MHz)", 100, 60000, 3000)
gain = st.sidebar.slider("Gain (dBi)", 0, 25, 8)
efficiency = st.sidebar.slider("Efficiency (%)", 10, 100, 85)

elements = st.sidebar.slider("Array Elements", 2, 128, 16)
spacing = st.sidebar.slider("Element Spacing (λ)", 0.1, 2.0, 0.5)
phase = st.sidebar.slider("Phase Shift (deg)", -180, 180, 0)

polarization = st.sidebar.selectbox("Polarization",
    ["Linear (Vertical)","Linear (Horizontal)","Circular (RHCP)","Circular (LHCP)"])

field_region = st.sidebar.radio("Field Region", ["Far Field","Near Field"])

# RF parameters
st.sidebar.subheader("RF Parameters")
Z0 = st.sidebar.number_input("Characteristic Impedance Z0 (Ω)", value=50.0)
ZL = st.sidebar.number_input("Load Impedance ZL (Ω)", value=75.0)
distance = st.sidebar.number_input("Tx-Rx Distance (m)", value=10.0)
tx_power = st.sidebar.number_input("Transmit Power (dBm)", value=20.0)

theta = np.linspace(0, np.pi, 360)
theta_deg = np.rad2deg(theta)

# ============================================================
# RADIATION MODELS
# ============================================================
def array_pattern(N, d, phase, theta):
    psi = 2*np.pi*d*np.cos(theta) + np.deg2rad(phase)
    return np.abs(np.sin(N*psi/2)/(np.sin(psi/2)+1e-9))

def get_pattern(model):
    if "Dipole" in model or "Monopole" in model:
        return np.sin(theta)
    elif "Loop" in model:
        return np.cos(theta)**2
    elif "Helical" in model or "Rubber" in model:
        return np.cos(theta)**3
    elif "Horn" in model or "Waveguide" in model:
        return np.exp(-theta**2)
    elif "Dish" in model or "Reflector" in model:
        return np.cos(theta)**4
    elif "Patch" in model or "IFA" in model:
        return np.cos(theta)
    elif "Yagi" in model or "Log-Periodic" in model or "Phased Array" in model:
        return array_pattern(elements, spacing, phase, theta)
    elif "Bow-Tie" in model:
        return np.abs(np.sin(2*theta))
    elif "Omni" in model:
        return np.ones_like(theta)
    else:
        return np.abs(np.cos(theta))

def apply_polarization(pattern):
    if "Horizontal" in polarization:
        pattern *= np.cos(theta)
    elif "RHCP" in polarization:
        pattern *= (1 + 0.1*np.sin(theta))
    elif "LHCP" in polarization:
        pattern *= (1 - 0.1*np.sin(theta))
    return pattern

pattern = get_pattern(model)
pattern = apply_polarization(pattern)
pattern /= np.max(pattern)

# ============================================================
# METRICS
# ============================================================
half_power = np.max(pattern)/np.sqrt(2)
indices = np.where(pattern >= half_power)[0]
beamwidth = theta_deg[indices[-1]] - theta_deg[indices[0]]
directivity = gain * (efficiency/100)

# ============================================================
# MAIN UI
# ============================================================
st.title("📡 Antenna Simulator")
st.markdown(f"### {family} → **{model}**")

col1, col2 = st.columns([2.5,1])

with col1:
    fig, ax = plt.subplots(subplot_kw={'projection':'polar'})
    ax.plot(theta, pattern)
    ax.set_title("Radiation Pattern")
    st.pyplot(fig)

    # 3D Pattern
    phi = np.linspace(0,2*np.pi,180)
    THETA,PHI = np.meshgrid(theta,phi)
    R = np.tile(pattern,(len(phi),1))
    X = R*np.sin(THETA)*np.cos(PHI)
    Y = R*np.sin(THETA)*np.sin(PHI)
    Z = R*np.cos(THETA)
    fig3d = go.Figure(data=[go.Surface(x=X,y=Y,z=Z,surfacecolor=R)])
    st.plotly_chart(fig3d, use_container_width=True)

with col2:
    st.subheader("Radiation Metrics")
    st.write(f"Beamwidth: {beamwidth:.1f}°")
    st.write(f"Directivity: {directivity:.2f} dBi")

# ============================================================
# RF CALCULATIONS
# ============================================================
st.header("📡 RF Performance Metrics")

gamma = (ZL - Z0)/(ZL + Z0)
gamma_mag = abs(gamma)
VSWR = (1 + gamma_mag)/(1 - gamma_mag)
S11 = 20*np.log10(gamma_mag)
S21 = -20*np.log10(distance + 1e-6)

st.write(f"Reflection Coefficient (Γ): {gamma:.3f}")
st.write(f"Return Loss (S11): {S11:.2f} dB")
st.write(f"VSWR: {VSWR:.2f}")
st.write(f"Transmission Loss (S21): {S21:.2f} dB")

# ============================================================
# SMITH CHART
# ============================================================
st.header("📈 Smith Chart")

z_norm = ZL / Z0
gamma_complex = (z_norm - 1)/(z_norm + 1)

theta_smith = np.linspace(0, 2*np.pi, 400)
circle_x = np.cos(theta_smith)
circle_y = np.sin(theta_smith)

fig_smith = go.Figure()
fig_smith.add_trace(go.Scatter(x=circle_x, y=circle_y, mode='lines', name="Unit Circle"))
fig_smith.add_trace(go.Scatter(
    x=[np.real(gamma_complex)],
    y=[np.imag(gamma_complex)],
    mode='markers+text',
    text=["ZL"],
    textposition="top center"
))
fig_smith.update_layout(title="Smith Chart", xaxis=dict(scaleanchor="y"))
st.plotly_chart(fig_smith, use_container_width=True)

# ============================================================
# IMPEDANCE MATCHING
# ============================================================
st.subheader("🔧 Impedance Matching Tool")
matching = st.selectbox("Matching Network", ["Quarter-Wave Transformer","L-Network"])

if matching == "Quarter-Wave Transformer":
    Zt = np.sqrt(Z0*ZL)
    st.write(f"Required Transformer Impedance: {Zt:.2f} Ω")
else:
    Q = np.sqrt(abs((ZL/Z0)-1))
    st.write(f"Quality Factor (Q): {Q:.2f}")

# ============================================================
# LINK BUDGET CALCULATOR
# ============================================================
st.header("📡 Link Budget Calculator")

wavelength = 300 / frequency
path_loss = 20*np.log10(4*np.pi*distance/wavelength)
rx_power = tx_power + gain - path_loss

st.write(f"Free Space Path Loss: {path_loss:.2f} dB")
st.write(f"Estimated Received Power: {rx_power:.2f} dBm")

# ============================================================
# NEAR VS FAR FIELD
# ============================================================
st.header("Near vs Far Field Comparison")

near_pattern = pattern*(1/(1+theta**2))
near_pattern /= np.max(near_pattern)

fig_nf, ax_nf = plt.subplots(subplot_kw={'projection':'polar'})
ax_nf.plot(theta, near_pattern, label="Near Field")
ax_nf.plot(theta, pattern, label="Far Field")
ax_nf.legend()
st.pyplot(fig_nf)

# ============================================================
# REFERENCE TABLE
# ============================================================

import pandas as pd

st.header("📚 Antenna Quick Reference")

ref_data = pd.DataFrame({
    "Antenna": ["Dipole","Patch","Yagi","Dish","Horn"],
    "Size": ["λ/2","λ/2","Multi","Large","Large"],
    "Gain": ["2.15 dBi","6–9 dBi","10–15 dBi","30+ dBi","10–25 dBi"],
    "Applications": ["TV, RF","WiFi, GPS","TV","Satellite","Radar"]
})

st.dataframe(ref_data, use_container_width=True)

st.caption("Developed by Aditya Dass — Advanced RF Antenna Research Tool")
