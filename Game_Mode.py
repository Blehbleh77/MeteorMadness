import pygame
import random
import sys
import math
import os

# --- Step 1: Setup Base Directory for Assets ---
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meteor Madness - Save the Earth!")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 50)
ORANGE = (255, 140, 0)
RED = (200, 40, 0)

# --- Fonts with fallback ---
def load_font(filename, size):
    font_path = os.path.join(FONTS_DIR, filename)
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    else:
        print(f"⚠ Font {filename} not found, using default.")
        return pygame.font.Font(None, size)

play_font = load_font("Orbitron-Medium.ttf", 40)    # Play/Restart/Quit
title_font = load_font("Orbitron-Bold.ttf", 72)     # Game titles
sub_font = load_font("Orbitron-Regular.ttf", 24)    # Subtitles
score_font = load_font("Orbitron-SemiBold.ttf", 40) # Score

# Earth settings
earth_radius = 300
earth_x, earth_y = WIDTH // 2, HEIGHT + 80

# Asteroid settings
asteroids = []  # [x, y, speed, hp, radius]
spawn_event = pygame.USEREVENT + 1
spawn_interval = 2000
pygame.time.set_timer(spawn_event, spawn_interval)

explosions = []  # [x, y, frame]

# --- Load assets (images) ---
def load_image(filename, scale=None, alpha=True):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ ERROR: Missing image {filename} in assets/")
        pygame.quit()
        sys.exit()
    img = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

earth_img = load_image("Earth.png", (earth_radius * 2, earth_radius * 2))
meteor_img = load_image("meteor.png")
meteor_base_size = 40
galaxy_bg = load_image("stars_minimal.jpg", (WIDTH, HEIGHT), alpha=False)

# Asteroid types
SMALL = (1, 24)
MEDIUM = (2, 36)
BIG = (3, 48)


def start_screen():
    """Start Menu"""
    waiting = True
    button_width, button_height = 180, 60
    button_x = WIDTH // 2 - button_width // 2
    button_y = HEIGHT // 2 + 80

    earth_display = pygame.transform.scale(earth_img, (earth_radius * 2, earth_radius * 2))
    earth_rect = earth_display.get_rect(center=(WIDTH // 2, HEIGHT + 100))

    while waiting:
        screen.blit(galaxy_bg, (0, 0))

        # Glow behind Earth
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (50, 100, 255, 60), (WIDTH // 2, HEIGHT + 100), 350)
        screen.blit(glow_surface, (0, 0))

        screen.blit(earth_display, earth_rect)

        # Title
        title_text = "Meteor Madness"
        title_shadow = title_font.render(title_text, True, (30, 30, 30))
        title = title_font.render(title_text, True, WHITE)
        shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 2 - 118))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title, title_rect)

        # Subtitle
        slogan = sub_font.render("Click to flick the meteors away!", True, (180, 180, 255))
        slogan_rect = slogan.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(slogan, slogan_rect)

        # Play button
        pygame.draw.rect(screen, (20, 20, 40), (button_x, button_y, button_width, button_height), border_radius=15)
        pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height), border_radius=15, width=3)
        play_text = play_font.render("PLAY", True, WHITE)
        play_rect = play_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(play_text, play_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if button_x <= mx <= button_x + button_width and button_y <= my <= button_y + button_height:
                    waiting = False


def game_over_screen(final_score):
    """Game Over Menu"""
    waiting = True
    button_width, button_height = 240, 60
    restart_x = WIDTH // 2 - button_width - 20
    quit_x = WIDTH // 2 + 20
    button_y = HEIGHT // 2 + 20

    while waiting:
        screen.blit(galaxy_bg, (0, 0))

        # Title
        title_text = "GAME OVER"
        title_shadow = title_font.render(title_text, True, (30, 30, 30))
        title = title_font.render(title_text, True, WHITE)
        shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 2 - 118))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title, title_rect)

        # Score
        score_text = score_font.render(f"Final Score: {final_score}", True, (180, 180, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        screen.blit(score_text, score_rect)

        # Retry button
        pygame.draw.rect(screen, (20, 20, 40), (restart_x, button_y, button_width, button_height), border_radius=15)
        pygame.draw.rect(screen, WHITE, (restart_x, button_y, button_width, button_height), border_radius=15, width=3)
        restart_text = play_font.render("RETRY", True, WHITE)
        restart_rect = restart_text.get_rect(center=(restart_x + button_width // 2, button_y + button_height // 2))
        screen.blit(restart_text, restart_rect)

        # Quit button
        pygame.draw.rect(screen, (20, 20, 40), (quit_x, button_y, button_width, button_height), border_radius=15)
        pygame.draw.rect(screen, WHITE, (quit_x, button_y, button_width, button_height), border_radius=15, width=3)
        quit_text = play_font.render("QUIT", True, WHITE)
        quit_rect = quit_text.get_rect(center=(quit_x + button_width // 2, button_y + button_height // 2))
        screen.blit(quit_text, quit_rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if restart_x <= mx <= restart_x + button_width and button_y <= my <= button_y + button_height:
                    waiting = False
                if quit_x <= mx <= quit_x + button_width and button_y <= my <= button_y + button_height:
                    pygame.quit()
                    sys.exit()


def run_game():
    """Main Game"""
    global asteroids
    asteroids = []
    score = 0
    start_ticks = pygame.time.get_ticks()
    running = True
    clock = pygame.time.Clock()
    earth_angle = 0

    while running:
        screen.blit(galaxy_bg, (0, 0))

        # Rotating Earth
        earth_angle = (earth_angle + 0.2) % 360
        rotated_earth = pygame.transform.rotate(earth_img, earth_angle)
        earth_rect = rotated_earth.get_rect(center=(earth_x, earth_y))
        screen.blit(rotated_earth, earth_rect)

        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == spawn_event:
                x = random.randint(meteor_base_size, WIDTH - meteor_base_size)
                y = 0
                if elapsed_time < 15:
                    asteroid_type = SMALL
                elif elapsed_time < 30:
                    asteroid_type = random.choice([SMALL, MEDIUM])
                else:
                    asteroid_type = random.choice([SMALL, MEDIUM, BIG])
                hp, radius = asteroid_type
                speed = random.uniform(1, 1.5 + elapsed_time * 0.03)
                asteroids.append([x, y, speed, hp, radius])
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for a in asteroids[:]:
                    ax, ay, speed, hp, radius = a
                    if (mx - ax) ** 2 + (my - ay) ** 2 < radius ** 2:
                        a[3] -= 1
                        if a[3] <= 0:
                            asteroids.remove(a)
                            score += 10
                            explosions.append([ax, ay, 0])
                        break

        # Move asteroids
        for a in asteroids[:]:
            ax, ay, speed, hp, radius = a
            dx, dy = earth_x - ax, earth_y - ay
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist == 0:
                continue
            ax += dx / dist * speed
            ay += dy / dist * speed
            a[0], a[1] = ax, ay
            if dist < earth_radius + radius:
                running = False
                game_over_screen(score)
            meteor_size = radius * 2
            scaled_meteor = pygame.transform.scale(meteor_img, (meteor_size, meteor_size))
            meteor_rect = scaled_meteor.get_rect(center=(int(ax), int(ay)))
            screen.blit(scaled_meteor, meteor_rect)

        # Explosions
        for exp in explosions[:]:
            x, y, frame = exp
            colors = [YELLOW, ORANGE, RED]
            color = colors[min(frame // 2, 2)]
            radius = 15 + frame * 3
            alpha = max(255 - frame * 25, 0)
            exp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(exp_surface, (*color, alpha), (radius, radius), radius)
            screen.blit(exp_surface, (x - radius, y - radius))
            exp[2] += 1
            if exp[2] > 10:
                explosions.remove(exp)

        # Score
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (15, 15))

        pygame.display.flip()
        clock.tick(60)


# --- Main loop ---
while True:
    start_screen()
    run_game()
