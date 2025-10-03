import pygame
import sys
import math
import io
import time
import os

# --- Constants ---
DENSITIES = {"Iron": 7800, "Rock": 3000, "Ice": 900}
TNT_EQUIVALENT = 4.184e9


# --- Color Palette & Theme (MODIFIED for Lighter Gray/New Purple Controls) ---
PALE_CYAN_ACCENT_COLOR = "#DDC7F4" # Primary Text/Accent (New, Deeper Purple)
LIGHTER_CYAN_COLOR = "#9B7CBF" # Secondary Text/Highlight/Buttons (Lighter Purple for Controls)
DEEP_BLUE_BACKGROUND_RGB = (45, 45, 50) # Lighter Dark Gray for Sidebar/Box background
DEEP_BLUE_BACKGROUND_RGBA = (45, 45, 50, 240) # Lighter Dark Gray for Sidebar/Box background (with transparency)
CYAN_SHADOW_RGBA = (130, 100, 180, 180) # Muted Purple Shadow
CYAN_BUTTON_SHADOW_RGBA = (130, 100, 180, 230) # Muted Purple Button Shadow

# Explosion Colors from your Meteor Madness game (Keep the warm colors for explosion)
YELLOW_EXP = (255, 220, 50)
ORANGE_EXP = (255, 140, 0)
RED_EXP = (200, 40, 0)


# --- Pygame Setup & Dimensions ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
FPS = 60
MARGIN = 20
# Input panel remains at 280
INPUT_PANEL_WIDTH = 280 
INPUT_PANEL_HEIGHT = SCREEN_HEIGHT 
RESULTS_PANEL_HEIGHT = 230

# Animation State Machine
PRE_IMPACT = 0
IN_FLIGHT = 1
IMPACTED = 2

# Graphics constants
EARTH_SIZE = 350
ASTEROID_BASE_SIZE = 70
ASTEROID_SPEED = 8
EXPLOSION_DURATION = 0.5

# --- Backend calculations (Unchanged) ---
def calculate_mass(diameter, material):
    radius = diameter / 2
    volume = (4/3) * math.pi * (radius**3)
    density = DENSITIES.get(material, 3000)
    return volume * density

def impact_energy(diameter, velocity, material):
    mass = calculate_mass(diameter, material)
    velocity_m_s = velocity * 1000
    energy_joules = 0.5 * mass * (velocity_m_s**2)
    return energy_joules / TNT_EQUIVALENT

def estimate_crater_size(diameter, velocity, angle, material, location):
    energy = impact_energy(diameter, velocity, material)
    angle_factor = math.sin(math.radians(angle))
    effective_energy = energy * angle_factor
    crater_diameter = (effective_energy ** (1/4)) * 1.2 if location == "Land" else 0
    return crater_diameter, effective_energy

def assess_risks(diameter, velocity, angle, material, location):
    energy = impact_energy(diameter, velocity, material)
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

# --- Pygame UI Helper Functions & Classes (Unchanged) ---
def draw_text(surface, text, font, color, rect, aa=True, bkg=None):
    y = rect.top
    line_spacing = -2
    font_height = font.size("Tg")[1]
    
    while text:
        i = 1
        if y + font_height > rect.bottom:
            break
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)
        surface.blit(image, (rect.left, y))
        y += font_height + line_spacing
        text = text[i:]
    return text

def draw_shadowed_text(surface, text, font, color, position, shadow_color, shadow_offset=(1, 1)):
    text_surf = font.render(text, True, shadow_color)
    surface.blit(text_surf, (position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, position)
    
# NEW HELPER FUNCTION FOR DRAWING RESULT BOXES
def draw_result_box(surface, rect, header_text, font_header, font_label):
    # Draw Box Background and Border
    box_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    box_surf.fill(DEEP_BLUE_BACKGROUND_RGBA)
    pygame.draw.rect(box_surf, pygame.Color(PALE_CYAN_ACCENT_COLOR), box_surf.get_rect(), 3, border_radius=10)
    # Draw a slight shadow outside the box
    pygame.draw.rect(box_surf, pygame.Color(CYAN_SHADOW_RGBA), box_surf.get_rect().inflate(10,10), 10, border_radius=15)
    surface.blit(box_surf, rect.topleft)

    MARGIN_INNER = 10
    # Draw Header
    draw_shadowed_text(surface, header_text, font_header, pygame.Color(LIGHTER_CYAN_COLOR), (rect.x + MARGIN_INNER, rect.y + 10), (0,0,0))
    
    # Return the starting coordinates for content inside the box
    return rect.x + MARGIN_INNER, rect.y + 35

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.grabbed = False
        self.handle_rad = h
        self.update_handle_pos()

    def update_handle_pos(self):
        self.handle_pos = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.w

    @property
    def value(self):
        return self.val

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(self.handle_pos - self.handle_rad, self.rect.centery - self.handle_rad, self.handle_rad*2, self.handle_rad*2).collidepoint(event.pos):
                self.grabbed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.grabbed = False
        elif event.type == pygame.MOUSEMOTION and self.grabbed:
            self.handle_pos = max(self.rect.x, min(event.pos[0], self.rect.right))
            self.val = self.min_val + (self.handle_pos - self.rect.x) / self.rect.w * (self.max_val - self.min_val)
            return True
        return False

    def draw(self, surface, font_label, font_val):
        pygame.draw.rect(surface, pygame.Color(PALE_CYAN_ACCENT_COLOR), (self.rect.x, self.rect.centery - 2, self.rect.w, 4), border_radius=2)
        pygame.draw.rect(surface, pygame.Color(LIGHTER_CYAN_COLOR), (self.rect.x, self.rect.centery - 2, self.handle_pos - self.rect.x, 4), border_radius=2)
        pygame.draw.circle(surface, pygame.Color(LIGHTER_CYAN_COLOR), (self.handle_pos, self.rect.centery), self.handle_rad // 2)
        pygame.draw.circle(surface, pygame.Color(PALE_CYAN_ACCENT_COLOR), (self.handle_pos, self.rect.centery), self.handle_rad // 2, 1)
        draw_shadowed_text(surface, self.label, font_label, pygame.Color(PALE_CYAN_ACCENT_COLOR), (self.rect.x, self.rect.y - 25), (0,0,0))
        val_text = f"{self.val:.0f}"
        val_surf = font_val.render(val_text, True, pygame.Color(LIGHTER_CYAN_COLOR))
        surface.blit(val_surf, (self.rect.right - val_surf.get_width(), self.rect.y - 25))

class Dropdown:
    def __init__(self, x, y, w, h, options, initial_val, label):
        self.label = label
        self.options = options
        self.rect = pygame.Rect(x, y, w, h)
        self.option_rects = []
        self.is_open = False
        self.selected_val = initial_val
        self.font = None

        if initial_val not in options:
            self.selected_val = options[0]
            
    def is_active(self):
        return self.is_open

    @property
    def value(self):
        return self.selected_val

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            
            if self.is_open:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_val = self.options[i]
                        self.is_open = False
                        return True
            
            if self.is_open:
                self.is_open = False
                return True

        return False

    def draw(self, surface, font_label, font_option):
        self.font = font_option
        draw_shadowed_text(surface, self.label, font_label, pygame.Color(PALE_CYAN_ACCENT_COLOR), (self.rect.x, self.rect.y - 25), (0,0,0))
        color = pygame.Color(LIGHTER_CYAN_COLOR)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = self.font.render(self.selected_val, True, DEEP_BLUE_BACKGROUND_RGB)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.centery - text_surf.get_height() // 2))
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - 5),
            (self.rect.right - 5, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery + 5)
        ]
        pygame.draw.polygon(surface, DEEP_BLUE_BACKGROUND_RGB, arrow_points)
        
    def draw_options(self, surface):
        if not self.is_open:
            return

        self.option_rects = []
        for i, option in enumerate(self.options):
            option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.h, self.rect.w, self.rect.h)
            self.option_rects.append(option_rect)
            
            # FIXED SYNTAX ERROR: added 'self.' to selected_val
            bg_color = DEEP_BLUE_BACKGROUND_RGB if option != self.selected_val else LIGHTER_CYAN_COLOR
            text_color = PALE_CYAN_ACCENT_COLOR if option != self.selected_val else DEEP_BLUE_BACKGROUND_RGB
            
            pygame.draw.rect(surface, bg_color, option_rect)
            pygame.draw.rect(surface, PALE_CYAN_ACCENT_COLOR, option_rect, 1)
            opt_surf = self.font.render(option, True, text_color)
            surface.blit(opt_surf, (option_rect.x + 10, option_rect.centery - opt_surf.get_height() // 2))

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            return True
        return False

    def draw(self, surface, font):
        color = pygame.Color(LIGHTER_CYAN_COLOR)
        shadow_color = pygame.Color(CYAN_BUTTON_SHADOW_RGBA)
        shadow_rect = self.rect.inflate(10, 10)
        pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=12)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = font.render(self.text, True, DEEP_BLUE_BACKGROUND_RGB)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


# --- Image Loading and Setup (FIXED to load all images locally) ---
# ... (rest of the code remains the same until load_images)

# --- Image Loading and Setup (MODIFIED to use Relative Paths) ---
def load_images():
    # Base directory where your script is located
    BASE_DIR = os.path.dirname(__file__)
    # Join paths relative to your project folder
    images = {}
    
    # Paths for all images are now relative to the script's location
    # NOTE: You must place these files in the same directory as the Python script.
    
    # 1. Background Image
    # Assuming 'ai-generated-purple-galaxy-space-stars-in-outer-space-ai-generated-free-photo.jpg' 
    # is directly inside Meteor_Madness folder
    BG_PATH =os.path.join(BASE_DIR, "assets", "images", "Background.jpg")
    
    # 2. Earth Image
    # Assuming 'download.png' is directly inside Meteor_Madness folder
    EARTH_PATH =os.path.join(BASE_DIR, "assets", "images", "Earth2.png") 
    
    # 3. Asteroid Image
    # Assuming '454791-Picsart-BackgroundRemover.jpg' is directly inside Meteor_Madness folder
    ASTEROID_PATH =os.path.join(BASE_DIR, "assets", "images", "Asteroid.jpg") 
    # 4. Font Files (Assumed to be in the same folder)
    FONT_FILE = "Orbitron-Regular.ttf"
    FONT_TITLE_FILE = "Orbitron-Bold.ttf"
    
    # 1. Background - Try local load
    try:
        bg_img = pygame.image.load(BG_PATH).convert()
        images['background'] = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Successfully loaded background from relative path: {BG_PATH}")
        
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading background image: {e}")
        images['background'] = None
        
    # 2. Earth image (Load, scale and center onto a fixed square surface)
    try:
        earth_img = pygame.image.load(EARTH_PATH).convert_alpha()
        
        # Create a stable square surface for rotation
        final_square_surface = pygame.Surface((EARTH_SIZE, EARTH_SIZE), pygame.SRCALPHA)
        
        # Scale the loaded image to fit the fixed square size
        scaled_earth_img = pygame.transform.scale(earth_img, (EARTH_SIZE, EARTH_SIZE))
        
        # Blit the scaled image onto the fixed square surface
        final_square_surface.blit(scaled_earth_img, (0, 0))
        
        images['earth'] = final_square_surface # Store the stable, square image
        print(f"Successfully loaded Earth image from relative path: {EARTH_PATH}")
        
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading Earth image: {e}. Using fallback circle.")
        images['earth'] = pygame.Surface((EARTH_SIZE, EARTH_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(images['earth'], (50, 50, 200), (EARTH_SIZE//2, EARTH_SIZE//2), EARTH_SIZE//2)

    # 3. Asteroid image
    try:
        asteroid_img = pygame.image.load(ASTEROID_PATH).convert_alpha()
        images['asteroid'] = pygame.transform.scale(asteroid_img, (ASTEROID_BASE_SIZE, ASTEROID_BASE_SIZE))
        print(f"Successfully loaded asteroid image from relative path: {ASTEROID_PATH}")
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading asteroid image: {e}. Using fallback circle.")
        images['asteroid'] = pygame.Surface((ASTEROID_BASE_SIZE, ASTEROID_BASE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(images['asteroid'], (150, 150, 150), (ASTEROID_BASE_SIZE//2, ASTEROID_BASE_SIZE//2), ASTEROID_BASE_SIZE//2)

    return images

# --- Main Game ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroid Impact Explorer")
    clock = pygame.time.Clock()

    images = load_images()
    BASE_DIR = os.path.dirname(__file__)

    # --- Fonts (MODIFIED: Font loading also uses relative paths) ---
    FONT_FILE = os.path.join(BASE_DIR, "assets", "fonts", "Orbitron-Regular.ttf")  
    FONT_TITLE_FILE =os.path.join(BASE_DIR, "assets", "fonts", "Orbitron-Bold.ttf")
    
    try:
        # Attempt to load fonts using relative paths (files expected in Meteor_Madness folder)
        font_prominent_result = pygame.font.Font(FONT_TITLE_FILE, 28)
        font_prominent_result_small = pygame.font.Font(FONT_TITLE_FILE, 22) 
        font_title = pygame.font.Font(FONT_TITLE_FILE, 53) 
    except pygame.error:
        try:
            # Fallback for font files (using Regular if Bold fails)
            font_prominent_result = pygame.font.Font(FONT_FILE, 28)
            font_prominent_result_small = pygame.font.Font(FONT_FILE, 22) 
            font_title = pygame.font.Font(FONT_FILE, 53)
        except pygame.error:
            # Final fallback to Pygame default
            font_prominent_result = pygame.font.Font(None, 28)
            font_prominent_result_small = pygame.font.Font(None, 22)
            font_title = pygame.font.Font(None, 53)
            print("Warning: Could not load custom fonts. Falling back to default Pygame font.")


        
    try:
        # Load body fonts
        font_header = pygame.font.Font(FONT_TITLE_FILE, 20) 
        font_label = pygame.font.Font(FONT_FILE, 18)
        font_body = pygame.font.Font(FONT_FILE, 14)
    except pygame.error:
        font_header = pygame.font.Font(None, 20) 
        font_label = pygame.font.Font(None, 18)
        font_body = pygame.font.Font(None, 14)
        print("Warning: Could not load body fonts. Falling back to default Pygame font.")
        
# ... (rest of the main function remains the same)


        
    try:
        font_header = pygame.font.Font(FONT_TITLE_FILE, 20) 
        font_label = pygame.font.Font(FONT_FILE, 18)
        # MODIFIED: Increased font_body size from 12 to 14 for better risk text readability
        font_body = pygame.font.Font(FONT_FILE, 14)
    except pygame.error:
        font_header = pygame.font.Font(None, 20) 
        font_label = pygame.font.Font(None, 18)
        font_body = pygame.font.Font(None, 14)
        print("Warning: Could not load body fonts. Falling back to default Pygame font.")


            
    # --- UI Elements Positioning ---
    
    # 1. INPUT PANEL (Left Sidebar)
    INPUT_PANEL_X = 0
    INPUT_PANEL_Y = 0
    INPUT_PANEL_HEIGHT = SCREEN_HEIGHT
    
    # Control element positions (relative to INPUT_PANEL_X)
    SLIDER_W = INPUT_PANEL_WIDTH - (2 * MARGIN)
    SLIDER_H = 20
    INPUT_START_Y = INPUT_PANEL_Y + 150 
    COL1_X = INPUT_PANEL_X + MARGIN
    DROPDOWN_W = SLIDER_W
    DROPDOWN_H = 30
    
    # Calculate Y positions with proper spacing
    Y_DIAMETER = INPUT_START_Y
    Y_VELOCITY = Y_DIAMETER + 90
    Y_ANGLE = Y_VELOCITY + 90
    Y_MATERIAL_DROPDOWN = Y_ANGLE + 90
    Y_LOCATION_DROPDOWN = Y_MATERIAL_DROPDOWN + 60 

    diameter_slider = Slider(COL1_X, Y_DIAMETER, SLIDER_W, SLIDER_H, 50, 10000, 500, "Diameter (m)")
    velocity_slider = Slider(COL1_X, Y_VELOCITY, SLIDER_W, SLIDER_H, 5, 70, 25, "Velocity (km/s)")
    angle_slider = Slider(COL1_X, Y_ANGLE, SLIDER_W, SLIDER_H, 0, 90, 45, "Impact Angle (°)")
    material_dropdown = Dropdown(COL1_X, Y_MATERIAL_DROPDOWN, DROPDOWN_W, DROPDOWN_H, ["Rock", "Iron", "Ice"], "Rock", "Material")
    location_dropdown = Dropdown(COL1_X, Y_LOCATION_DROPDOWN, DROPDOWN_W, DROPDOWN_H, ["Land", "Ocean"], "Land", "Location")
    impact_button = Button(COL1_X + (SLIDER_W // 2) - 65, Y_LOCATION_DROPDOWN + 60, 130, 50, "Apply")
    quit_button = Button(COL1_X + (SLIDER_W // 2) - 65, Y_LOCATION_DROPDOWN + 130, 130, 50, "Quit")
    
    slider_elements = [diameter_slider, velocity_slider, angle_slider]
    dropdown_elements = [material_dropdown, location_dropdown]

    # --- Positioning for Boxes 1 & 2 (Between Panel and Earth) ---
    
    RESULTS_LEFT_PANEL_X_START = INPUT_PANEL_WIDTH + MARGIN 
    RESULTS_LEFT_PANEL_Y_START = 150 
    # Current Width: 370
    RESULTS_LEFT_PANEL_WIDTH = 370 
    SMALL_BOX_H = 100 

    # 3. EARTH/ANIMATION Positioning 
    
    EARTH_AREA_START_X = RESULTS_LEFT_PANEL_X_START + RESULTS_LEFT_PANEL_WIDTH + MARGIN 
    EARTH_AREA_WIDTH = SCREEN_WIDTH - EARTH_AREA_START_X - MARGIN

    EARTH_X = EARTH_AREA_START_X + (EARTH_AREA_WIDTH // 2) 
    EARTH_Y = 320 
    EARTH_CENTER = (EARTH_X, EARTH_Y)

    # 4. Major Risks Panel (Fills the space below the Earth/Animation)
    MAJOR_RISKS_X = INPUT_PANEL_WIDTH + MARGIN 
    MAJOR_RISKS_Y = EARTH_Y + (EARTH_SIZE // 2) + MARGIN # Remains below the Earth
    MAJOR_RISKS_WIDTH = SCREEN_WIDTH - INPUT_PANEL_WIDTH - (2 * MARGIN)
    MAJOR_RISKS_HEIGHT = SCREEN_HEIGHT - MAJOR_RISKS_Y - MARGIN 
    RISKS_RECT = pygame.Rect(MAJOR_RISKS_X, MAJOR_RISKS_Y, MAJOR_RISKS_WIDTH, MAJOR_RISKS_HEIGHT)


    # --- Game State ---
    running = True
    results_data = None
    
    # Asteroid/Animation state
    animation_state = PRE_IMPACT
    asteroid_pos = pygame.Vector2(0, 0)
    target_pos = pygame.Vector2(0, 0)
    velocity_vec = pygame.Vector2(0, 0)
    
    # Rotation and Explosion variables
    earth_angle = 0.0
    explosion_start_time = 0
    
    # Pre-render a circular mask surface for efficiency
    EARTH_RADIUS = EARTH_SIZE // 2
    circle_mask = pygame.Surface((EARTH_SIZE, EARTH_SIZE), pygame.SRCALPHA)
    # The mask is a white circle on a transparent background
    pygame.draw.circle(circle_mask, (255, 255, 255, 255), (EARTH_RADIUS, EARTH_RADIUS), EARTH_RADIUS)

    # MODIFIED: Adjusted for the new font_body (14pt)
    RISK_LINE_HEIGHT = 60 # Increased safe increment for a wrapping paragraph (~3 lines of font_body)

    while running:
        # --- Event Handling (Unchanged) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            dropdown_clicked = False
            for dropdown in dropdown_elements:
                if dropdown.handle_event(event):
                    dropdown_clicked = True
            
            if dropdown_clicked:
                for dropdown in dropdown_elements:
                    if dropdown.is_open:
                        for other_dropdown in dropdown_elements:
                            if other_dropdown is not dropdown:
                                other_dropdown.is_open = False
            
            for element in slider_elements:
                element.handle_event(event)
            
            if impact_button.handle_event(event) and animation_state != IN_FLIGHT:
                # Calculate Results
                d = diameter_slider.value
                v = velocity_slider.value
                a = angle_slider.value
                m = material_dropdown.value
                l = location_dropdown.value

                crater, energy = estimate_crater_size(d, v, a, m, l)
                risks = assess_risks(d, v, a, m, l)
                mass = calculate_mass(d, m)
                
                results_data = {
                    "energy": energy,
                    "mass": mass,
                    "crater": crater,
                    "location": l,
                    "risks": risks
                }

                # Start Animation
                animation_state = IN_FLIGHT
                
                # --- Asteroid trajectory setup (Comes from the RIGHT, hits the RIGHT) ---
                start_x = SCREEN_WIDTH - MARGIN # Start at the far right
                start_y = EARTH_CENTER[1] # Start vertically aligned with the Earth center
                asteroid_pos.x, asteroid_pos.y = start_x, start_y
                
                earth_radius_half = EARTH_SIZE / 2
                
                # Target the right hemisphere (center + offset) based on the angle
                target_offset = math.cos(math.radians(a)) * (earth_radius_half - ASTEROID_BASE_SIZE/2)
                
                target_pos.x = EARTH_CENTER[0] + target_offset
                target_pos.y = EARTH_CENTER[1]
                
                direction = target_pos - asteroid_pos
                distance = direction.length()
                if distance > 0:
                    visual_speed = ASTEROID_SPEED + (v / 70) * 5
                    velocity_vec = direction.normalize() * visual_speed
                else:
                    animation_state = PRE_IMPACT
            if quit_button.handle_event(event):
                running=False

        # --- Update Animation ---
        if animation_state == IN_FLIGHT:
            distance_to_target = (target_pos - asteroid_pos).length()
            
            if distance_to_target < velocity_vec.length():
                animation_state = IMPACTED
                explosion_start_time = time.time()
                asteroid_pos.x = -100 # Hide asteroid
            else:
                asteroid_pos += velocity_vec
            
        elif animation_state == IMPACTED:
            if time.time() - explosion_start_time > EXPLOSION_DURATION:
                animation_state = PRE_IMPACT
                
        # Earth rotation update: smooth rotation
        earth_angle = (earth_angle + 0.2) % 360

        # --- Drawing ---
        screen.fill(DEEP_BLUE_BACKGROUND_RGB)
        if images.get('background'):
            screen.blit(images['background'], (0, 0))
            
        # Draw Main Title (Centered in the RIGHT section)
        MAIN_TITLE_START_X = INPUT_PANEL_WIDTH + MARGIN 
        MAIN_TITLE_WIDTH = SCREEN_WIDTH - MAIN_TITLE_START_X - MARGIN
        TITLE_TEXT_WIDTH = font_title.size("ASTEROID IMPACT EXPLORER")[0]
        TITLE_X = MAIN_TITLE_START_X + (MAIN_TITLE_WIDTH // 2) - (TITLE_TEXT_WIDTH // 2)

        draw_shadowed_text(screen, "ASTEROID IMPACT EXPLORER", font_title, pygame.Color(PALE_CYAN_ACCENT_COLOR), 
                           (TITLE_X, 70), (0,0,0))


          # --- Draw Rotating Earth (PERFECT STABILITY FIX) ---
        if images.get('earth'):
            
            # 1. Rotate the stable, pre-scaled square image (images['earth'])
            rotated_earth_full = pygame.transform.rotate(images['earth'], earth_angle)
            
            # 2. Create the final output surface, which is always the fixed size
            final_earth_surface = pygame.Surface((EARTH_SIZE, EARTH_SIZE), pygame.SRCALPHA)
            
            # 3. Blit the rotated image onto the final surface, using the center 
            # of the rotated image's bounding box to calculate the offset.
            rotated_rect = rotated_earth_full.get_rect(center=(EARTH_SIZE // 2, EARTH_SIZE // 2))
            final_earth_surface.blit(rotated_earth_full, rotated_rect)

            # 4. Apply the circular mask directly to the final, fixed-size surface
            final_earth_surface.blit(circle_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # 5. Draw the result to the screen at the fixed center
            earth_rect = final_earth_surface.get_rect(center=EARTH_CENTER)
            screen.blit(final_earth_surface, earth_rect)

        
        # --- Draw Asteroid/Explosion (Unchanged) ---
        if animation_state == IN_FLIGHT:
            if images.get('asteroid'):
                 asteroid_angle = earth_angle * 2
                 rotated_asteroid = pygame.transform.rotate(images['asteroid'], asteroid_angle)
                 asteroid_rect = rotated_asteroid.get_rect(center=(int(asteroid_pos.x), int(asteroid_pos.y)))
                 screen.blit(rotated_asteroid, asteroid_rect)
                 
        elif animation_state == IMPACTED:
            # Draw Explosion/Flash effect
            time_elapsed = time.time() - explosion_start_time
            time_ratio = time_elapsed / EXPLOSION_DURATION
            frame = int(time_ratio * 10)
            
            colors = [YELLOW_EXP, ORANGE_EXP, RED_EXP]
            color = colors[min(frame // 2, 2)]
            
            max_radius = 50 + min(results_data.get('energy', 0) / 100, 200)
            radius = int(20 + frame * (max_radius/10))
            
            alpha = max(0, 255 - frame * 25)
            
            exp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(exp_surface, (*color, alpha), (radius, radius), radius)
            
            screen.blit(exp_surface, (target_pos.x - radius, target_pos.y - radius))

        # ----------------------------------------------------------------------
        # --- Draw UI Panels (Input Panel) ---
        # ----------------------------------------------------------------------
        # Draw Left Sidebar Input Panel 
        panel_rect = pygame.Rect(INPUT_PANEL_X, INPUT_PANEL_Y, INPUT_PANEL_WIDTH, INPUT_PANEL_HEIGHT)
        panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surf.fill(DEEP_BLUE_BACKGROUND_RGBA)

        
        # Blit the panel background first
        screen.blit(panel_surf, panel_rect.topleft)

        
        # --- Draw a bold line only on the right edge of the panel (on the main screen) ---
        border_color = pygame.Color(PALE_CYAN_ACCENT_COLOR)
        shadow_color = pygame.Color(CYAN_SHADOW_RGBA)
        
        # 1. Draw the shadow line (slightly offset)
        shadow_x = INPUT_PANEL_X + INPUT_PANEL_WIDTH + 2
        pygame.draw.line(screen, shadow_color, (shadow_x, INPUT_PANEL_Y), (shadow_x, INPUT_PANEL_Y + INPUT_PANEL_HEIGHT), 8)

        # 2. Draw the main border line
        border_x = INPUT_PANEL_X + INPUT_PANEL_WIDTH
        pygame.draw.line(screen, border_color, (border_x, INPUT_PANEL_Y), (border_x, INPUT_PANEL_Y + INPUT_PANEL_HEIGHT), 3)

        # Draw the SIMULATION INPUTS header
        draw_shadowed_text(screen, "SIMULATION INPUTS", font_header, pygame.Color(LIGHTER_CYAN_COLOR), (INPUT_PANEL_X + MARGIN, INPUT_PANEL_Y + 90), (0,0,0))
        

        for element in slider_elements:
            element.draw(screen, font_label, font_label)
        
        for element in dropdown_elements:
            element.draw(screen, font_label, font_label)
            
        impact_button.draw(screen, font_label)
        quit_button.draw(screen, font_label)
        
        # ------------------------------------------------------------------
        # --- Draw Energy/Impact Result (Between Panel and Earth) ---
        # ------------------------------------------------------------------
        if results_data:
            # Boxes 1 & 2 use the current RESULTS_LEFT_PANEL_WIDTH = 370
            ENERGY_RECT = pygame.Rect(RESULTS_LEFT_PANEL_X_START, RESULTS_LEFT_PANEL_Y_START, RESULTS_LEFT_PANEL_WIDTH, SMALL_BOX_H)
            CRATER_RECT = pygame.Rect(RESULTS_LEFT_PANEL_X_START, RESULTS_LEFT_PANEL_Y_START + SMALL_BOX_H + MARGIN, RESULTS_LEFT_PANEL_WIDTH, SMALL_BOX_H)
            
            # ------------------------------------------------------------------
            # DRAW BOX 1: ENERGY
            # ------------------------------------------------------------------
            cx, cy = draw_result_box(screen, ENERGY_RECT, "IMPACT ENERGY", font_header, font_label)
            
            # Energy Value (Mega-tons TNT) - Using font size 28 or 22
            energy_text = f"{results_data['energy']:,.2f} Mt"
            
            # --- DYNAMIC FONT SELECTION ---
            # Check length to prevent overflow (Max length around 12 characters is safe for 28pt)
            if len(energy_text) > 12:
                current_font = font_prominent_result_small # 22pt
            else:
                current_font = font_prominent_result # 28pt

            # Calculate new Y position for better centering
            text_height = current_font.size("Tg")[1]
            y_center_offset = cy + ((SMALL_BOX_H - 10) - cy + ENERGY_RECT.y) // 2 - (text_height // 2)
            
            # Use the selected font
            draw_shadowed_text(screen, energy_text, current_font, pygame.Color(PALE_CYAN_ACCENT_COLOR), (cx, y_center_offset), (0,0,0))


            # ------------------------------------------------------------------
            # DRAW BOX 2: CRATER / TSUNAMI
            # ------------------------------------------------------------------
            cx_crater, cy_crater = draw_result_box(screen, CRATER_RECT, "IMPACT RESULT", font_header, font_label)
            
            # Dynamic Label and Value based on location
            result_label = "Crater Diameter" if results_data['location'] == 'Land' else "Tsunami Risk"
            result_value = f"{results_data['crater']:.2f} km" if results_data['location'] == 'Land' else "HIGH"

            # Result Label (18pt)
            draw_shadowed_text(screen, result_label, font_label, pygame.Color(PALE_CYAN_ACCENT_COLOR), (cx_crater, cy_crater), (0,0,0))
            
            # Calculate new Y position for better centering in the taller box
            text_height_prominent = font_prominent_result.size("Tg")[1]
            header_end_y = cy_crater + font_label.size("Tg")[1] + 5 
            remaining_height = CRATER_RECT.bottom - header_end_y - 10 
            y_center_offset_crater = header_end_y + remaining_height // 2 - (text_height_prominent // 2)
            
            # Result Value (28pt)
            draw_shadowed_text(screen, result_value, font_prominent_result, pygame.Color(LIGHTER_CYAN_COLOR), (cx_crater, y_center_offset_crater), (0,0,0))

            
            # ------------------------------------------------------------------
            # DRAW BOX 3: MAJOR RISKS (Bottom, fills the width under Earth)
            # ------------------------------------------------------------------
            cx_risk, cy_risk = draw_result_box(screen, RISKS_RECT, "MAJOR RISKS", font_header, font_label)
            
            # Dynamic display of risk list
            risk_y_start = cy_risk + 5
            
            for risk in results_data['risks']:
                # Draw a small bullet point (font_body 14pt)
                draw_text(screen, "•", font_body, pygame.Color(PALE_CYAN_ACCENT_COLOR), pygame.Rect(cx_risk, risk_y_start, 10, 15))
                
                # Draw the risk text, offset for the bullet point
                text_rect = pygame.Rect(cx_risk + 15, risk_y_start, RISKS_RECT.width - 30, RISKS_RECT.height - (risk_y_start - RISKS_RECT.y) - 10) 
                
                # Use draw_text for wrapping with the 14pt font_body
                draw_text(screen, risk, font_body, pygame.Color(PALE_CYAN_ACCENT_COLOR), text_rect)
                
                # Advance the Y position using the safe fixed increment (60)
                risk_y_start += RISK_LINE_HEIGHT 

        # ------------------------------------------------------------------
        
        # Draw Dropdown Options (Drawn LAST)
        for element in dropdown_elements:
             element.draw_options(screen)
        

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
