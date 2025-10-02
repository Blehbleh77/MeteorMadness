import streamlit as st
import subprocess
import os
import sys

# --- Setup Paths ---
BASE_DIR = os.path.dirname(__file__)
GAME_MODE_PATH = os.path.join(BASE_DIR, "game_mode.py")
EXPLORATION_MODE_PATH = os.path.join(BASE_DIR, "exploration_mode.py")
LOGO_PATH = os.path.join(BASE_DIR, "assets", "earth_logo.png")

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Meteor Madness Hub", page_icon="🌍", layout="centered")

st.title("🌌 Meteor Madness Hub")

# --- Display Logo if available ---
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, use_column_width=True)
else:
    st.warning("Logo not found! Continue without image.")

st.markdown("## Choose Your Mode")

# --- Two buttons side by side ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🎮 Game Mode"):
        try:
            subprocess.Popen([sys.executable, GAME_MODE_PATH])
            st.success("Game Mode launched! Check your Pygame window.")
        except Exception as e:
            st.error(f"Failed to launch Game Mode: {e}")

with col2:
    if st.button("🛰 Exploration Mode"):
        try:
            subprocess.Popen([sys.executable, "-m", "streamlit", "run", EXPLORATION_MODE_PATH])
            st.success("Exploration Mode launched in a new browser tab.")
        except Exception as e:
            st.error(f"Failed to launch Exploration Mode: {e}")

st.markdown(
    """
    ---
    **Instructions:**  
    - Click **Game Mode** to play the arcade meteor game.  
    - Click **Exploration Mode** to explore asteroid impacts interactively.  
    """
)
