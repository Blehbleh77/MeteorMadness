import streamlit as st
import os
import subprocess
import sys
import base64

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
GAME_MODE_PATH = os.path.join(BASE_DIR, "game_mode.py")
EXPLORATION_MODE_PATH = os.path.join(BASE_DIR, "exploration_mode.py")
BG_IMAGE_PATH = os.path.join(BASE_DIR, "assets","images", "starry_background.jpg")

# --- Colors ---
NEON_BLUE_ACCENT_COLOR = "#00BFFF"
NEON_BLUE_SHADOW_RGBA = "rgba(0, 191, 255, 0.7)"
NEON_BLUE_BUTTON_SHADOW_RGBA = "rgba(0, 191, 255, 0.9)"

# --- Encode background image as base64 ---
def get_base64_image(image_path):
    # Added error handling to verify file existence and read errors
    if not os.path.exists(image_path):
        st.error(f"Error: Background image file not found at path: {image_path}")
        return None
    try:
        with open(image_path, "rb") as img_file:
            data = img_file.read()
            return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error reading background image: {e}")
        return None

# --- IMPORTANT CHANGE 1: Uncommented and activated the actual image loading ---
bg_base64 = get_base64_image(BG_IMAGE_PATH)

# --- Streamlit Page Config ---
st.set_page_config(page_title="Crash \'n\' Course ", layout="wide")

# --- CSS ---
# --- IMPORTANT CHANGE 2: Conditionally apply CSS if image was loaded ---
if bg_base64:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

        /* Background */
        [data-testid="stAppViewContainer"] {{
            /* IMPORTANT CHANGE 3: Changed image/png to image/jpeg */
            background-image: url("data:image/jpeg;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Title */
        .title-box {{
            text-align: center;
            font-family: 'Orbitron', sans-serif;
            font-size: 4rem;
            font-weight: 900;
            color: {NEON_BLUE_ACCENT_COLOR};
            padding: 50px 20px;
            margin-bottom: 50px;
        }}

        /* Neon box */
        .neon-box {{
            background-color: rgba(0,0,50,0.7);
            padding: 25px;
            margin: 20px auto;
            border-radius: 15px;
            box-shadow:0 0 25px {NEON_BLUE_SHADOW_RGBA};
            color: #F0F8FF;
            font-family: 'Orbitron', sans-serif;
            text-align: center;
            transition: 0.5s ease;
        }}
        .neon-box:hover {{
            margin-bottom: 8px;
            color: {NEON_BLUE_ACCENT_COLOR};
            box-shadow: 0 0 12px {NEON_BLUE_BUTTON_SHADOW_RGBA};
            transform: translateY(-5px);
        }}
        .neon-box h3 {{
            margin-bottom: 12px;
            color: {NEON_BLUE_ACCENT_COLOR};
            font-size: 1.4rem;
        }}
        .neon-box p {{
            margin: 0;
            font-size: 1rem;
            opacity: 0.95;
        }}

        /* Button container (center-aligned) */
        .button-container {{
            text-align: center;
            margin-bottom: 40px;
            display: flex;
            justify-content: center;
        }}

        /* Button style */
        .stButton > button {{
            background-color: {NEON_BLUE_ACCENT_COLOR};
            color: #081018;
            font-weight: 900;
            padding:16px 32px;
            border-radius: 12px;
            box-shadow:0 0 18px {NEON_BLUE_BUTTON_SHADOW_RGBA},0 0 40px {NEON_BLUE_ACCENT_COLOR} inset;
            font-size: 1.2rem;
            border: none;
            transition: 0.5s ease;
        }}
        .stButton > button:hover {{
            background-color: #33ccff;
            box-shadow: 0 0 30px {NEON_BLUE_BUTTON_SHADOW_RGBA}, 0 0 60px {NEON_BLUE_ACCENT_COLOR} inset;
            transform: scale(1.1);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    # Fallback CSS if background image failed to load
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #000033; /* Dark blue fallback color */
            background-image: none;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Title ---
st.markdown('<div class="title-box">🌌 CRASH \'n\' COURSE </div>', unsafe_allow_html=True)

# --- Boxes in two columns ---
col1, col2 = st.columns(2)



# --- Column 1: Game Mode ---
with col1:
    st.markdown(
        """
        <div class="neon-box">
            <h3>🎮 Fun Game Mode</h3>
            <p>Dodge, defend, and survive!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Use a narrower column within col1 to help center the button more effectively
    # This creates a structure like: Wide Column > [Empty Space, Narrow Button Col, Empty Space]
    # We use st.columns([1, 1, 1]) where the button goes in the middle part (weight 1)
    
    # NEW: Use st.columns([1, 2, 1]) to center the button in the middle '2' section.
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1]) # [space, button, space] ratio

    with btn_col2:
        # st.button is now inside the center column
        if st.button("🚀 Launch Game Mode", key="game", use_container_width=True):
            try:
                subprocess.Popen([sys.executable, GAME_MODE_PATH])
            except Exception as e:
                st.error(f"Failed to launch: {e}")

# --- Column 2: Exploration Mode ---
with col2:
    st.markdown(
        """
        <div class="neon-box">
            <h3>🛰 Exploration Mode</h3>
            <p>Learn about meteors interactively!</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # NEW: Use st.columns([1, 2, 1]) to center the button in the middle '2' section.
    btn_col4, btn_col5, btn_col6 = st.columns([1, 2, 1]) # [space, button, space] ratio

    with btn_col5:
        # st.button is now inside the center column
        if st.button("🔭 Launch Exploration Mode", key="explore", use_container_width=True):
            try:
                subprocess.Popen([sys.executable, EXPLORATION_MODE_PATH])
            except Exception as e:
                st.error(f"Failed to launch: {e}")

# Note: The original 'button-container' markdown was removed because the inner `st.columns` 
# structure is a more reliable Streamlit method for centering components.