
# 🌌 Meteor Madness - NASA Space Apps 2025 Submission



!\[Meteor Madness Banner](assets/images/meteor\_madness\_banner.png)



\*\*Interactive Asteroid Impact Simulation \& Arcade Game\*\*



---



\## 🚀 Challenge Overview



\*\*Event:\*\* 2025 NASA Space Apps Challenge  

\*\*Difficulty:\*\* Beginner/Youth, Intermediate, Advanced  

\*\*Subjects:\*\* Astrophysics, Coding, Data Analysis, Disaster Response, Space Exploration, Statistics  



NASA’s challenge:  

> A newly identified near-Earth asteroid, \*Impactor-2025\*, poses a potential threat to Earth. Develop an interactive visualization and simulation tool that integrates NASA and USGS datasets, allowing users to model asteroid impact scenarios, predict consequences, and explore mitigation strategies.



Our solution: \*\*Meteor Madness\*\* – an engaging, educational, and scientifically informed platform to explore asteroid impacts and defend Earth in real-time.



---



\## 🎯 Objectives



\- Enable users to \*\*simulate asteroid impacts\*\* using size, velocity, angle, and material inputs.  

\- Calculate \*\*impact energy, crater size, and environmental effects\*\*.  

\- Provide \*\*interactive visualizations\*\* with Pygame arcade gameplay and exploration mode.  

\- Combine \*\*educational and gamified elements\*\* to engage both public and policymakers.  

\- Build a \*\*modular system\*\* for future expansion with real NASA and USGS datasets.



---



\## 🧩 Project Structure



MeteorMadness/

├── main\_menu.py # Streamlit hub to launch modes

├── game\_mode.py # Arcade Pygame game

├── exploration\_mode.py # Asteroid impact simulation (Streamlit, future Pygame)

├── assets/ # Fonts, images, and media

│ ├── fonts/

│ └── images/

├── requirements.txt # Python dependencies

└── README.md # This file





---



\## 🎮 Features



\### 1. Game Mode (Arcade)



\- Flick meteors away to protect Earth.  

\- Dynamic asteroid spawning with increasing difficulty.  

\- Explosions, score tracking, and game-over mechanics.  



!\[Game Mode Screenshot](assets/images/game\_mode\_screenshot.png)



---



\### 2. Exploration Mode (Simulation)



\- Input asteroid parameters: \*\*diameter, velocity, impact angle, material, location\*\*.  

\- Calculates \*\*mass, effective energy, and estimated crater size\*\*.  

\- Shows \*\*potential risks and environmental effects\*\* (tsunamis, fires, shockwaves).  

\- Designed with \*\*neon-themed interface\*\* for an engaging user experience.  



!\[Exploration Mode Screenshot](assets/images/exploration\_mode\_screenshot.png)



---



\### 3. Streamlit Main Menu (Hub)



\- One-click access to both \*\*Game Mode\*\* and \*\*Exploration Mode\*\*.  

\- Launch Pygame locally or Exploration Mode in browser.  

\- Visually appealing with logo and instructions.  



!\[Main Menu Screenshot](assets/images/main\_menu\_screenshot.png)



---



\## ⚙️ How to Run



\### 1. Clone Repository

```bash

git clone https://github.com/YourUsername/MeteorMadness.git

cd MeteorMadness



2\. Install Dependencies



pip install -r requirements.txt



3\. Run Main Menu (Streamlit Hub)



streamlit run main\_menu.py



📊 Technical Details



Languages \& Libraries: Python, Pygame, Streamlit, NumPy



Physics \& Calculations:



Kinetic energy and mass based on asteroid size \& material



Crater diameter scaling and angle effects



Environmental risk modeling (land/ocean, shallow/steep impacts)



Assets: Fonts, images, and UI effects for immersive gameplay



Modular Design: Easily extendable for new modes, asteroid types, or datasets



🏆 Standout Features



Gamification: Arcade mode and interactive exploration



Educational Overlays: Tooltips and explanations of physics concepts



Neon Visuals: Sci-fi themed interface for engagement



Expandable Framework: Ready for real NASA \& USGS dataset integration



Accessibility \& Engagement: Easy-to-use hub for all audiences📂 Submission Notes



Assets folder must remain in the same directory as Python files



Future plan: Convert exploration\_mode.py to Pygame for consistent gameplay



Optional: Package Game Mode and Exploration Mode as executables with PyInstaller



📹 Demo / Media



Gameplay Video (optional, if you record one)



Screenshots included above for visual reference



🔮 Future Work



Integrate real NASA NEO API data for asteroid trajectories



Model deflection strategies like kinetic impactors or gravity tractors



Add 3D visualizations of impact zones and orbital paths



Web-based deployment via Streamlit Cloud for public accessibility



📝 References \& Resources



NASA Near-Earth Object Program



USGS Geological Datasets



Hackathon Challenge: NASA Space Apps 2025











