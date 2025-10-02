import streamlit as st
import numpy as np
import math

# --- Constants ---
DENSITIES = {"Iron": 7800, "Rock": 3000, "Ice": 900} # kg/m³
TNT_EQUIVALENT = 4.184e9 # Joules per megaton TNT

# Define the neon light red color for reuse
NEON_RED_ACCENT_COLOR = "#FF3333" # Light Red
NEON_RED_SHADOW_RGBA = "rgba(255, 51, 51, 0.7)"
NEON_RED_BUTTON_SHADOW_RGBA = "rgba(255, 51, 51, 0.9)"


# --- Backend calculations ---
def calculate_mass(diameter, material):
    """Calculates the asteroid's mass based on diameter and material."""
    radius = diameter / 2
    volume = (4/3) * math.pi * (radius**3)
    density = DENSITIES.get(material, 3000)
    return volume * density # kg

def impact_energy(diameter, velocity, material):
    """Calculates kinetic energy in megatons of TNT."""
    mass = calculate_mass(diameter, material)
    # Velocity input is km/s, converting to m/s
    velocity_m_s = velocity * 1000 
    energy_joules = 0.5 * mass * (velocity_m_s**2)
    return energy_joules / TNT_EQUIVALENT # megatons

def estimate_crater_size(diameter, velocity, angle, material, location):
    """Estimates crater size based on energy and angle."""
    # Note: velocity here is expected to be in m/s for correct energy calculation
    energy = impact_energy(diameter, velocity / 1000, material) # Pass km/s to energy function
    angle_factor = math.sin(math.radians(angle))
    effective_energy = energy * angle_factor
    
    # Rough scaling law: D ~ E^(1/4)
    crater_diameter = (effective_energy ** (1/4)) * 1.2 if location=="Land" else 0
    return crater_diameter, effective_energy

def assess_risks(diameter, velocity, angle, material, location):
    """Provides a list of potential risks."""
    energy = impact_energy(diameter, velocity / 1000, material) 
    
    risks = []
    
    if energy > 5000:
        risks.append("Potential global climate impact - The impact could throw dust and smoke into the sky, blocking sunlight for months. This might cause food shortages and big changes to the world’s climate.")
    if energy > 1000:
        risks.append("Massive fires & regional shockwaves - The heat and force from the strike could set huge areas on fire. Strong shockwaves could knock down buildings and flatten forests.")
    if location == "Ocean" and diameter > 100:
        risks.append("Tsunami risk - If it lands in the sea, giant waves could form and travel far. These tsunamis could flood coastal cities and cause massive destruction.")
    if location == "Land":
        if angle < 20:
            risks.append("Shallow impact - A low-angle hit would scatter rock and debris across the land. This could damage towns nearby and fill the air with dust.")
        if angle > 70 and energy > 50:
            risks.append("High-angle - A steep impact would shake the ground like a huge earthquake. Buildings and roads could be destroyed even far from the strike.")

    if not risks:
        risks.append("Localized impact - The asteroid would cause only small, local effects. Most of the world would not be affected.")

    return risks

# --- Streamlit Page Configuration and Custom CSS (Galaxy Theme) ---
st.set_page_config(page_title="Asteroid Impact Explorer", layout="wide")

# Image URLs for aesthetics
GALAXY_BG_URL = "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&w=1974"

# Custom CSS for Galaxy background, neon text, and fixed bottom-left control box
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
<style>
[data-testid="stAppViewContainer"] {{background-image: url("{GALAXY_BG_URL}"); background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed; color: #FFFACD;}}
.stApp, .stHeader, .st-bh, label, p, .st-b5, .stMarkdown p, h1, h2, h3, h4, h5, h6, input, button, div {{font-family: 'Orbitron', sans-serif !important; color: #FFFACD !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.8);}}
[data-testid="stMetricValue"] {{color: {NEON_RED_ACCENT_COLOR}; text-shadow: 0 0 12px {NEON_RED_BUTTON_SHADOW_RGBA}; font-size: 2.25rem;}}
[data-testid="stMetricLabel"] {{color: #A0D2EB; font-size: 1rem;}}
[data-testid="stSidebarContent"] {{background-color: rgba(20, 20, 40, 0.9); padding: 15px; border-radius: 0 10px 10px 0; border-right: 3px solid {NEON_RED_ACCENT_COLOR}; box-shadow: 5px 0 15px {NEON_RED_SHADOW_RGBA};}}
.neon-box {{background-color: rgba(20, 20, 40, 0.9); padding: 10px; border-radius: 10px; border: 3px solid {NEON_RED_ACCENT_COLOR}; box-shadow: 0 0 15px {NEON_RED_SHADOW_RGBA}; color: white; z-index: 1000; margin-bottom: 10px;}}
[data-testid="stSidebarContent"] .stSlider div[data-baseweb="slider"], [data-testid="stSidebarContent"] .stRadio, .neon-box .stSlider div[data-baseweb="slider"], .neon-box .stRadio {{background-color: rgba(255, 255, 255, 0.1); padding: 5px; border-radius: 5px; margin-bottom: 5px; margin-top: 5px; color: white !important;}}
.neon-box button, [data-testid="stSidebarContent"] button {{width: 100%; background-color: {NEON_RED_ACCENT_COLOR} !important; color: #141428 !important; border: none; padding: 8px; border-radius: 5px; margin-top: 8px; font-weight: bold; box-shadow: 0 0 10px {NEON_RED_BUTTON_SHADOW_RGBA};}}
.stRadio > div:nth-child(2) {{padding-top: 0px !important; padding-bottom: 0px !important; margin-bottom: 0px !important;}}
</style>
""", unsafe_allow_html=True)

st.header("🌌 Asteroid Impact Explorer")


# --- 2. Input Control Panel (Sidebar) ---
with st.sidebar:
    # Use st.form to group inputs and prevent constant re-runs
    with st.form("input_form"):
        # Header for the sidebar (Updated to Neon Red)
        st.markdown(f"<h3 style='color: {NEON_RED_ACCENT_COLOR} !important; text-shadow: 0 0 8px {NEON_RED_SHADOW_RGBA};'>SIMULATION INPUTS</h3>", unsafe_allow_html=True)
        
        # Sliders
        diameter = st.slider("Diameter (m)", 50, 10000, 500, key="diameter_in")
        velocity = st.slider("Velocity (km/s)", 5, 70, 25, key="velocity_in")
        angle = st.slider("Impact Angle (°)", 0, 90, 45, key="angle_in")
        
        # Radio buttons - Stacked vertically (using horizontal=True for compact radio buttons)
        st.markdown('<p style="margin-bottom: 5px; color:white !important;">Material</p>', unsafe_allow_html=True)
        material = st.radio("Material Selection", ["Iron", "Rock", "Ice"], key="material_in", index=1, horizontal=True, label_visibility="collapsed")

        st.markdown('<p style="margin-bottom: 5px; color:white !important;">Location</p>', unsafe_allow_html=True)
        location = st.radio("Location Selection", ["Land", "Ocean"], key="location_in", index=0, horizontal=True, label_visibility="collapsed")

        # Submit button
        apply_impact = st.form_submit_button("Apply")


# --- 1. Main Content Area Layout ---
# Use columns (spacer and results) to push the results box to the right side of the main content area.
col_spacer, col_results = st.columns([1, 1])

# Define the placeholder in the right column
with col_results:
    results_placeholder = st.empty()


# --- 3. Results Logic (Populating the placeholder) ---
if apply_impact:
    # Calculations based on inputs
    crater, effective_energy = estimate_crater_size(diameter, velocity, angle, material, location)
    risks = assess_risks(diameter, velocity, angle, material, location)

    # Render results into the placeholder using the custom style
    with results_placeholder.container():
        # Apply neon-box style to the results container
        st.markdown('<div class="neon-box" style="width: 100%;">', unsafe_allow_html=True)
        st.markdown("### 💥 Impact Assessment", unsafe_allow_html=True)
        
        # Display Energy
        st.metric(
            label="Effective Energy (Megatons TNT)",
            value=f"{effective_energy:,.2f}",
            delta=f"Mass: {calculate_mass(diameter, material)/1e12:.2f} trillion kg"
        )

        # Display Crater Size or Ocean message
        if location == "Land":
            st.metric(
                label="Estimated Crater Diameter (km)",
                value=f"{crater:.2f} km",
                delta_color="off"
            )
        else:
            st.markdown("---")
            st.info("🌊 Ocean Impact: Direct crater estimate is not applicable.")

        # Display Risks
        st.markdown("#### ⚠ Potential Effects", unsafe_allow_html=True)
        for risk in risks:
            st.write(f"- {risk}")

        st.markdown('</div>', unsafe_allow_html=True) # Close the results box div
