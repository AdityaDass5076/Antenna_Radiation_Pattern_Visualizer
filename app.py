import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# -------------------- Page Configuration ---------------------
st.set_page_config(
    page_title="Antenna Radiation Pattern Visualizer",
    layout="wide",
    page_icon="📡"
)

# ---------------- Space Galaxy Themed CSS -------------------
st.markdown(
    """
    <style>
    /* Gradient background from dark blue to black */
    .stApp {
        background: radial-gradient(circle at center, #0c2d65 0%, #000000 90%);
        color: #c9d1d9;
        font-family: 'Consolas', monospace;
        min-height: 100vh;
    }
    /* Sidebar background */
    .sidebar-content {
        background: linear-gradient(180deg, #143a8a 0%, #000000 100%);
        color: #a9c1ff;
    }
    /* Headings color */
    h1, h2, h3, h4, h5, h6 {
        color: #60a5fa;
    }
    /* Labels and slider text */
    label, .st-bs > label {
        color: #60a5fa !important;
        font-weight: bold;
    }
    /* Checkbox text */
    .stCheckboxLabel, .stSelectbox > label {
        color: #60a5fa !important;
        font-weight: bold;
    }
    /* Add starry background */
    body::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: transparent url("https://i.postimg.cc/d0nq7Lvq/stars.png") repeat;
        background-size: cover;
        z-index: -1;
        pointer-events: none;
        opacity: 0.4;
        animation: twinkle 20s linear infinite;
    }
    @keyframes twinkle {
        0%, 100% {opacity: 0.4;}
        50% {opacity: 0.7;}
    }
    /* Moon and planets image in sidebar */
    .sidebar-content::after {
        content: "";
        position: absolute;
        bottom: 10px; right: 10px;
        width: 150px; height: 150px;
        background-image: url("https://i.postimg.cc/3R3jB75C/moon-planets.png");
        background-size: contain;
        background-repeat: no-repeat;
        opacity: 0.3;
        pointer-events: none;
    }
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #031a47;
    }
    ::-webkit-scrollbar-thumb {
        background: #5082f5;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Antenna Categories and Models --------------
ANTENNA_CATEGORIES = {
    "Wire Antennas": {
        "Dipole Antenna": ["Antenna Length (L, m)", "Operating Frequency (f, MHz)", "Feed Point", "Polarization", "Ground Plane Height (m)"],
        "Monopole Antenna": ["Antenna Length (L, m)", "Operating Frequency (f, MHz)", "Feed Point", "Ground Plane Height (m)"],
        "Loop Antenna (Small Loop)": ["Aperture Size (m²)", "Operating Frequency (f, MHz)", "Polarization"],
        "Loop Antenna (Large Loop)": ["Aperture Size (m²)", "Operating Frequency (f, MHz)", "Polarization"],
        "Helical Antenna (Normal-mode)": ["Antenna Length (L, m)", "Operating Frequency (f, MHz)", "Phase Difference (deg)", "Polarization"],
        "Helical Antenna (Axial-mode)": ["Antenna Length (L, m)", "Operating Frequency (f, MHz)", "Phase Difference (deg)", "Polarization"]
    },
    "Aperture Antennas": {
        "Horn Antenna": ["Aperture Size (m²)", "Operating Frequency (f, MHz)", "Feed Point"],
        "Slot Antenna": ["Aperture Size (m²)", "Operating Frequency (f, MHz)", "Polarization"],
        "Waveguide Aperture": ["Aperture Size (m²)", "Operating Frequency (f, MHz)"]
    },
    "Array Antennas": {
        "Linear Array": ["Array Elements (N)", "Element Spacing (d, λ)", "Amplitude Distribution", "Phase Difference (deg)", "Operating Frequency (f, MHz)"],
        "Planar Array": ["Array Elements (N)", "Element Spacing (d, λ)", "Amplitude Distribution", "Phase Difference (deg)", "Operating Frequency (f, MHz)"],
        "Circular Array": ["Array Elements (N)", "Element Spacing (d, λ)", "Phase Difference (deg)", "Operating Frequency (f, MHz)"],
        "Phased Array": ["Array Elements (N)", "Element Spacing (d, λ)", "Amplitude Distribution", "Phase Difference (deg)", "Operating Frequency (f, MHz)"]
    },
    "Smart Antennas": {
        "Smart Adaptive Antenna": ["Array Elements (N)", "Element Spacing (d, λ)", "Operating Frequency (f, MHz)"]
    },
    "Reflector Antennas": {
        "Parabolic Reflector": ["Aperture Size (m²)", "Operating Frequency (f, MHz)", "Reflectors / Directors"],
        "Corner Reflector": ["Aperture Size (m²)", "Operating Frequency (f, MHz)", "Reflectors / Directors"],
        "Cassegrain Antenna": ["Aperture Size (m²)", "Operating Frequency (f, MHz)", "Reflectors / Directors"]
    },
    "Lens Antennas": {
        "Dielectric Lens": ["Aperture Size (m²)", "Operating Frequency (f, MHz)"],
        "Metal Plate Lens": ["Aperture Size (m²)", "Operating Frequency (f, MHz)"]
    },
    "Printed / Integrated Antennas": {
        "Microstrip Patch Antenna": ["Antenna Length (L, m)", "Operating Frequency (f, MHz)", "Feed Point"],
        "Planar Inverted-F Antenna (PIFA)": ["Antenna Length (L, m)", "Operating Frequency (f, MHz)", "Feed Point"],
        "Slot-loaded Patch": ["Aperture Size (m²)", "Operating Frequency (f, MHz)"]
    }
}

# ---------------- Parameter Inputs ---------------------------
def get_param_input(param):
    """Return Streamlit widget based on parameter name."""
    if param == "Antenna Length (L, m)":
        return st.sidebar.slider(param, 0.01, 5.0, 0.5, 0.01)
    elif param == "Aperture Size (m²)":
        return st.sidebar.slider(param, 0.01, 10.0, 1.0, 0.01)
    elif param == "Operating Frequency (f, MHz)":
        return st.sidebar.slider(param, 100, 3000, 900, 10)
    elif param == "Feed Point":
        return st.sidebar.selectbox(param, ["Center-fed", "End-fed", "Off-center"])
    elif param == "Array Elements (N)":
        return st.sidebar.slider(param, 2, 32, 8, 1)
    elif param == "Element Spacing (d, λ)":
        return st.sidebar.slider(param, 0.1, 2.0, 0.5, 0.01)
    elif param == "Amplitude Distribution":
        return st.sidebar.selectbox(param, ["Uniform", "Tapered"])
    elif param == "Phase Difference (deg)":
        return st.sidebar.slider(param, -180, 180, 0, 1)
    elif param == "Polarization":
        return st.sidebar.selectbox(param, ["Linear", "Circular", "Elliptical"])
    elif param == "Ground Plane Height (m)":
        return st.sidebar.slider(param, 0.0, 10.0, 1.0, 0.1)
    elif param == "Reflectors / Directors":
        return st.sidebar.slider(param, 0, 5, 0, 1)
    else:
        return None

# ---------------- Basic Radiation Pattern Functions ------------
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

def gaussian(x, a, mu, sigma, offset):
    return a * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2)) + offset

def calculate_gaussian_metrics(theta_deg, pattern_norm):
    max_idx = np.argmax(pattern_norm)
    window_deg = 20
    indices = np.where((theta_deg >= theta_deg[max_idx] - window_deg) & (theta_deg <= theta_deg[max_idx] + window_deg))[0]
    if len(indices) < 5:
        return None
    xdata = theta_deg[indices]
    ydata = pattern_norm[indices]
    p0 = [np.max(ydata), theta_deg[max_idx], 5.0, np.min(ydata)]
    try:
        popt, _ = curve_fit(gaussian, xdata, ydata, p0=p0)
    except RuntimeError:
        return None
    a, mu, sigma, offset = popt
    main_lobe_magnitude = a + offset
    main_lobe_direction = mu
    angular_width = 2.355 * sigma
    outside_mask = (theta_deg < mu - window_deg) | (theta_deg > mu + window_deg)
    side_lobes = pattern_norm[outside_mask]
    side_lobe_level = np.max(side_lobes) if len(side_lobes) > 0 else 0
    return {
        "main_lobe_magnitude": main_lobe_magnitude,
        "main_lobe_direction": main_lobe_direction,
        "angular_width": angular_width,
        "side_lobe_level": side_lobe_level
    }

# -------------------- Plotting functions -----------------------
def plot_2d_polar(theta, pattern, title="2D Polar Radiation Pattern"):
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6, 6))
    ax.plot(theta, pattern, color='cyan', linewidth=2, label='Normalized Radiation Pattern')
    ax.fill_between(theta, 0, pattern, color='deepskyblue', alpha=0.3)
    ax.set_title(title, color='white', fontsize=14)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rticks([0.25, 0.5, 0.75, 1.0])
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(color='gray', linestyle='--', alpha=0.4)
    ax.set_xlabel('Theta (radians)', color='white')
    ax.set_ylabel('Normalized Gain', color='white')
    return fig

def plot_3d_surface(pattern, theta):
    phi = np.linspace(0, 2 * np.pi, 180)
    THETA, PHI = np.meshgrid(theta, phi)
    R = np.tile(pattern, (len(phi), 1))
    X = R * np.sin(THETA) * np.cos(PHI)
    Y = R * np.sin(THETA) * np.sin(PHI)
    Z = R * np.cos(THETA)
    surf = go.Surface(x=X, y=Y, z=Z, surfacecolor=R, colorscale="Turbo", showscale=True, colorbar=dict(title='Normalized Gain'))
    fig3d = go.Figure(data=[surf])
    fig3d.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        title="3D Radiation Pattern",
        font=dict(color='lightblue'),
        paper_bgcolor='#0c2d65',
        plot_bgcolor='#0c2d65',
    )
    # Add legend text as annotations for color info
    fig3d.add_annotation(text="Color bar: Normalized Gain (0 to 1)", x=0.5, y=1.02, xref="paper", yref="paper",
                         showarrow=False, font=dict(color='lightblue', size=12), align="center")
    return fig3d

# -------------------- Sidebar Inputs ---------------------------
st.sidebar.title("Antenna Design Parameters")
antenna_category = st.sidebar.selectbox("Select Antenna Type", list(ANTENNA_CATEGORIES.keys()))
antenna_model = st.sidebar.selectbox("Select Antenna Model", list(ANTENNA_CATEGORIES[antenna_category].keys()))

params_list = ANTENNA_CATEGORIES[antenna_category][antenna_model]

param_values = {}
for param in params_list:
    val = get_param_input(param)
    param_values[param] = val

theta = np.linspace(0, np.pi, 360)
theta_deg = np.rad2deg(theta)

# -------------------- Pattern Calculation ---------------------
if antenna_model in ["Dipole Antenna", "Monopole Antenna"]:
    length_lambda = param_values.get("Antenna Length (L, m)", 0.5)
    freq = param_values.get("Operating Frequency (f, MHz)", 900)
    wavelength = 3e8 / (freq * 1e6)
    normalized_length = length_lambda / wavelength
    pattern = dipole_pattern(normalized_length, theta)
elif antenna_model == "Linear Array":
    n = param_values.get("Array Elements (N)", 8)
    d = param_values.get("Element Spacing (d, λ)", 0.5)
    phase = param_values.get("Phase Difference (deg)", 0)
    pattern = ula_array_pattern(n, d, phase, theta)
else:
    pattern = np.abs(np.cos(theta) ** 3)
pattern = np.nan_to_num(pattern)
pattern /= np.max(pattern)

# -------------------- Radiated Metrics --------------------------
metrics = calculate_gaussian_metrics(theta_deg, pattern)
if not metrics:
    metrics = {
        "main_lobe_magnitude": np.max(pattern),
        "main_lobe_direction": float(theta_deg[np.argmax(pattern)]),
        "angular_width": None,
        "side_lobe_level": None
    }

# -------------------- Layout -----------------------------
st.title("📡 Antenna Radiation Pattern Visualizer")
st.markdown(f"### Antenna Type: **{antenna_category}**  |  Model: **{antenna_model}**")
freq_display = param_values.get("Operating Frequency (f, MHz)", "N/A")
st.markdown(f"### Operating Frequency: **{freq_display} MHz**")

col1, col2 = st.columns([2.5, 1])

with col1:
    st.subheader("Radiation Pattern Visualization")

    show_2d = st.checkbox("Show 2D Polar Plot", value=True)
    show_3d = st.checkbox("Show 3D Radiation Pattern", value=True)

    if show_2d:
        fig2d = plot_2d_polar(theta, pattern)
        st.pyplot(fig2d, use_container_width=True)

    if show_3d:
        fig3d = plot_3d_surface(pattern, theta)
        st.plotly_chart(fig3d, use_container_width=True)

with col2:
    st.subheader("Key Radiation Metrics & Observation")
    st.markdown(f"- **Main Lobe Magnitude:** {metrics['main_lobe_magnitude']:.3f} (Ideal > 0.7)")
    st.markdown(f"- **Main Lobe Direction:** {metrics['main_lobe_direction']:.1f}° (0° means main beam is zenith/upwards)")
    if metrics['angular_width'] is not None:
        st.markdown(f"- **Angular Width (FWHM):** {metrics['angular_width']:.1f}° (Ideal < 60° for directional beams)")
    else:
        st.markdown("- **Angular Width (FWHM):** N/A")
    if metrics['side_lobe_level'] is not None:
        st.markdown(f"- **Side Lobe Level:** {metrics['side_lobe_level']:.3f} (Ideal < 0.3 relative to main lobe)")
    else:
        st.markdown("- **Side Lobe Level:** N/A")

    st.markdown("---")
    note = ""
    if metrics['main_lobe_magnitude'] < 0.3:
        note += "The main lobe magnitude is low, indicating poor directivity and inefficient radiation.\n"
        note += "Ideal antenna designs have a main lobe magnitude above 0.7 to ensure focused energy.\n"
    elif metrics['side_lobe_level'] is not None and metrics['side_lobe_level'] > 0.3:
        note += "Side lobes are relatively high, which can cause interference and reduce antenna effectiveness.\n"
        note += "Reducing side lobes below 0.3 through amplitude tapering or array adjustments is recommended.\n"
    else:
        note += "This radiation pattern demonstrates good directivity and acceptable side lobes, indicating efficient antenna performance.\n"

    if metrics['angular_width'] is not None:
        if metrics['angular_width'] > 90:
            note += "However, the angular width is quite large, resulting in a broader beam and less directional focus.\n"
            note += "Aim for narrower beams with angular width less than 60° for most directional antenna applications.\n"
        else:
            note += "The angular width is narrow, implying a focused main beam suitable for directional communication.\n"

    note += "\n**Technical Suggestions:**\n"
    note += "- Increase antenna length or aperture size to improve main lobe magnitude.\n"
    note += "- Use tapered amplitude distributions to suppress side lobes.\n"
    note += "- Optimize element spacing (around 0.5λ to 1λ) to avoid grating lobes.\n"
    note += "- Minimize phase errors in phased arrays for sharper beam steering.\n"
    note += "- Carefully design reflectors/directors to enhance gain and reduce undesired lobes.\n"

    note += "\n**Practical advice:** This antenna design can be improved by following the above ideal parameter ranges to achieve high efficiency and practical usability."

    st.info(note)

# -------------------- Footer -----------------------------
st.markdown("---")
st.caption("Developed by Aditya Dass - Antenna Radiation Visualization App - Scientific & Educational Tool")


