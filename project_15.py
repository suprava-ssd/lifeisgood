from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

class AlphaRenderer:
    def __init__(self):
        """Initialize the alpha rendering system"""
        self.effect_type = "none"
        self.base_brightness = 1.0

    def start_effect(self, effect_type, brightness=1.0):
        """Begin a visual effect simulation"""
        self.effect_type = effect_type
        self.base_brightness = brightness

        # No glEnable calls - we're just setting our internal state
        pass

    def end_effect(self):
        """End visual effect simulation"""
        self.effect_type = "none"
        self.base_brightness = 1.0

        # No glDisable calls
        pass

    def set_color(self, r, g, b, a):
        """Enhanced set_color with stronger glow effect"""
        if self.effect_type == "glow":
            # Simulate additive glow by increasing brightness and enhancing colors
            # Scale RGB by alpha for brightness, keep alpha at 1.0 for visibility
            brightness = self.base_brightness * a

            # Enhance glow by boosting color components, especially blue
            enhanced_r = r * brightness + 0.1 * a  # Slight boost to red
            enhanced_g = g * brightness + 0.2 * a  # Medium boost to green
            enhanced_b = b * brightness + 0.3 * a  # Strong boost to blue

            glColor3f(enhanced_r, enhanced_g, enhanced_b)

        elif self.effect_type == "fade":
            # Simulate alpha fade by darkening colors
            glColor3f(r * a, g * a, b * a)

        elif self.effect_type == "ghost":
            # Ghost effect - blue tint with alpha
            glColor3f(r * 0.7 + 0.2, g * 0.7 + 0.2, b * 0.7 + 0.4)

        else:
            # Normal mode - no transparency simulation
            glColor3f(r, g, b)


# Create global renderer
alpha_fx = AlphaRenderer()
# Game state
class GameState:
    def __init__(self):
        self.player_pos = [0, 0, 50]  # x, y, z
        self.player_direction = [0, 1, 0]  # Initial direction (forward)
        self.player_lives = 9
        self.player_bullets = []
        self.player_missed_bullets = 0
        self.player_bullet_count = 1  # Number of bullets fired at once
        self.player_shooting_speed = 1.0  # Initial shooting speed
        self.first_person_mode = False
        self.last_shield_hit = 0.0
        # Player visual effect for life pickup
        self.player_flicker = False
        self.flicker_start_time = 0
        self.flicker_duration = 0.5  # 0.5 seconds of flickering
        
        # Cheat mode flag and shield properties
        self.cheat_mode = False  # Is cheat mode activated
        self.shield_radius = 45  # Size of shield around player
        self.shield_opacity = 0.3  # Transparency of shield
        self.shield_color = [0.3, 0.7, 1.0]  # Blue shield color
        self.shield_pulse = 0  # For pulsing animation effect

        # Helper aircraft tracking
        self.enemies_killed = 0
        self.helper_active = False
        self.helper_offset = [-30, 0, 0]  # Offset from player position
        self.helper_target = None
        self.helper_last_shot_time = 0
        self.helper_shooting_interval = 1.0  # Shoot every 1 second

        # Life pickup gifts
        self.life_gifts = []  # List to store active life gifts
        self.gift_pulse = 0  # For pulsating neon effect

        # Pause state variables
        self.paused = False
        self.pause_message = "Waiting for your arrival"
        
        # Resume state variables
        self.resuming = False
        self.resume_message = "Get Ready to Fight, Astronaut!"
        self.resume_countdown = 3  # Countdown from 3
        self.countdown_start_time = 0
        self.countdown_interval = 1.0  # 1 second between countdown numbers
        self.resume_message_duration = 2.0  # Display message for 2 seconds total

        # Enemy with color variation
        self.enemy_pos = self.generate_random_position(upper_area_only=True)
        self.enemy_lives = 1
        self.enemy_bullets = []
        self.enemy_shooting_style = 0  # 0-4 different styles
        self.enemy_bullet_color = [1.0, 0.0, 0.0]  # Initial red
        self.enemy_max_lives = 1  # Track the current max lives for this enemy
        self.enemy_color = [0.5, 0.5, 0.5]  # Base color - will change with evolution
        self.enemy_evolution = 0  # Track enemy evolution level
        self.enemy_size = 2.0  # Enemy UFO size scale factor (increased)
        
        # Enemy movement and teleportation
        self.enemy_speed = 1.0
        self.enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1), 0]
        self.enemy_teleport_time = time.time()
        self.enemy_teleport_interval = 5.0  # Seconds between teleports
        self.enemy_visible = True
        self.enemy_target_pos = self.generate_random_position(upper_area_only=True)  # Target position for movement

        self.explosions = []  # Track explosion effects

        # Asteroids with velocity for movement and trail particles
        self.asteroids = []
        for _ in range(10):
            # Generate a stronger initial velocity
            vel_x = random.uniform(-3.0, 3.0)
            vel_y = random.uniform(-3.0, 3.0)
            # Make sure velocity isn't too small
            if abs(vel_x) < 1.0: vel_x *= 2.0
            if abs(vel_y) < 1.0: vel_y *= 2.0

            self.asteroids.append({
                'pos': self.generate_random_position(),
                'size': random.uniform(8, 18),  # Slightly larger for better trails
                'type': random.randint(0, 2),
                'rotation': [random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)],
                'rotation_speed': [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)],
                'velocity': [vel_x, vel_y, 0],  # Stronger velocity
                'trail_particles': [],  # Add trail particles
                'heat_level': random.uniform(0.7, 1.0)  # Randomize heat glow intensity
            })

        # More stars for better background
        self.stars = []
        for _ in range(300):  # 300 stars
            self.stars.append({
                'pos': [random.uniform(-2000, 2000), random.uniform(-2000, 2000), random.uniform(-800, -200)],
                'brightness': random.uniform(0.5, 1.0),
                'blink_rate': random.uniform(0.5, 2.0)
            })

        # More planets for background decoration
        self.planets = []
        for _ in range(15):  # 15 planets
            self.planets.append({
                'pos': [random.uniform(-1500, 1500), random.uniform(-1500, 1500), random.uniform(-700, -300)],
                'size': random.uniform(20, 80),
                'color': [random.uniform(0.2, 0.8), random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)],
                'rings': random.random() > 0.7,  # Some planets have rings
                'ring_color': [random.uniform(0.2, 0.9), random.uniform(0.2, 0.9), random.uniform(0.2, 0.9)],
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(0.01, 0.05) * (1 if random.random() > 0.5 else -1)
            })

        self.aurora_effect = False
        self.aurora_time = 0
        self.aurora_colors = []  # Store colors for enhanced aurora effect

        self.last_shot_time = 0
        self.game_over = False

    def generate_random_position(self, upper_area_only=False):
        """Generate a random position that's always within game boundaries"""
        # Define stricter boundaries for spawning (80% of grid length)
        safe_boundary_x = GRID_LENGTH * 0.8
        
        # For enemies, restrict to upper 80% of the screen if requested
        if upper_area_only:
            # Only use the upper 80% of the screen for enemy position
            y_min = -0.2 * GRID_LENGTH  # Bottom 20% is off-limits (upper 80%)
            y_max = safe_boundary_x
        else:
            # Full range for other objects
            y_min = -safe_boundary_x
            y_max = safe_boundary_x

        # Generate position within these boundaries
        pos = [random.uniform(-safe_boundary_x, safe_boundary_x),
               random.uniform(y_min, y_max),
               random.uniform(30, 80)]

        # Make sure it's not too close to the player
        while True:
            distance = math.sqrt((pos[0] - self.player_pos[0]) ** 2 +
                                 (pos[1] - self.player_pos[1]) ** 2 +
                                 (pos[2] - self.player_pos[2]) ** 2)
            if distance > 150:  # Minimum distance from player
                return pos

            # Try a new position if too close
            pos = [random.uniform(-safe_boundary_x, safe_boundary_x),
                   random.uniform(y_min, y_max),
                   random.uniform(30, 80)]

    def generate_enemy_color(self, evolution_level):
        """Generate distinct colors for different enemy evolution levels"""
        if evolution_level == 0:
            return [0.5, 0.5, 0.5]  # Gray - initial form
        elif evolution_level == 1:
            return [0.7, 0.2, 0.2]  # Red
        elif evolution_level == 2:
            return [0.2, 0.7, 0.2]  # Green
        elif evolution_level == 3:
            return [0.2, 0.2, 0.8]  # Blue
        else:
            return [0.8, 0.2, 0.8]  # Purple - final form

    def generate_random_aurora_colors(self):
        """Generate random vibrant colors for aurora effect"""
        colors = []
        for _ in range(5):  # Generate 5 vibrant colors
            # Generate colors with high saturation
            hue = random.random()  # Random hue value (0-1)
            
            # Convert HSV to RGB with high saturation and value
            h = hue * 6.0
            i = int(h)
            f = h - i
            
            p = 0.0  # Value for black (minimum brightness)
            q = 1.0 * (1.0 - f)  # Intermediate value
            t = 1.0 * f  # Intermediate value
            
            if i % 6 == 0:
                r, g, b = 1.0, t, p
            elif i % 6 == 1:
                r, g, b = q, 1.0, p
            elif i % 6 == 2:
                r, g, b = p, 1.0, t
            elif i % 6 == 3:
                r, g, b = p, q, 1.0
            elif i % 6 == 4:
                r, g, b = t, p, 1.0
            else:
                r, g, b = 1.0, p, q
                
            colors.append((r, g, b))
            
        return colors


# Global constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960
GRID_LENGTH = 1000  # Length of grid lines

# Initialize game state (after defining constants)
game_state = GameState()

# Camera-related variables
camera_pos = [0, -800, 800]  # Adjusted for larger view
fovY = 65  # Field of view


def draw_hud_text():
    """
    Draw all HUD text elements with absolutely guaranteed visibility
    Last updated: 2025-05-06 19:51:57 UTC
    User: suprava-ssd
    """
    # 1. COMPLETELY reset all matrices to set up a clean 2D environment
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    # Use a standard orthographic projection with Y increasing upward
    # This is the most reliable setup for 2D text rendering in OpenGL
    glOrtho(0.0, WINDOW_WIDTH, 0.0, WINDOW_HEIGHT, -1.0, 1.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # 2. Position parameters - simple upper left corner positioning
    left_margin = 20
    top_margin = WINDOW_HEIGHT - 30
    line_height = 25  # Increased for better visibility

    # 3. Draw text - using the most reliable font
    def draw_hud_line(y_pos, text, color=(1.0, 1.0, 1.0)):
        # Draw the text shadow first (black)
        glColor3f(0.0, 0.0, 0.0)
        glRasterPos2i(left_margin + 1, y_pos - 1)  # Offset for shadow

        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

        # Draw the main text
        glColor3f(color[0], color[1], color[2])
        glRasterPos2f(left_margin, y_pos)

        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

    # 4. Draw each line of HUD text
    current_y = top_margin

    draw_hud_line(current_y, f"Lives: {game_state.player_lives}")
    current_y -= line_height

    draw_hud_line(current_y, f"Bullets Missed: {game_state.player_missed_bullets}/100")
    current_y -= line_height

    draw_hud_line(current_y, f"Enemy Lives: {game_state.enemy_lives}")
    current_y -= line_height

    draw_hud_line(current_y, f"Bullet Count: {game_state.player_bullet_count}")
    current_y -= line_height

    draw_hud_line(current_y, f"Enemy Evolution: {game_state.enemy_evolution}")
    current_y -= line_height

    draw_hud_line(current_y, f"Enemies Killed: {game_state.enemies_killed}")
    current_y -= line_height

    # Helper status with colored text
    if game_state.helper_active:
        draw_hud_line(current_y, "Helper Active: YES", color=(0.0, 1.0, 0.0))
    else:
        draw_hud_line(current_y, f"Helper Active: NO ({game_state.enemies_killed}/3)",
                      color=(1.0, 0.5, 0.0))
    current_y -= line_height

    # Cheat mode indicator
    if game_state.cheat_mode:
        draw_hud_line(current_y, "CHEAT MODE ACTIVE", color=(1.0, 0.3, 0.3))

    # 5. Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text_2d(x, y, text, font=GLUT_BITMAP_HELVETICA_18, r=1.0, g=1.0, b=1.0):
    """
    Draw text in 2D screen coordinates with improved visibility
    Without using restricted OpenGL functions
    Last updated: 2025-05-06 19:56:45 UTC
    User: suprava-ssd
    """
    # Save current matrices
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    # Set up a tight orthographic projection
    # This positions everything in a very specific z-range to control visibility
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    # Switch to modelview matrix for positioning
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Set the text color
    glColor3f(r, g, b)

    # Position the text with a very specific z-value to ensure it's drawn on top
    # Even without disabling depth test, this positions the text at the front
    glRasterPos2f(x, y)

    # Draw each character in the text
    for char in text:
        glutBitmapCharacter(font, ord(char))

    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
# IMPROVED CENTERED TEXT FUNCTION
def draw_centered_text_2d(text, y_offset=0, font=GLUT_BITMAP_TIMES_ROMAN_24, r=1.0, g=1.0, b=1.0):
    """Draw text centered on screen with improved visibility"""
    # Calculate text width for centering
    width = 0
    for char in text:
        width += glutBitmapWidth(font, ord(char))
    
    # Calculate centered position
    x = (WINDOW_WIDTH - width) / 2
    y = WINDOW_HEIGHT / 2 + y_offset
    
    # Draw the text
    draw_text_2d(x, y, text, font, r, g, b)


def draw_stealth_fighter(damaged_state=0, is_helper=False):
    """
    Draw the player spaceship as a stealth fighter with damage states - INCREASED SIZE
    Last updated: 2025-05-06 20:01:26 UTC
    User: suprava-ssd
    """
    glPushMatrix()

    # Scale based on whether it's the helper aircraft or main player
    if is_helper:
        # Helper aircraft is smaller
        glScalef(0.7, 0.7, 0.7)
    else:
        # Main player aircraft
        glScalef(1.5, 1.5, 1.5)

    # Apply flicker effect for life pickup
    if game_state.player_flicker and not is_helper:
        elapsed = time.time() - game_state.flicker_start_time
        if elapsed < game_state.flicker_duration:
            # Fast flicker between normal color and bright blue
            flicker_speed = 15.0
            if int(elapsed * flicker_speed) % 2 == 0:
                glColor3f(0.2, 0.5, 1.0)  # Bright blue
            else:
                glColor3f(0.3, 0.4, 0.8)  # Normal color
        else:
            game_state.player_flicker = False
            glColor3f(0.3, 0.4, 0.8)  # Normal color after flicker ends
    else:
        # Base color - more prominent coloring with damage states
        if is_helper:
            # Helper is always a bright color
            glColor3f(0.3, 0.8, 0.9)  # Cyan-blue for helper
        else:
            if damaged_state == 0:
                glColor3f(0.3, 0.4, 0.8)  # Bright blue color for undamaged state
            elif damaged_state == 1:
                glColor3f(0.5, 0.3, 0.3)  # Reddish damaged state
            elif damaged_state == 2:
                glColor3f(0.6, 0.2, 0.2)  # Deep red heavily damaged

    # Main body - flat angular fuselage
    glPushMatrix()
    glScalef(1.5, 3, 0.4)  # Wider, longer, flatter

    # Create angular stealth body using quads instead of triangles
    # Top face - pointed nose (converted to quad with an extra vertex)
    glBegin(GL_QUADS)
    # Top face - pointed nose (converted)
    glVertex3f(0, 10, 0)  # nose point
    glVertex3f(0, 10, 0)  # duplicate the nose point to create a degenerate quad
    glVertex3f(-5, 0, 2)  # left side
    glVertex3f(5, 0, 2)  # right side

    # Bottom face (converted)
    glVertex3f(0, 10, 0)  # nose point
    glVertex3f(0, 10, 0)  # duplicate the nose point to create a degenerate quad
    glVertex3f(-5, 0, -2)  # left bottom
    glVertex3f(5, 0, -2)  # right bottom

    # Center body section (already quads)
    # Top face
    glVertex3f(-5, 0, 2)
    glVertex3f(5, 0, 2)
    glVertex3f(7, -10, 2)
    glVertex3f(-7, -10, 2)

    # Bottom face
    glVertex3f(-5, 0, -2)
    glVertex3f(5, 0, -2)
    glVertex3f(7, -10, -2)
    glVertex3f(-7, -10, -2)
    glEnd()
    glPopMatrix()

    # Helper function to draw a triangular wing using quads
    def draw_wing(is_right=True):
        multiplier = 1 if is_right else -1
        glBegin(GL_QUADS)
        # Main wing surface as a quad
        glVertex3f(0, 5, 0)  # front point
        glVertex3f(0, 5, 0)  # duplicate front point for quad
        glVertex3f(multiplier * 20, -10, 0)  # wing tip
        glVertex3f(0, -10, 0)  # wing root back
        glEnd()

    # Helper function to draw a tail fin using quads
    def draw_tail_fin(is_right=True):
        multiplier = 1 if is_right else -1
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)  # base
        glVertex3f(0, 0, 0)  # duplicate base point for quad
        glVertex3f(multiplier * 3, -5, 0)  # back
        glVertex3f(0, -5, 8)  # top
        glEnd()

    if not is_helper or damaged_state < 2:  # Both wings at full health
        # Left wing
        glPushMatrix()
        glTranslatef(-15, 0, 0)
        if is_helper:
            glColor3f(0.2, 0.7, 0.8)  # Helper wing color
        else:
            glColor3f(0.2, 0.3, 0.7)  # Slightly darker blue than body
        draw_wing(is_right=False)
        glPopMatrix()

    if not is_helper or damaged_state < 1:  # Right wing only present at no damage
        # Right wing
        glPushMatrix()
        glTranslatef(15, 0, 0)
        if is_helper:
            glColor3f(0.2, 0.7, 0.8)  # Helper wing color
        else:
            glColor3f(0.2, 0.3, 0.7)
        draw_wing(is_right=True)
        glPopMatrix()

    if not is_helper or damaged_state < 2:  # Left tail fin removed at damage level 2
        glPushMatrix()
        glTranslatef(-5, -20, 2)
        if is_helper:
            glColor3f(0.25, 0.75, 0.85)  # Helper tail color
        else:
            glColor3f(0.25, 0.35, 0.75)
        draw_tail_fin(is_right=False)
        glPopMatrix()

    if not is_helper or damaged_state < 1:  # Right tail fin removed at damage level 1
        glPushMatrix()
        glTranslatef(5, -20, 2)
        if is_helper:
            glColor3f(0.25, 0.75, 0.85)  # Helper tail color
        else:
            glColor3f(0.25, 0.35, 0.75)
        draw_tail_fin(is_right=True)
        glPopMatrix()

    # Cockpit canopy
    glPushMatrix()
    glTranslatef(0, 0, 3)

    if is_helper:
        glColor3f(0.4, 0.9, 1.0)  # Helper canopy color
    elif damaged_state < 2:
        glColor3f(0.7, 0.9, 1.0)  # Brighter blue-ish transparent
    else:
        glColor3f(0.7, 0.3, 0.3)  # Damaged reddish canopy

    glPushMatrix()
    glScalef(4, 8, 2)

    # Custom shape for the canopy using quads
    glBegin(GL_QUADS)
    # Front section (converted to quad)
    glVertex3f(0, 1, 0)  # nose point
    glVertex3f(0, 1, 0)  # duplicate nose point for quad
    glVertex3f(-1, 0, 0)  # left front
    glVertex3f(1, 0, 0)  # right front

    # Top center section (converted to quad)
    glVertex3f(-1, 0, 0)  # left front
    glVertex3f(1, 0, 0)  # right front
    glVertex3f(0, -1, 1)  # peak
    glVertex3f(0, -1, 1)  # duplicate peak for quad
    glEnd()

    glPopMatrix()
    glPopMatrix()

    # Engine exhausts
    if not is_helper or damaged_state < 2:  # Left engine
        glPushMatrix()
        glTranslatef(-4, -25, 0)

        if is_helper:
            glColor3f(0.0, 0.8, 1.0)  # Helper engine color - bright cyan
        elif damaged_state < 1:
            glColor3f(1.0, 0.5, 0.0)  # Brighter orange glow
        else:
            glColor3f(0.5, 0.2, 0.1)  # Damaged engine

        glutSolidCone(2, 5, 10, 3)
        glPopMatrix()

    if not is_helper or damaged_state < 1:  # Right engine
        glPushMatrix()
        glTranslatef(4, -25, 0)
        if is_helper:
            glColor3f(0.0, 0.8, 1.0)  # Helper engine color - bright cyan
        else:
            glColor3f(1.0, 0.5, 0.0)  # Brighter orange glow

        glutSolidCone(2, 5, 10, 3)
        glPopMatrix()

    # Gun/weapons hardpoints
    if is_helper:
        glColor3f(0.4, 0.8, 0.9)  # Helper weapon color
    else:
        glColor3f(0.6, 0.6, 0.6)  # Brighter metallic

    # Left weapons hardpoint
    if not is_helper or damaged_state < 1:
        glPushMatrix()
        glTranslatef(-8, 5, -1)
        glScalef(0.5, 2, 0.5)
        glutSolidCube(3)
        glPopMatrix()

    # Right weapons hardpoint
    if not is_helper or damaged_state < 1:
        glPushMatrix()
        glTranslatef(8, 5, -1)
        glScalef(0.5, 2, 0.5)
        glutSolidCube(3)
        glPopMatrix()

    # Center hardpoint - always present
    glPushMatrix()
    glTranslatef(0, 5, -1)
    glScalef(0.8, 2.5, 0.5)
    glutSolidCube(3)
    glPopMatrix()

    # Add highlight details - engine glows for more prominent appearance
    if not is_helper or damaged_state < 2:
        glPushMatrix()
        glTranslatef(0, -27, 0)
        if is_helper:
            glColor3f(0.0, 0.9, 1.0)  # Helper engine glow - cyan
        else:
            glColor3f(1.0, 0.7, 0.2)  # Bright orange glow with transparency
        glutSolidSphere(3, 10, 10)
        glPopMatrix()

    glPopMatrix()

def draw_wireframe_sphere(radius, lats, longs):
    """
    Draw a wireframe sphere using only basic OpenGL primitives.

    Parameters:
    - radius: Radius of the sphere
    - lats: Number of latitude lines
    - longs: Number of longitude lines
    """
    # Generate sphere vertices
    vertices = []

    # Create vertices using spherical coordinates
    for i in range(lats + 1):
        lat = math.pi * (-0.5 + float(i) / lats)
        z = math.sin(lat)
        zr = math.cos(lat)

        for j in range(longs + 1):
            lng = 2 * math.pi * float(j) / longs
            x = math.cos(lng) * zr
            y = math.sin(lng) * zr
            vertices.append((x * radius, y * radius, z * radius))

    # Draw latitude lines
    glBegin(GL_LINES)
    for i in range(lats + 1):
        for j in range(longs):
            idx1 = i * (longs + 1) + j
            idx2 = i * (longs + 1) + j + 1

            # Connect adjacent longitude points
            glVertex3f(*vertices[idx1])
            glVertex3f(*vertices[idx2])
    glEnd()

    # Draw longitude lines
    glBegin(GL_LINES)
    for i in range(lats):
        for j in range(longs + 1):
            idx1 = i * (longs + 1) + j
            idx2 = (i + 1) * (longs + 1) + j

            # Connect adjacent latitude points
            glVertex3f(*vertices[idx1])
            glVertex3f(*vertices[idx2])
    glEnd()


def draw_shield():
    """Draw shield effect with enhanced glow and transparency"""
    # Set up our effect with increased brightness for more glow
    alpha_fx.start_effect("glow", brightness=1.8)  # Increased from 1.2 to 1.8

    # Enhanced pulsing effect with wider range
    time_factor = time.time() * 2.5  # Faster pulsing
    pulse_primary = 0.7 + 0.3 * math.sin(time_factor)
    pulse_secondary = 0.7 + 0.3 * math.sin(time_factor * 1.3 + 0.7)  # Different frequency

    shield_opacity = 0.5 * pulse_primary  # Slightly higher base opacity

    # Draw more layered spheres with richer colors to simulate transparency

    # Outermost layer - very faint aura
    alpha_fx.set_color(0.4, 0.7, 1.0, shield_opacity * 0.3)
    draw_wireframe_sphere(game_state.shield_radius + 5, 16, 16)

    # Main outer layer - brighter blue
    alpha_fx.set_color(0.3, 0.6, 1.0, shield_opacity * 0.7)
    draw_wireframe_sphere(game_state.shield_radius, 20, 20)  # More segments

    # Secondary layer - slightly different color for depth
    alpha_fx.set_color(0.4, 0.7, 1.0, shield_opacity * 0.6)
    draw_wireframe_sphere(game_state.shield_radius - 4, 18, 18)

    # Inner layer - lighter blue with hint of white
    alpha_fx.set_color(0.5, 0.8, 1.0, shield_opacity * 0.8)
    draw_wireframe_sphere(game_state.shield_radius - 8, 16, 16)

    # Core layer - nearly white
    alpha_fx.set_color(0.7, 0.9, 1.0, shield_opacity * 0.7)
    draw_wireframe_sphere(game_state.shield_radius - 15, 12, 12)

    # Add energy patterns - horizontal rings that rotate
    num_rings = 3
    for i in range(num_rings):
        ring_opacity = shield_opacity * (0.7 - i * 0.1) * pulse_secondary

        # Calculate rotation based on time
        angle_x = (time.time() * 15 + i * 40) % 360
        angle_z = (time.time() * 20 + i * 60) % 360

        glPushMatrix()
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_z, 0, 0, 1)

        # Adjust color for ring
        r = 0.4 + i * 0.2  # Transition from blue to white
        g = 0.6 + i * 0.2
        b = 1.0
        alpha_fx.set_color(r, g, b, ring_opacity)

        # Draw thin ring at different radiuses
        ring_radius = game_state.shield_radius * (0.9 - i * 0.15)
        tube_radius = 1.0 + i * 0.5  # Thin tube
        draw_solid_torus(tube_radius, ring_radius, 8, 24)

        glPopMatrix()

    # Add energy sparkle effects
    num_sparkles = 15
    for i in range(num_sparkles):
        # Position sparkles on shield surface with slight randomization
        angle1 = i * 137.5  # Golden angle for good distribution
        angle2 = i * 94.2 + time.time() * 20  # Different angle with movement

        # Convert to spherical coordinates
        rad1 = math.radians(angle1)
        rad2 = math.radians(angle2)
        x = math.sin(rad1) * math.cos(rad2) * game_state.shield_radius
        y = math.sin(rad1) * math.sin(rad2) * game_state.shield_radius
        z = math.cos(rad1) * game_state.shield_radius

        # Draw sparkle
        glPushMatrix()
        glTranslatef(x, y, z)

        # Pulsing size based on time but offset for each sparkle
        sparkle_size = 2.0 + 1.0 * math.sin(time.time() * 3.0 + i * 0.5)

        # Very bright color
        alpha_fx.set_color(1.0, 1.0, 1.0, 0.7 * pulse_secondary)

        # Draw as simple cross
        glBegin(GL_LINES)
        glVertex3f(-sparkle_size, 0, 0)
        glVertex3f(sparkle_size, 0, 0)
        glVertex3f(0, -sparkle_size, 0)
        glVertex3f(0, sparkle_size, 0)
        glVertex3f(0, 0, -sparkle_size)
        glVertex3f(0, 0, sparkle_size)
        glEnd()

        glPopMatrix()

    # Draw shield impact ripples when hit
    if hasattr(game_state, 'last_shield_hit') and time.time() - game_state.last_shield_hit < 0.8:  # Extended duration
        hit_progress = (time.time() - game_state.last_shield_hit) / 0.8
        ripple_size = hit_progress * 0.5
        ripple_opacity = (1.0 - hit_progress) * 0.9  # Stays brighter longer

        # Bright blue-white impact color
        alpha_fx.set_color(0.7, 0.9, 1.0, ripple_opacity)
        draw_wireframe_sphere(game_state.shield_radius * (1.0 + ripple_size), 16, 16)

        # Second ripple wave (slightly smaller and faster)
        if hit_progress > 0.2:
            second_ripple = (hit_progress - 0.2) / 0.8
            second_size = second_ripple * 0.3
            second_opacity = (1.0 - second_ripple) * 0.7

            alpha_fx.set_color(0.5, 0.8, 1.0, second_opacity)
            draw_wireframe_sphere(game_state.shield_radius * (1.0 + second_size), 12, 12)

    alpha_fx.end_effect()

def draw_ufo_enemy(damage_level=0, color=[0.5, 0.5, 0.5]):
    """Draw the UFO enemy with damage indicated by color"""
    if not game_state.enemy_visible:
        return
        
    glPushMatrix()
    # Apply size scaling factor for larger UFO
    glScalef(game_state.enemy_size, game_state.enemy_size, game_state.enemy_size)

    # Base color from parameter (evolution level)
    r, g, b = color

    # Main saucer body - darkens with damage but keeps base hue
    if damage_level == 0:
        glColor3f(r, g, b)  # Full color
    elif damage_level < 0.5:
        glColor3f(r * 0.8, g * 0.8, b * 0.8)  # Slightly darkened
    else:
        glColor3f(r * 0.6, g * 0.6, b * 0.6)  # Heavily darkened

    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    draw_solid_torus(7, 20, 20, 20)
    glPopMatrix()

    # Top dome - brighten the color for contrast
    if damage_level == 0:
        glColor3f(min(r + 0.2, 1.0), min(g + 0.2, 1.0), min(b + 0.2, 1.0))
    elif damage_level < 0.5:
        glColor3f(min(r + 0.1, 1.0), min(g + 0.1, 1.0), min(b + 0.1, 1.0))
    else:
        glColor3f(r, g, b)

    glPushMatrix()
    glTranslatef(0, 0, 7)
    glScalef(1, 1, 0.5)
    glutSolidSphere(15, 20, 10)
    glPopMatrix()

    # Bottom lights - fewer lights active as damage increases
    light_count = 8 - int(damage_level * 5)
    for i in range(light_count):
        angle = i * (360.0 / light_count)
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(18, 0, -3)

        # Lights are complementary to main color
        glColor3f(1.0 - r * 0.5, 1.0 - g * 0.5, 1.0 - b * 0.5)

        glutSolidSphere(3, 10, 10)
        glPopMatrix()

    # Central light/beam
    if damage_level < 0.8:  # Beam turns off when heavily damaged
        intensity = 0.9 - damage_level * 0.5
        glColor3f(1.0 - r * 0.7, 1.0 - g * 0.7, 1.0 - b * 0.7)  # Complementary color for beam
        glPushMatrix()
        glTranslatef(0, 0, -5)
        glutSolidCone(5, 5, 10, 5)
        glPopMatrix()

    glPopMatrix()


def draw_life_gift(gift):
    """
    Draw a life gift pickup with neon effect - increased size
    Last updated: 2025-05-06 20:07:05 UTC
    User: suprava-ssd
    """
    glPushMatrix()
    glTranslatef(gift['pos'][0], gift['pos'][1], gift['pos'][2])

    # Apply scaling factor to increase overall size
    gift_scale = 5.0  # Increase from 1.0 to 1.8 for 80% larger
    glScalef(gift_scale, gift_scale, gift_scale)

    # Rotation for visual interest
    rotation_speed = 90  # degrees per second
    angle = (time.time() * rotation_speed) % 360
    glRotatef(angle, 0, 0, 1)

    # Enhanced pulsing effect
    pulse_factor = 0.3 * math.sin(game_state.gift_pulse) + 0.7

    # Draw the outer neon glow - larger and brighter
    # Simulate transparency without blend mode by adjusting color intensity
    glow_intensity = 0.5 * pulse_factor
    glColor3f(0.0 * glow_intensity, 1.0 * glow_intensity, 0.8 * glow_intensity)  # Scaled cyan glow
    draw_wireframe_sphere(16, 16, 16)  # Use wire sphere instead of solid with blend

    # Add a second larger, fainter glow for more visibility
    glow2_intensity = 0.2 * pulse_factor
    glColor3f(0.0 * glow2_intensity, 0.8 * glow2_intensity, 1.0 * glow2_intensity)  # Lighter cyan
    draw_wireframe_sphere(20, 12, 12)  # Additional larger wireframe sphere

    # Draw the heart shape - increased size
    glColor3f(1.0, 0.2, 0.5)  # Pink-red for heart

    # Draw the solid heart shape with quads instead of triangles
    glBegin(GL_QUADS)
    # Left lobe (using a quad)
    glVertex3f(-7, 0, 0)
    glVertex3f(-7, 0, 0)  # Duplicate vertex to create a degenerate quad
    glVertex3f(0, -10, 0)
    glVertex3f(0, 7, 0)

    # Right lobe (using a quad)
    glVertex3f(7, 0, 0)
    glVertex3f(7, 0, 0)  # Duplicate vertex to create a degenerate quad
    glVertex3f(0, -10, 0)
    glVertex3f(0, 7, 0)
    glEnd()

    # Add a plus sign - thicker and larger
    glColor3f(1.0, 1.0, 1.0)  # White plus sign
    glLineWidth(4.0)  # Increased from 3.0

    glBegin(GL_LINES)
    # Vertical line
    glVertex3f(0, 4, 1)
    glVertex3f(0, -4, 1)

    # Horizontal line
    glVertex3f(-4, 0, 1)
    glVertex3f(4, 0, 1)
    glEnd()

    # Add a small highlight dot in the center for extra flair
    glColor3f(1.0, 1.0, 1.0)  # White highlight
    glPointSize(3.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 2)
    glEnd()

    glPopMatrix()


def draw_asteroid_trail(particles):
    """
    Draw the trail particles behind an asteroid
    Last updated: 2025-05-06 20:07:05 UTC
    User: suprava-ssd
    """
    # No use of glEnable/glDisable - simulate alpha effect with color scaling

    for particle in particles:
        # Fade out based on age
        alpha = 1.0 - particle['age']

        # Instead of alpha blending, scale the RGB components by alpha
        if particle['age'] < 0.3:
            # Bright yellow/white core - scale by alpha
            glColor3f(1.0 * alpha, 1.0 * alpha, 0.8 * alpha)
        elif particle['age'] < 0.6:
            # Orange mid section - scale by alpha*0.8
            scaled_alpha = alpha * 0.8
            glColor3f(1.0 * scaled_alpha, 0.6 * scaled_alpha, 0.0)
        else:
            # Dark red/orange tail - scale by alpha*0.6
            scaled_alpha = alpha * 0.6
            glColor3f(0.8 * scaled_alpha, 0.2 * scaled_alpha, 0.0)

        # Draw particle based on its age - newer particles have more detail
        glPointSize(particle['size'])

        # For newer particles use small quads instead of points
        if particle['age'] < 0.4:
            half_size = particle['size'] * 0.5
            glBegin(GL_QUADS)
            glVertex3f(particle['pos'][0] - half_size, particle['pos'][1] - half_size, particle['pos'][2])
            glVertex3f(particle['pos'][0] + half_size, particle['pos'][1] - half_size, particle['pos'][2])
            glVertex3f(particle['pos'][0] + half_size, particle['pos'][1] + half_size, particle['pos'][2])
            glVertex3f(particle['pos'][0] - half_size, particle['pos'][1] + half_size, particle['pos'][2])
            glEnd()
        else:
            # Older particles are just points
            glBegin(GL_POINTS)
            glVertex3f(particle['pos'][0], particle['pos'][1], particle['pos'][2])
            glEnd()


def draw_asteroid(size, type_id, rotation, heat_level=1.0):
    """
    Draw asteroids with sun-like appearance
    Last updated: 2025-05-06 20:19:39 UTC
    User: suprava-ssd
    """
    glPushMatrix()

    # Apply rotation
    glRotatef(rotation[0], 1, 0, 0)
    glRotatef(rotation[1], 0, 1, 0)
    glRotatef(rotation[2], 0, 0, 1)

    # CHANGE 1: Use solar colors based on asteroid type
    if type_id == 0:
        # Core sun color - bright yellow-white
        glColor3f(1.0, 0.95, 0.8)
        glutSolidSphere(size, 12, 12)  # Higher resolution for sun surface

        # CHANGE 2: Add solar surface features (sunspots)
        glColor3f(0.9, 0.6, 0.1)  # Darker orange for sunspots
        for _ in range(3):
            x = random.uniform(-0.7, 0.7) * size
            y = random.uniform(-0.7, 0.7) * size
            z = random.uniform(-0.7, 0.7) * size

            # Calculate surface position
            length = math.sqrt(x * x + y * y + z * z)
            if length > 0:
                x = x * size / length
                y = y * size / length
                z = z * size / length

            glPushMatrix()
            glTranslatef(x, y, z)
            glutSolidSphere(size * 0.2, 8, 8)  # Smaller sunspots
            glPopMatrix()

        # CHANGE 3: Enhanced solar corona effect
        heat_intensity = 0.8  # Increased intensity regardless of heat_level
        glColor3f(1.0 * heat_intensity, 0.8 * heat_intensity, 0.0)
        glPushMatrix()

        # Draw multiple wireframe spheres for corona
        for i in range(5):  # More layers for more pronounced effect
            scale_factor = 1.2 + (i * 0.15)  # Larger, more visible corona
            intensity_factor = 1.0 - (i * 0.2)
            if intensity_factor > 0:
                glColor3f(1.0 * heat_intensity * intensity_factor,
                          0.7 * heat_intensity * intensity_factor,
                          0.0)
                draw_wireframe_sphere(size * scale_factor, 12 - i, 12 - i)
        glPopMatrix()

    elif type_id == 1:
        # CHANGE 4: Solar flare type - orange-red surface
        glColor3f(1.0, 0.6, 0.1)
        glScalef(1, 0.9, 0.9)  # Less flattened for sun
        glutSolidSphere(size, 12, 12)

        # CHANGE 5: Add solar flares
        glColor3f(1.0, 0.5, 0.0)  # Bright orange for flares
        for _ in range(4):
            angle = random.uniform(0, 360)
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)
            glTranslatef(size * 0.8, 0, 0)

            # Draw solar flare as elongated shape
            glBegin(GL_QUADS)
            glVertex3f(0, -size * 0.2, 0)
            glVertex3f(size * 0.6, -size * 0.1, 0)
            glVertex3f(size * 0.6, size * 0.1, 0)
            glVertex3f(0, size * 0.2, 0)
            glEnd()
            glPopMatrix()

        # CHANGE 6: Brighter corona glow
        heat_intensity = 0.9
        glColor3f(1.0 * heat_intensity, 0.6 * heat_intensity, 0.1 * heat_intensity)
        glPushMatrix()

        for i in range(4):
            scale_factor = 1.2 + (i * 0.2)
            intensity_factor = 1.0 - (i * 0.25)
            if intensity_factor > 0:
                glColor3f(1.0 * heat_intensity * intensity_factor,
                          0.6 * heat_intensity * intensity_factor,
                          0.1 * heat_intensity * intensity_factor)
                draw_wireframe_sphere(size * scale_factor, 10 - i, 10 - i)
        glPopMatrix()

    else:
        # CHANGE 7: Solar prominence type - deep red surface
        glColor3f(0.9, 0.3, 0.1)

        # Use sphere instead of dodecahedron for sun-like shape
        glutSolidSphere(size, 12, 12)

        # CHANGE 8: Add solar prominences (loops)
        glColor3f(1.0, 0.4, 0.0)

        for i in range(3):
            angle = i * 120
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)

            # Draw prominence arc
            glBegin(GL_QUAD_STRIP)
            for t in range(0, 181, 20):
                rad = math.radians(t)
                arc_radius = size * 1.2
                thickness = size * 0.1

                x = math.cos(rad) * arc_radius
                y = math.sin(rad) * arc_radius

                glVertex3f(x, y, thickness)
                glVertex3f(x, y, -thickness)
            glEnd()
            glPopMatrix()

        # CHANGE 9: Red-orange corona
        heat_intensity = 0.9
        glPushMatrix()

        for i in range(4):
            scale_factor = 1.2 + (i * 0.2)
            intensity_factor = 1.0 - (i * 0.2)
            if intensity_factor > 0:
                glColor3f(1.0 * heat_intensity * intensity_factor,
                          0.3 * heat_intensity * intensity_factor,
                          0.1 * heat_intensity * intensity_factor)
                draw_wireframe_sphere(size * scale_factor, 10 - i, 10 - i)
        glPopMatrix()

    glPopMatrix()


def draw_bullet(is_player=True, is_helper=False):
    """
    Draw a bullet (player or enemy) with custom shapes
    Last updated: 2025-05-06 20:24:08 UTC
    User: suprava-ssd
    """
    glPushMatrix()

    if is_player:
        if is_helper:
            # Helper bullets - cyan laser
            glColor3f(0.0, 0.8, 1.0)
            glScalef(0.5, 2.0, 0.5)  # Slightly smaller helper bullets
        else:
            # Player bullets - blue laser
            glColor3f(0.2, 0.5, 1.0)
            glScalef(0.8, 2.5, 0.8)  # Slightly larger bullets
        glutSolidCube(3)
    else:
        # Enemy bullets - based on enemy shooting style
        r, g, b = game_state.enemy_bullet_color
        glColor3f(r, g, b)

        if game_state.enemy_shooting_style == 0:
            # Standard laser
            glutSolidCube(4)  # Slightly larger
        elif game_state.enemy_shooting_style == 1:
            # Energy ball
            glutSolidSphere(3, 10, 10)  # Larger sphere
        elif game_state.enemy_shooting_style == 2:
            # REPLACED: Diamond projectile (custom diamond instead of octahedron)
            glScalef(1.5, 1.5, 1.5)  # Scale up

            # Custom diamond shape using quads
            glBegin(GL_QUADS)

            # Top half
            glVertex3f(0, 0, 4)  # Top point
            glVertex3f(-2, -2, 0)  # SW corner
            glVertex3f(2, -2, 0)  # SE corner
            glVertex3f(0, 0, 4)  # Top point (degenerate quad)

            glVertex3f(0, 0, 4)  # Top point
            glVertex3f(2, -2, 0)  # SE corner
            glVertex3f(2, 2, 0)  # NE corner
            glVertex3f(0, 0, 4)  # Top point (degenerate quad)

            glVertex3f(0, 0, 4)  # Top point
            glVertex3f(2, 2, 0)  # NE corner
            glVertex3f(-2, 2, 0)  # NW corner
            glVertex3f(0, 0, 4)  # Top point (degenerate quad)

            glVertex3f(0, 0, 4)  # Top point
            glVertex3f(-2, 2, 0)  # NW corner
            glVertex3f(-2, -2, 0)  # SW corner
            glVertex3f(0, 0, 4)  # Top point (degenerate quad)

            # Bottom half
            glVertex3f(0, 0, -4)  # Bottom point
            glVertex3f(-2, -2, 0)  # SW corner
            glVertex3f(2, -2, 0)  # SE corner
            glVertex3f(0, 0, -4)  # Bottom point (degenerate quad)

            glVertex3f(0, 0, -4)  # Bottom point
            glVertex3f(2, -2, 0)  # SE corner
            glVertex3f(2, 2, 0)  # NE corner
            glVertex3f(0, 0, -4)  # Bottom point (degenerate quad)

            glVertex3f(0, 0, -4)  # Bottom point
            glVertex3f(2, 2, 0)  # NE corner
            glVertex3f(-2, 2, 0)  # NW corner
            glVertex3f(0, 0, -4)  # Bottom point (degenerate quad)

            glVertex3f(0, 0, -4)  # Bottom point
            glVertex3f(-2, 2, 0)  # NW corner
            glVertex3f(-2, -2, 0)  # SW corner
            glVertex3f(0, 0, -4)  # Bottom point (degenerate quad)

            glEnd()

        elif game_state.enemy_shooting_style == 3:
            # Cube projectile
            glutSolidCube(5)  # Larger cube
        else:
            # REPLACED: Cone projectile with custom cylinder
            glRotatef(90, 1, 0, 0)  # Keep the same rotation

            # Custom cylinder implementation
            radius = 3
            height = 7
            slices = 12  # Number of sides around the cylinder
            stacks = 4  # Number of divisions along height

            # Draw the cylinder body using quad strips
            glBegin(GL_QUAD_STRIP)
            for i in range(slices + 1):
                angle = 2.0 * math.pi * i / slices
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                # Top vertex
                glVertex3f(x, y, height / 2)
                # Bottom vertex
                glVertex3f(x, y, -height / 2)
            glEnd()

            # Draw the top and bottom caps using triangle fans
            # Top cap
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, height / 2)  # Center point
            for i in range(slices + 1):
                angle = 2.0 * math.pi * i / slices
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                glVertex3f(x, y, height / 2)
            glEnd()

            # Bottom cap
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, -height / 2)  # Center point
            for i in range(slices + 1):
                angle = -2.0 * math.pi * i / slices  # Note the negative to reverse winding
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                glVertex3f(x, y, -height / 2)
            glEnd()

    glPopMatrix()

def draw_solid_torus(inner_radius, outer_radius, sides, rings):
    """
    Draw a solid torus using only basic OpenGL primitives.

    Parameters:
    - inner_radius: Radius of the tube
    - outer_radius: Distance from center of torus to center of tube
    - sides: Number of segments around the tube
    - rings: Number of segments around the torus
    """
    # Pre-calculate values for performance
    two_pi = 2.0 * math.pi

    # For each ring segment
    for i in range(rings):
        ring_angle1 = i * two_pi / rings
        ring_angle2 = (i + 1) * two_pi / rings

        cos_ring1 = math.cos(ring_angle1)
        sin_ring1 = math.sin(ring_angle1)
        cos_ring2 = math.cos(ring_angle2)
        sin_ring2 = math.sin(ring_angle2)

        # Draw the ring using triangle strips
        glBegin(GL_TRIANGLE_STRIP)

        # For each side segment
        for j in range(sides + 1):
            side_angle = j * two_pi / sides

            cos_side = math.cos(side_angle)
            sin_side = math.sin(side_angle)

            # Calculate vertex positions
            x1 = (outer_radius + inner_radius * cos_side) * cos_ring1
            y1 = (outer_radius + inner_radius * cos_side) * sin_ring1
            z1 = inner_radius * sin_side

            x2 = (outer_radius + inner_radius * cos_side) * cos_ring2
            y2 = (outer_radius + inner_radius * cos_side) * sin_ring2
            z2 = inner_radius * sin_side

            # Calculate normal vectors for smooth shading
            nx1 = cos_side * cos_ring1
            ny1 = cos_side * sin_ring1
            nz1 = sin_side

            nx2 = cos_side * cos_ring2
            ny2 = cos_side * sin_ring2
            nz2 = sin_side

            # Set normals and vertices
            glNormal3f(nx1, ny1, nz1)
            glVertex3f(x1, y1, z1)

            glNormal3f(nx2, ny2, nz2)
            glVertex3f(x2, y2, z2)

        glEnd()

def draw_explosion(size, age):
    """Draw explosion without using glut sphere functions"""
    alpha_fx.start_effect("glow", brightness=1.5)

    # Size calculation
    if age < 0.3:
        current_size = size * (age * 3.0)
    else:
        current_size = size * (1.0 - (age - 0.3) / 0.7)

    # Core opacity fades throughout
    core_opacity = 1.0 - age

    # Multi-pass approach to simulate transparency
    # Draw spheres from largest to smallest

    # Pass 1: Outer layer - red
    alpha_fx.set_color(1.0, 0.2, 0.0, core_opacity * 0.6)
    draw_wireframe_sphere(current_size, 8, 8)

    # Pass 2: Middle layer - orange
    alpha_fx.set_color(1.0, 0.5, 0.0, core_opacity * 0.8)
    draw_wireframe_sphere(current_size * 0.7, 6, 6)

    # Pass 3: Core - yellow/white
    alpha_fx.set_color(1.0, 0.9, 0.6, core_opacity)
    draw_wireframe_sphere(current_size * 0.5, 4, 4)

    # Particle effects - lines for large explosions
    if size > 15:
        glBegin(GL_LINES)
        for i in range(15):
            angle = i * 24
            rad = math.radians(angle)
            length = current_size * 1.5

            x_offset = math.cos(rad) * length
            y_offset = math.sin(rad) * length
            z_offset = random.uniform(-0.5, 0.5) * length

            # Start of line - bright
            alpha_fx.set_color(1.0, 0.9, 0.2, core_opacity * 0.8)
            glVertex3f(0, 0, 0)

            # End of line - fade out
            alpha_fx.set_color(1.0, 0.3, 0.0, 0.1)
            glVertex3f(x_offset, y_offset, z_offset)
        glEnd()

    alpha_fx.end_effect()

def draw_stars_and_planets():
    """Draw the background stars and planets"""
    # Stars
    glPointSize(2)
    for star in game_state.stars:
        # Calculate blinking effect
        brightness = star['brightness'] * (0.7 + 0.3 * math.sin(time.time() * star['blink_rate']))
        glColor3f(brightness, brightness, brightness)

        glBegin(GL_POINTS)
        glVertex3f(star['pos'][0], star['pos'][1], star['pos'][2])
        glEnd()

    # Planets
    for planet in game_state.planets:
        r, g, b = planet['color']
        glColor3f(r, g, b)

        glPushMatrix()
        glTranslatef(planet['pos'][0], planet['pos'][1], planet['pos'][2])
        
        # Apply rotation for visual interest
        glRotatef(planet['rotation'], 0, 0, 1)

        # Add some texture variation to planets
        glutSolidSphere(planet['size'], 20, 20)

        # Draw rings for some planets
        if planet['rings']:
            ring_r, ring_g, ring_b = planet['ring_color']
            glColor3f(ring_r, ring_g, ring_b)
            glRotatef(75, 1, 0, 0)

            glPushMatrix()
            glutSolidTorus(planet['size'] / 10, planet['size'] * 1.8, 20, 30)
            glPopMatrix()

        glPopMatrix()


def draw_aurora_effect():
    """
    Draw enhanced aurora effect without using triangle strips
    Last updated: 2025-05-06 20:28:56 UTC
    User: suprava-ssd
    """
    # Calculate fade based on time
    fade_time = time.time() - game_state.aurora_time
    if fade_time < 0.3:
        opacity = fade_time / 0.3  # Fade in
    elif fade_time > 1.2:
        opacity = 1.0 - ((fade_time - 1.2) / 0.3)  # Fade out
    else:
        opacity = 1.0  # Full brightness

    alpha_fx.start_effect("glow", brightness=1.2)

    # Get aurora colors from game state
    color1 = game_state.aurora_colors[0]
    color2 = game_state.aurora_colors[1]

    # Draw aurora as multiple layers with limited grid size for performance
    for layer in range(5):  # Reduced from 5 to 3 layers
        wave_time = time.time() * (0.5 + layer * 0.1)
        layer_height = -200 + layer * 100
        layer_opacity = opacity * (0.3 + layer * 0.2)  # Increased opacity
        grid_size = 50  # Smaller grid

        # Draw using GL_QUADS instead of GL_TRIANGLE_STRIP
        glBegin(GL_QUADS)
        for i in range(-grid_size, grid_size - 2, 2):  # Step by 2 for better performance
            for j in range(-grid_size, grid_size - 4, 4):  # Step by 4
                # Calculate the four corners of each quad
                x1 = i * 10
                y1 = j * 10
                x2 = (i + 2) * 10  # Next point in x direction
                y2 = (j + 4) * 10  # Next point in y direction

                # Wave calculations for the four vertices
                # Bottom left
                wave1_bl = 20 * math.sin(x1 / 100 + wave_time)
                wave2_bl = 15 * math.cos(y1 / 120 + wave_time * 0.7)
                z1 = layer_height + wave1_bl + wave2_bl

                # Bottom right
                wave1_br = 20 * math.sin(x2 / 100 + wave_time)
                wave2_br = 15 * math.cos(y1 / 120 + wave_time * 0.7)
                z2 = layer_height + wave1_br + wave2_br

                # Top right
                wave1_tr = 20 * math.sin(x2 / 100 + wave_time)
                wave2_tr = 15 * math.cos(y2 / 120 + wave_time * 0.7)
                z3 = layer_height + wave1_tr + wave2_tr

                # Top left
                wave1_tl = 20 * math.sin(x1 / 100 + wave_time)
                wave2_tl = 15 * math.cos(y2 / 120 + wave_time * 0.7)
                z4 = layer_height + wave1_tl + wave2_tl

                # Color interpolation for this quad (use average position)
                avg_x = (x1 + x2) / 2
                t = (math.sin(avg_x / 200 + wave_time) + 1) / 2
                r = color1[0] * (1 - t) + color2[0] * t
                g = color1[1] * (1 - t) + color2[1] * t
                b = color1[2] * (1 - t) + color2[2] * t

                # Set color for all vertices of this quad
                alpha_fx.set_color(r, g, b, layer_opacity)

                # Draw quad in counter-clockwise order
                glVertex3f(x1, y1, z1)  # Bottom left
                glVertex3f(x2, y1, z2)  # Bottom right
                glVertex3f(x2, y2, z3)  # Top right
                glVertex3f(x1, y2, z4)  # Top left
        glEnd()

    alpha_fx.end_effect()


def draw_transparent_grid():
    pass

def update_asteroid_trail(asteroid, dt):
    """
    Update asteroid trail particles
    Last updated: 2025-05-06 10:20:51 UTC
    User: suprava-ssd
    """
    # Define lifespan for particles
    max_particles = 15 if asteroid['size'] > 15 else 8

    # Create new trail particles at asteroid's position
    if random.random() < 0.3:
        # Make sure asteroid has a heat_level property, with a default if it doesn't exist
        if 'heat_level' not in asteroid:
            asteroid['heat_level'] = random.uniform(0.5, 1.0)

        particle = {
            'pos': asteroid['pos'].copy(),
            'size': asteroid['size'] * 0.8 * random.uniform(0.5, 1.0),
            'age': 0.0,
            'lifetime': random.uniform(0.5, 1.5),
            'color': [0.9, 0.6, 0.2],  # Orange-yellow base color
            'heat_level': asteroid['heat_level']  # Now safe to access
        }

        # Add a slight offset to the particle's position
        offset_range = asteroid['size'] * 0.2
        particle['pos'][0] += random.uniform(-offset_range, offset_range)
        particle['pos'][1] += random.uniform(-offset_range, offset_range)
        particle['pos'][2] += random.uniform(-offset_range, offset_range)

        asteroid['trail_particles'].append(particle)

    # Update existing particles
    for particle in asteroid['trail_particles'][:]:
        # Age the particle
        particle['age'] += dt

        # Remove old particles
        if particle['age'] > particle['lifetime']:
            asteroid['trail_particles'].remove(particle)
            continue

        # Shrink particles as they age
        age_ratio = particle['age'] / particle['lifetime']
        particle['size'] *= (1.0 - dt * 0.5)

        # Fade color intensity over time
        fade_factor = 1.0 - age_ratio
        particle['color'][0] = 0.9 * fade_factor
        particle['color'][1] = 0.6 * fade_factor
        particle['color'][2] = 0.2 * fade_factor

    # Limit the number of particles
    while len(asteroid['trail_particles']) > max_particles:
        asteroid['trail_particles'].pop(0)  # Remove oldest particle


def initialize_asteroids(count=5):
    """
    Initialize asteroids with all required properties including type and heat_level
    Last updated: 2025-05-06 10:23:32 UTC
    User: suprava-ssd
    """
    asteroids = []

    for _ in range(count):
        # Generate random position away from the player
        pos = [
            random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50),
            random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50),
            random.uniform(-100, -50)  # Keep asteroids above the player
        ]

        # Make sure asteroids start away from the player
        while math.sqrt(pos[0] ** 2 + pos[1] ** 2) < 200:
            pos[0] = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            pos[1] = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)

        # Create asteroid with more realistic properties
        size = random.uniform(15, 30)

        # Give asteroids actual velocity - not too fast, but noticeable
        velocity = [
            random.uniform(-1.5, 1.5),
            random.uniform(-1.5, 1.5),
            random.uniform(-0.2, 0.2)
        ]

        # Make sure velocity is not too small
        speed = math.sqrt(velocity[0] ** 2 + velocity[1] ** 2 + velocity[2] ** 2)
        if speed < 0.5:
            # Normalize to minimum speed
            factor = 0.5 / speed
            velocity = [v * factor for v in velocity]

        # Add 'type' property for asteroid rendering
        asteroid_type = random.randint(0, 2)  # Randomly select asteroid type (0, 1, or 2)

        asteroid = {
            'pos': pos,
            'size': size,
            'velocity': velocity,
            'rotation': [random.uniform(0, 360) for _ in range(3)],
            'rotation_speed': [random.uniform(-2, 2) for _ in range(3)],
            'trail_particles': [],
            'heat_level': random.uniform(0.5, 1.0),
            'type': asteroid_type  # Add type property
        }

        asteroids.append(asteroid)

    return asteroids

def update_enemy_movement(dt):
    """Update enemy UFO movement and teleportation"""
    current_time = time.time()
    
    # Check if it's time to teleport (disappear/reappear)
    if current_time - game_state.enemy_teleport_time > game_state.enemy_teleport_interval:
        game_state.enemy_teleport_time = current_time
        
        if game_state.enemy_visible:
            # Disappear
            game_state.enemy_visible = False
        else:
            # Reappear in a new location in the upper 80% of the screen
            game_state.enemy_pos = game_state.generate_random_position(upper_area_only=True)
            game_state.enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1), 0]
            game_state.enemy_visible = True
            
            # Set a new random target position for movement
            game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)
    
    # Update movement if visible
    if game_state.enemy_visible:
        # If we have a target position, move towards it
        if game_state.enemy_target_pos:
            # Calculate direction to target
            dx = game_state.enemy_target_pos[0] - game_state.enemy_pos[0]
            dy = game_state.enemy_target_pos[1] - game_state.enemy_pos[1]
            dz = game_state.enemy_target_pos[2] - game_state.enemy_pos[2]
            
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # If close to target, get a new one
            if dist < 10:
                game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)
            else:
                # Normalize direction
                if dist > 0:
                    dx /= dist
                    dy /= dist
                    dz /= dist
                
                # Update position
                game_state.enemy_pos[0] += dx * game_state.enemy_speed * dt * 60
                game_state.enemy_pos[1] += dy * game_state.enemy_speed * dt * 60
                game_state.enemy_pos[2] += dz * game_state.enemy_speed * dt * 60
                
                # Ensure the enemy stays in the upper 80% of the screen
                bottom_boundary = -0.2 * GRID_LENGTH  # 20% from the bottom (upper 80%)
                if game_state.enemy_pos[1] < bottom_boundary:
                    game_state.enemy_pos[1] = bottom_boundary
                    # Set a new target in the valid area
                    game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)
        else:
            # Set initial target position if none exists
            game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)


def update_enemy_bullets():
    """
    Update enemy bullets position and handle collisions with player
    Last updated: 2025-05-06 20:54:58 UTC
    User: suprava-ssd
    """
    bullets_to_remove = []
    for idx, bullet in enumerate(game_state.enemy_bullets):
        # Store previous position before updating
        prev_position = bullet['pos'].copy()

        # Update bullet position based on velocity
        bullet['pos'][0] += bullet['vel'][0] * game_state.delta_time
        bullet['pos'][1] += bullet['vel'][1] * game_state.delta_time
        bullet['pos'][2] += bullet['vel'][2] * game_state.delta_time

        # Check if bullet is outside game bounds
        if (abs(bullet['pos'][0]) > GAME_AREA_SIZE or
                abs(bullet['pos'][1]) > GAME_AREA_SIZE or
                bullet['pos'][2] < -200 or bullet['pos'][2] > 200):
            bullets_to_remove.append(idx)
            continue

        # IMPROVED COLLISION DETECTION:
        # 1. Define collision radii
        player_radius = 10.0  # Player ship collision radius
        bullet_radius = 3.0  # Enemy bullet collision radius

        # 2. Perform swept collision detection between previous and current positions
        if not game_state.cheat_mode:  # Skip if player has shield/cheat mode
            # Calculate direction vector of bullet movement this frame
            direction = [
                bullet['pos'][0] - prev_position[0],
                bullet['pos'][1] - prev_position[1],
                bullet['pos'][2] - prev_position[2]
            ]

            # Calculate length of movement
            movement_length = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)

            if movement_length > 0:
                # Normalize direction vector
                direction[0] /= movement_length
                direction[1] /= movement_length
                direction[2] /= movement_length

                # Calculate vector from previous position to player
                to_player = [
                    game_state.player_pos[0] - prev_position[0],
                    game_state.player_pos[1] - prev_position[1],
                    game_state.player_pos[2] - prev_position[2]
                ]

                # Calculate dot product to find closest point on trajectory to player
                dot_product = (to_player[0] * direction[0] +
                               to_player[1] * direction[1] +
                               to_player[2] * direction[2])

                # Clamp to movement length
                dot_product = max(0, min(dot_product, movement_length))

                # Calculate closest point on trajectory
                closest_point = [
                    prev_position[0] + direction[0] * dot_product,
                    prev_position[1] + direction[1] * dot_product,
                    prev_position[2] + direction[2] * dot_product
                ]

                # Calculate distance between closest point and player center
                distance_squared = ((closest_point[0] - game_state.player_pos[0]) ** 2 +
                                    (closest_point[1] - game_state.player_pos[1]) ** 2 +
                                    (closest_point[2] - game_state.player_pos[2]) ** 2)

                # Check if distance is less than sum of radii (collision occurred)
                if distance_squared < (player_radius + bullet_radius) ** 2:
                    # Collision detected! Apply damage and remove bullet
                    handle_player_hit()
                    bullets_to_remove.append(idx)
                    continue

    # Remove bullets in reverse order to avoid index issues
    for idx in sorted(bullets_to_remove, reverse=True):
        game_state.enemy_bullets.pop(idx)


def handle_player_hit():
    """
    Handle player being hit by enemy bullet
    Last updated: 2025-05-06 20:54:58 UTC
    User: suprava-ssd
    """
    # If player is invincible (post-damage), don't apply damage again
    current_time = time.time()
    if current_time - game_state.last_hit_time < game_state.invincibility_time:
        return

    # Apply damage
    game_state.player_lives -= 1
    game_state.last_hit_time = current_time

    # Play hit sound
    play_sound('player_hit')

    # Create hit effect
    create_explosion(game_state.player_pos.copy(), size=10, is_player=True)

    # Check for game over
    if game_state.player_lives <= 0:
        game_state.game_over = True
        play_sound('game_over')

def update_helper_aircraft(dt):
    """Update the helper aircraft position and targeting"""
    if not game_state.helper_active:
        return
        
    # Position the helper aircraft relative to the player
    helper_pos = [
        game_state.player_pos[0] + game_state.helper_offset[0],
        game_state.player_pos[1] + game_state.helper_offset[1],
        game_state.player_pos[2] + game_state.helper_offset[2]
    ]
    
    # Find the closest asteroid to target
    closest_asteroid = None
    closest_dist = float('inf')
    
    for asteroid in game_state.asteroids:
        dx = asteroid['pos'][0] - helper_pos[0]
        dy = asteroid['pos'][1] - helper_pos[1]
        dz = asteroid['pos'][2] - helper_pos[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < closest_dist:
            closest_dist = dist
            closest_asteroid = asteroid
    
    # Set the target
    if closest_asteroid:
        game_state.helper_target = closest_asteroid
    
    # Check if it's time to shoot
    current_time = time.time()
    if current_time - game_state.helper_last_shot_time > game_state.helper_shooting_interval:
        if game_state.helper_target:
            game_state.helper_last_shot_time = current_time
            
            # Calculate direction to target
            dx = game_state.helper_target['pos'][0] - helper_pos[0]
            dy = game_state.helper_target['pos'][1] - helper_pos[1]
            dz = game_state.helper_target['pos'][2] - helper_pos[2]
            
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist > 0:
                dx /= dist
                dy /= dist
                dz /= dist
            
            # Create a new helper bullet
            game_state.player_bullets.append({
                'pos': helper_pos.copy(),
                'direction': [dx, dy, dz],
                'is_helper': True
            })


def update_life_gifts(dt):
    """Update life gift items"""
    # Update the pulsation effect
    game_state.gift_pulse = (game_state.gift_pulse + dt * 3) % (math.pi * 2)
    
    # Check for collisions with player
    for gift in game_state.life_gifts[:]:
        dx = gift['pos'][0] - game_state.player_pos[0]
        dy = gift['pos'][1] - game_state.player_pos[1]
        dz = gift['pos'][2] - game_state.player_pos[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 35:  # Player collision radius
            # Collect the gift
            game_state.player_lives += 1
            game_state.life_gifts.remove(gift)
            
            # Start player flicker effect
            game_state.player_flicker = True
            game_state.flicker_start_time = time.time()
            
            # Add a small explosion effect at player position
            game_state.explosions.append({
                'pos': game_state.player_pos.copy(),
                'size': 15,
                'age': 0.0,
                'duration': 0.3
            })


def update_game_state():
    """
    Update game logic here
    Last updated: 2025-05-06 10:11:46 UTC
    User: suprava-ssd
    """
    if game_state.game_over:
        return

    current_time = time.time()
    dt = 0.016  # Assume ~60 FPS for animation timing

    # Handle resuming countdown
    if game_state.resuming:
        elapsed = current_time - game_state.countdown_start_time

        if elapsed >= game_state.resume_message_duration + 3.0:
            # Resume is complete after message + countdown
            game_state.resuming = False

        # Don't update any other game state during resume countdown
        return

    # Don't update game state if paused
    if game_state.paused:
        return

    # Update enemy movement and teleportation
    update_enemy_movement(dt)

    # Update helper aircraft if active
    if game_state.helper_active:
        update_helper_aircraft(dt)

    # Update life gifts
    update_life_gifts(dt)

    # Handle player bullet movement
    for bullet in game_state.player_bullets[:]:
        bullet_speed = 6.0 if bullet.get('is_helper', False) else 8.0
        bullet['pos'][0] += bullet_speed * bullet['direction'][0]
        bullet['pos'][1] += bullet_speed * bullet['direction'][1]
        if 'direction' in bullet and len(bullet['direction']) > 2:
            bullet['pos'][2] += bullet_speed * bullet['direction'][2]

        # Check if bullet is out of bounds
        if abs(bullet['pos'][0]) > GRID_LENGTH or abs(bullet['pos'][1]) > GRID_LENGTH:
            # Only count missed bullets for the player, not the helper
            if not bullet.get('is_helper', False):
                game_state.player_missed_bullets += 1

                # Check game over condition
                if game_state.player_missed_bullets >= 100:
                    game_state.game_over = True

            game_state.player_bullets.remove(bullet)

        # NEW CODE: Add collision detection between player bullets (including helper bullets) and asteroids
        for asteroid in game_state.asteroids[:]:
            if bullet in game_state.player_bullets:  # Check if bullet still exists
                dx = bullet['pos'][0] - asteroid['pos'][0]
                dy = bullet['pos'][1] - asteroid['pos'][1]
                dz = bullet['pos'][2] - asteroid['pos'][2]

                distance = math.sqrt(dx * dx + dy * dy + dz * dz)

                # If collision detected
                if distance < asteroid['size'] + 5:  # 5 is bullet radius
                    # Create explosion
                    game_state.explosions.append({
                        'pos': [bullet['pos'][0], bullet['pos'][1], bullet['pos'][2]],
                        'size': 10,
                        'age': 0.0,
                        'duration': 0.3
                    })

                    # Remove bullet
                    if bullet in game_state.player_bullets:
                        game_state.player_bullets.remove(bullet)

                    # Reduce asteroid size or remove if too small
                    asteroid['size'] -= 5
                    if asteroid['size'] < 10:
                        # Create smaller explosion for asteroid destruction
                        game_state.explosions.append({
                            'pos': asteroid['pos'].copy(),
                            'size': 15,
                            'age': 0.0,
                            'duration': 0.5
                        })

                        # Create smaller asteroids
                        # Modify this section in your update_game_state function where asteroids are split:

                        # Create smaller asteroids
                        if len(game_state.asteroids) < 20:  # Limit total number of asteroids
                            for _ in range(2):
                                new_size = random.uniform(7, 12)

                                # Calculate new velocity with some randomness
                                new_vel = [
                                    asteroid['velocity'][0] * random.uniform(0.8, 1.2),
                                    asteroid['velocity'][1] * random.uniform(0.8, 1.2),
                                    asteroid['velocity'][2] * random.uniform(0.8, 1.2)
                                ]

                                # Add speed to make sure it moves
                                speed_factor = 1.2
                                new_vel = [v * speed_factor for v in new_vel]

                                # Create new asteroid with offset position
                                offset = 10
                                new_pos = [
                                    asteroid['pos'][0] + random.uniform(-offset, offset),
                                    asteroid['pos'][1] + random.uniform(-offset, offset),
                                    asteroid['pos'][2] + random.uniform(-offset, offset)
                                ]

                                # Either inherit the parent's type or randomly generate a new one
                                if random.random() < 0.7 and 'type' in asteroid:
                                    # 70% chance to keep parent type
                                    new_type = asteroid['type']
                                else:
                                    # 30% chance for a new random type
                                    new_type = random.randint(0, 2)

                                game_state.asteroids.append({
                                    'pos': new_pos,
                                    'size': new_size,
                                    'velocity': new_vel,
                                    'rotation': [random.uniform(0, 360) for _ in range(3)],
                                    'rotation_speed': [random.uniform(-2, 2) for _ in range(3)],
                                    'trail_particles': [],
                                    'heat_level': random.uniform(0.5, 1.0),
                                    'type': new_type  # Add type property to new asteroids
                                })

                        # Remove original asteroid
                        game_state.asteroids.remove(asteroid)
                    break  # Stop checking other asteroids for this bullet

    # ULTRA-ROBUST BULLET COLLISION DETECTION
    # This is a much simpler, brute-force approach that will guarantee bullets don't pass through

    # Handle enemy bullets with guaranteed collision detection
    for bullet in game_state.enemy_bullets[:]:
        # Store initial position
        initial_pos = bullet['pos'].copy()

        # Move bullet (save the movement increment for later collision check)
        speed = 5.0 if game_state.enemy_shooting_style < 3 else 4.0
        delta_x = speed * bullet['direction'][0]
        delta_y = speed * bullet['direction'][1]
        delta_z = speed * bullet['direction'][2]

        bullet['pos'][0] += delta_x
        bullet['pos'][1] += delta_y
        bullet['pos'][2] += delta_z

        # Check if out of bounds
        if abs(bullet['pos'][0]) > GRID_LENGTH or abs(bullet['pos'][1]) > GRID_LENGTH:
            if bullet in game_state.enemy_bullets:
                game_state.enemy_bullets.remove(bullet)
            continue

        # COLLISION DETECTION - Sampling approach
        # Check multiple points along the bullet's path
        collision_detected = False
        player_radius = 60  # Significantly increased collision radius

        # Divide the bullet's movement path into 10 segments for thorough checking
        for t in range(11):  # Check 11 points (including start and end)
            # Calculate position at this point
            t_fraction = t / 10.0
            check_point = [
                initial_pos[0] + t_fraction * delta_x,
                initial_pos[1] + t_fraction * delta_y,
                initial_pos[2] + t_fraction * delta_z
            ]

            # Calculate distance to player at this point
            dx = check_point[0] - game_state.player_pos[0]
            dy = check_point[1] - game_state.player_pos[1]
            dz = check_point[2] - game_state.player_pos[2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            # Check for collision with player or shield
            if not game_state.cheat_mode and distance < player_radius:
                # HIT PLAYER
                collision_detected = True
                game_state.player_lives -= 1

                # Create explosion at hit point
                game_state.explosions.append({
                    'pos': check_point.copy(),
                    'size': 20,
                    'age': 0.0,
                    'duration': 0.5
                })

                # Check game over condition
                if game_state.player_lives <= 0:
                    game_state.game_over = True

                # Remove bullet and break sampling loop
                if bullet in game_state.enemy_bullets:
                    game_state.enemy_bullets.remove(bullet)
                break

            elif game_state.cheat_mode and distance < game_state.shield_radius:
                # HIT SHIELD
                collision_detected = True

                # Update last_shield_hit time for visual effect
                game_state.last_shield_hit = time.time()

                # Create shield impact effect
                game_state.explosions.append({
                    'pos': check_point.copy(),
                    'size': 12,
                    'age': 0.0,
                    'duration': 0.3
                })

                # Remove bullet and break sampling loop
                if bullet in game_state.enemy_bullets:
                    game_state.enemy_bullets.remove(bullet)
                break

        # If collision was detected and handled, continue to next bullet
        if collision_detected:
            continue

    # Enemy shooting - if visible
    if game_state.enemy_visible and random.random() < 0.03:
        # Fire in random direction (not targeting the player)
        angle_h = random.uniform(0, 360)  # Random horizontal angle
        angle_v = random.uniform(-30, 30)  # Random vertical angle (slightly downward on average)

        # Convert angles to direction vector
        dx = math.cos(math.radians(angle_h)) * math.cos(math.radians(angle_v))
        dy = math.sin(math.radians(angle_h)) * math.cos(math.radians(angle_v))
        dz = math.sin(math.radians(angle_v))

        # Create the bullet
        game_state.enemy_bullets.append({
            'pos': game_state.enemy_pos.copy(),
            'direction': [dx, dy, dz]
        })

    # Collision detection for player bullets with enemy
    for bullet in game_state.player_bullets[:]:
        if not game_state.enemy_visible:
            continue

        # Use 3D distance calculation
        dx = bullet['pos'][0] - game_state.enemy_pos[0]
        dy = bullet['pos'][1] - game_state.enemy_pos[1]
        dz = bullet['pos'][2] - game_state.enemy_pos[2]

        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        # Increased collision radius and check all axes
        if distance < 35 * game_state.enemy_size:  # Adjust collision radius based on enemy size
            # Only remove if the bullet still exists
            if bullet in game_state.player_bullets:
                game_state.player_bullets.remove(bullet)
                game_state.enemy_lives -= 1

                # Add explosion at bullet impact
                game_state.explosions.append({
                    'pos': [bullet['pos'][0], bullet['pos'][1], bullet['pos'][2]],
                    'size': 10,
                    'age': 0.0,
                    'duration': 0.5
                })

                if game_state.enemy_lives <= 0:
                    # Enemy defeated - increment kill counter
                    game_state.enemies_killed += 1

                    # Check if helper aircraft should be activated
                    if game_state.enemies_killed >= 3 and not game_state.helper_active:
                        game_state.helper_active = True

                    # Spawn a life gift at the enemy's position
                    game_state.life_gifts.append({
                        'pos': game_state.enemy_pos.copy(),
                        'age': 0.0
                    })

                    # Player upgrades
                    game_state.player_bullet_count += 1
                    game_state.player_shooting_speed += 0.1

                    # Add larger explosion at enemy position
                    game_state.explosions.append({
                        'pos': [game_state.enemy_pos[0], game_state.enemy_pos[1], game_state.enemy_pos[2]],
                        'size': 30,
                        'age': 0.0,
                        'duration': 1.0
                    })

                    # Respawn enemy with more lives (up to 5) and new color
                    game_state.enemy_pos = game_state.generate_random_position(upper_area_only=True)
                    game_state.enemy_max_lives = min(5, game_state.enemy_max_lives + 1)
                    game_state.enemy_lives = game_state.enemy_max_lives
                    game_state.enemy_visible = True  # Make sure it's visible
                    game_state.enemy_teleport_time = current_time  # Reset teleport timer

                    # Increase evolution level and assign new color
                    game_state.enemy_evolution = min(4, game_state.enemy_evolution + 1)
                    game_state.enemy_color = game_state.generate_enemy_color(game_state.enemy_evolution)

                    # New shooting style and color
                    game_state.enemy_shooting_style = random.randint(0, 4)
                    game_state.enemy_bullet_color = [
                        random.uniform(0.5, 1.0),
                        random.uniform(0.2, 0.8),
                        random.uniform(0.2, 0.8)
                    ]

                    # Trigger enhanced aurora effect
                    game_state.aurora_effect = True
                    game_state.aurora_time = current_time
                    game_state.aurora_colors = game_state.generate_random_aurora_colors()

    # Check for bullet collisions (player vs enemy bullets)
    for p_bullet in game_state.player_bullets[:]:
        for e_bullet in game_state.enemy_bullets[:]:
            dx = p_bullet['pos'][0] - e_bullet['pos'][0]
            dy = p_bullet['pos'][1] - e_bullet['pos'][1]
            dz = p_bullet['pos'][2] - e_bullet['pos'][2]

            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            # Use larger collision radius
            if distance < 15:
                # Create explosion effect
                game_state.explosions.append({
                    'pos': [(p_bullet['pos'][0] + e_bullet['pos'][0]) / 2,
                            (p_bullet['pos'][1] + e_bullet['pos'][1]) / 2,
                            (p_bullet['pos'][2] + e_bullet['pos'][2]) / 2],
                    'size': 15,
                    'age': 0.0,
                    'duration': 0.7
                })

                # Make sure to check if bullets still exist in lists
                if p_bullet in game_state.player_bullets:
                    game_state.player_bullets.remove(p_bullet)
                if e_bullet in game_state.enemy_bullets:
                    game_state.enemy_bullets.remove(e_bullet)
                break

    # Update asteroid positions and trails
    for asteroid in game_state.asteroids:
        # Update position based on velocity - asteroids now definitely move!
        asteroid['pos'][0] += asteroid['velocity'][0]
        asteroid['pos'][1] += asteroid['velocity'][1]
        asteroid['pos'][2] += asteroid['velocity'][2]

        # Update rotation
        asteroid['rotation'][0] += asteroid['rotation_speed'][0]
        asteroid['rotation'][1] += asteroid['rotation_speed'][1]
        asteroid['rotation'][2] += asteroid['rotation_speed'][2]

        # Keep rotation angles in range 0-360
        for i in range(3):
            asteroid['rotation'][i] %= 360

        # Update trail particles
        update_asteroid_trail(asteroid, dt)

        # Keep asteroids within window boundaries with wrap-around
        boundary = GRID_LENGTH - asteroid['size']

        # Check if asteroid is beyond boundary in any dimension
        if abs(asteroid['pos'][0]) > boundary or abs(asteroid['pos'][1]) > boundary:
            # Wrap around to opposite edge (slightly in from the edge)
            if asteroid['pos'][0] > boundary:
                asteroid['pos'][0] = -boundary + asteroid['size']
            elif asteroid['pos'][0] < -boundary:
                asteroid['pos'][0] = boundary - asteroid['size']

            if asteroid['pos'][1] > boundary:
                asteroid['pos'][1] = -boundary + asteroid['size']
            elif asteroid['pos'][1] < -boundary:
                asteroid['pos'][1] = boundary - asteroid['size']

            # Clear trail particles when wrapping around
            asteroid['trail_particles'] = []

            # Slightly adjust velocity direction while maintaining magnitude
            speed = math.sqrt(asteroid['velocity'][0] ** 2 + asteroid['velocity'][1] ** 2)
            angle_change = random.uniform(-30, 30)  # Random angle change in degrees
            angle = math.degrees(math.atan2(asteroid['velocity'][1], asteroid['velocity'][0])) + angle_change
            asteroid['velocity'][0] = speed * math.cos(math.radians(angle))
            asteroid['velocity'][1] = speed * math.sin(math.radians(angle))

    # Collision detection for player with asteroids - no damage in cheat mode
    if not game_state.cheat_mode:
        for asteroid in game_state.asteroids:
            dx = asteroid['pos'][0] - game_state.player_pos[0]
            dy = asteroid['pos'][1] - game_state.player_pos[1]
            dz = asteroid['pos'][2] - game_state.player_pos[2]

            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance < (35 + asteroid['size']):  # Increased player radius for larger ship
                # Create explosion and reposition the asteroid
                game_state.player_lives -= 1

                game_state.explosions.append({
                    'pos': [asteroid['pos'][0], asteroid['pos'][1], asteroid['pos'][2]],
                    'size': asteroid['size'] + 5,
                    'age': 0.0,
                    'duration': 0.7
                })

                # Reposition the asteroid away from the player (within boundaries)
                new_pos = game_state.generate_random_position()
                asteroid['pos'] = new_pos

                # Clear trail particles after repositioning
                asteroid['trail_particles'] = []

                # Check game over condition
                if game_state.player_lives <= 0:
                    game_state.game_over = True
    else:
        # In cheat mode, bounces asteroids off shield
        for asteroid in game_state.asteroids:
            dx = asteroid['pos'][0] - game_state.player_pos[0]
            dy = asteroid['pos'][1] - game_state.player_pos[1]
            dz = asteroid['pos'][2] - game_state.player_pos[2]

            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            collision_distance = game_state.shield_radius + asteroid['size'] - 5  # Leave room for shield effect

            if distance < collision_distance:
                # Update last_shield_hit time for visual effect
                game_state.last_shield_hit = time.time()

                # Create shield impact effect
                game_state.explosions.append({
                    'pos': [
                        game_state.player_pos[0] + dx * game_state.shield_radius / distance,
                        game_state.player_pos[1] + dy * game_state.shield_radius / distance,
                        game_state.player_pos[2] + dz * game_state.shield_radius / distance
                    ],
                    'size': asteroid['size'] * 0.5,
                    'age': 0.0,
                    'duration': 0.4
                })

                # Reflect asteroid velocity like a bounce off the shield
                if distance > 0:
                    # Normalized direction from player to asteroid
                    nx = dx / distance
                    ny = dy / distance
                    nz = dz / distance

                    # Calculate dot product of velocity and normal
                    dot = (asteroid['velocity'][0] * nx +
                           asteroid['velocity'][1] * ny +
                           asteroid['velocity'][2] * nz)

                    # Reflect velocity with some random variation
                    bounce_factor = -1.5  # Stronger bounce
                    randomness = random.uniform(0.8, 1.2)  # Add some variability

                    asteroid['velocity'][0] += dot * nx * bounce_factor * randomness
                    asteroid['velocity'][1] += dot * ny * bounce_factor * randomness
                    asteroid['velocity'][2] += dot * nz * bounce_factor * randomness

                    # Move asteroid outside shield radius to prevent multiple collisions
                    push_distance = collision_distance + 5
                    asteroid['pos'][0] = game_state.player_pos[0] + nx * push_distance
                    asteroid['pos'][1] = game_state.player_pos[1] + ny * push_distance
                    asteroid['pos'][2] = game_state.player_pos[2] + nz * push_distance

    # Collision detection between player and enemy UFO
    if game_state.enemy_visible and not game_state.cheat_mode:
        dx = game_state.player_pos[0] - game_state.enemy_pos[0]
        dy = game_state.player_pos[1] - game_state.enemy_pos[1]
        dz = game_state.player_pos[2] - game_state.enemy_pos[2]

        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        collision_radius = 40 + 30 * game_state.enemy_size  # Combined collision radius

        if distance < collision_radius:
            # Damage both the player and enemy
            game_state.player_lives -= 1
            game_state.enemy_lives -= 1

            # Create large explosion at collision point
            collision_point = [
                (game_state.player_pos[0] + game_state.enemy_pos[0]) / 2,
                (game_state.player_pos[1] + game_state.enemy_pos[1]) / 2,
                (game_state.player_pos[2] + game_state.enemy_pos[2]) / 2
            ]

            game_state.explosions.append({
                'pos': collision_point,
                'size': 40,
                'age': 0.0,
                'duration': 0.8
            })

            # Bounce the player back
            direction_x = dx / distance if distance > 0 else 0
            direction_y = dy / distance if distance > 0 else 0
            game_state.player_pos[0] += direction_x * 20
            game_state.player_pos[1] += direction_y * 20

            # Teleport the enemy to a new position after collision
            game_state.enemy_pos = game_state.generate_random_position(upper_area_only=True)

            # Check if either is defeated
            if game_state.player_lives <= 0:
                game_state.game_over = True

            if game_state.enemy_lives <= 0:
                # Handle enemy defeat (same as when shot by bullet)
                game_state.enemies_killed += 1

                if game_state.enemies_killed >= 3 and not game_state.helper_active:
                    game_state.helper_active = True

                game_state.life_gifts.append({
                    'pos': collision_point.copy(),
                    'age': 0.0
                })

                game_state.player_bullet_count += 1
                game_state.player_shooting_speed += 0.1

                # Respawn enemy
                game_state.enemy_max_lives = min(5, game_state.enemy_max_lives + 1)
                game_state.enemy_lives = game_state.enemy_max_lives
                game_state.enemy_evolution = min(4, game_state.enemy_evolution + 1)
                game_state.enemy_color = game_state.generate_enemy_color(game_state.enemy_evolution)

                # New shooting style and color
                game_state.enemy_shooting_style = random.randint(0, 4)
                game_state.enemy_bullet_color = [
                    random.uniform(0.5, 1.0),
                    random.uniform(0.2, 0.8),
                    random.uniform(0.2, 0.8)
                ]

                # Trigger aurora effect
                game_state.aurora_effect = True
                game_state.aurora_time = time.time()
                game_state.aurora_colors = game_state.generate_random_aurora_colors()

    # Update explosions
    for explosion in game_state.explosions[:]:
        # Update age
        time_factor = 1.0 / explosion['duration'] if explosion['duration'] > 0 else 1.0
        explosion['age'] += dt * time_factor

        # Remove old explosions
        if explosion['age'] >= 1.0:
            game_state.explosions.remove(explosion)

    # Check aurora effect timer
    if game_state.aurora_effect:
        if current_time - game_state.aurora_time > 1.5:  # Increased duration to 1.5 seconds
            game_state.aurora_effect = False

    # Keep player within window boundaries
    boundary = GRID_LENGTH - 40  # Keep clear of the very edge, allowing for ship size
    game_state.player_pos[0] = max(-boundary, min(boundary, game_state.player_pos[0]))
    game_state.player_pos[1] = max(-boundary, min(boundary, game_state.player_pos[1]))

    # Update star twinkle effect
    for star in game_state.stars:
        # Slightly adjust blink rate for variety
        star['blink_rate'] = star['blink_rate'] * 0.999 + random.uniform(0.45, 2.1) * 0.001

    # Update planet rotation angles
    for planet in game_state.planets:
        planet['rotation'] += planet['rotation_speed']
        if planet['rotation'] > 360:
            planet['rotation'] -= 360

    

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement
    """
    global game_state

    # Handle spacebar for pause/resume
    if key == b' ':  # Spacebar
        if game_state.game_over:
            return
            
        if game_state.resuming:
            return  # Ignore spacebar during resume countdown
            
        if game_state.paused:
            # Start resuming countdown
            game_state.paused = False
            game_state.resuming = True
            game_state.countdown_start_time = time.time()
        else:
            # Pause the game
            game_state.paused = True
        
        return
    
    # Handle cheat mode toggle with 'c' key
    if key == b'i':
        game_state.cheat_mode = not game_state.cheat_mode
        return

    if game_state.game_over:
        # Only allow 'r' key in game over state
        if key == b'r':
            # Reset the game
            game_state = GameState()
        return
        
    # Don't process movement keys while paused or resuming
    if game_state.paused or game_state.resuming:
        return

    movement_speed = 15

    # Move forward (W key)
    if key == b'w':
        game_state.player_pos[1] += movement_speed

    # Move backward (S key)
    if key == b's':
        game_state.player_pos[1] -= movement_speed

    # Move left (A key)
    if key == b'a':
        game_state.player_pos[0] -= movement_speed

    # Move right (D key)
    if key == b'd':
        game_state.player_pos[0] += movement_speed

    # Forward left diagonal (Q key)
    if key == b'q':
        game_state.player_pos[0] -= movement_speed * 0.7
        game_state.player_pos[1] += movement_speed * 0.7

    # Forward right diagonal (E key)
    if key == b'e':
        game_state.player_pos[0] += movement_speed * 0.7
        game_state.player_pos[1] += movement_speed * 0.7

    # Backward left diagonal (Z key)
    if key == b'z':
        game_state.player_pos[0] -= movement_speed * 0.7
        game_state.player_pos[1] -= movement_speed * 0.7

    # Backward right diagonal (X key - changed from 'c' to 'x' since 'c' is now used for cheat mode)
    if key == b'c':
        game_state.player_pos[0] += movement_speed * 0.7
        game_state.player_pos[1] -= movement_speed * 0.7

    # Make sure player stays within the window boundaries
    boundary = GRID_LENGTH - 40  # Keep clear of the very edge, allowing for ship size
    game_state.player_pos[0] = max(-boundary, min(boundary, game_state.player_pos[0]))
    game_state.player_pos[1] = max(-boundary, min(boundary, game_state.player_pos[1]))


def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos
    
    # Don't process camera controls when paused or resuming
    if game_state.paused or game_state.resuming:
        return

    if not game_state.first_person_mode:
        x, y, z = camera_pos
        # Move camera up (UP arrow key)
        if key == GLUT_KEY_UP:
            z = min(2000, z + 10)

        # Move camera down (DOWN arrow key)
        if key == GLUT_KEY_DOWN:
            z = max(20, z - 10)

        # Moving camera left (LEFT arrow key)
        if key == GLUT_KEY_LEFT:
            x -= 10

        # Moving camera right (RIGHT arrow key)
        if key == GLUT_KEY_RIGHT:
            x += 10

        camera_pos = (x, y, z)


def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
    if game_state.game_over or game_state.paused or game_state.resuming:
        return

    current_time = time.time()

    # Left mouse button fires bullets
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Time-based shooting control with speed factor
        if current_time - game_state.last_shot_time > (1.0 / game_state.player_shooting_speed):
            game_state.last_shot_time = current_time

            # Calculate direction vector (forward in player orientation)
            direction = game_state.player_direction.copy()

            # Fire multiple bullets if player has upgrades
            spread_angle = 10.0  # Degrees between bullets for multi-shot

            if game_state.player_bullet_count == 1:
                # Single bullet
                bullet_pos = game_state.player_pos.copy()
                bullet_pos[1] += 15  # Bullet starts at the tip of the barrel

                game_state.player_bullets.append({
                    'pos': bullet_pos,
                    'direction': direction
                })
            else:
                # Multiple bullets with spread
                start_angle = -spread_angle * (game_state.player_bullet_count - 1) / 2

                for i in range(game_state.player_bullet_count):
                    angle = start_angle + i * spread_angle
                    angle_rad = math.radians(angle)

                    # Calculate direction with spread
                    bullet_dir = direction.copy()

                    # Apply rotation matrix for the spread
                    bullet_dir[0] = direction[0] * math.cos(angle_rad) - direction[1] * math.sin(angle_rad)
                    bullet_dir[1] = direction[0] * math.sin(angle_rad) + direction[1] * math.cos(angle_rad)

                    # Normalize
                    length = math.sqrt(bullet_dir[0] ** 2 + bullet_dir[1] ** 2)
                    if length > 0:
                        bullet_dir[0] /= length
                        bullet_dir[1] /= length

                    bullet_pos = game_state.player_pos.copy()
                    bullet_pos[1] += 15  # Bullet starts at the tip of the barrel

                    game_state.player_bullets.append({
                        'pos': bullet_pos,
                        'direction': bullet_dir
                    })

    # Right mouse button toggles camera mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        game_state.first_person_mode = not game_state.first_person_mode


def showScreen():
    """
    Display function to render the game scene
    Last updated: 2025-05-06 20:45:28 UTC
    User: suprava-ssd
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)  # Set viewport size

    # Note: Removed glEnable(GL_DEPTH_TEST) - assume depth testing is configured elsewhere
    # or rely on draw order for correct rendering

    setupCamera()  # Configure camera perspective

    # Draw background elements first (stars, planets)
    draw_stars_and_planets()

    # Draw aurora effect if active
    if game_state.aurora_effect:
        draw_aurora_effect()

    # Draw the transparent grid (stars visible through it)
    draw_transparent_grid()

    # Draw asteroids with trails
    for asteroid in game_state.asteroids:
        # Draw the trail first (behind asteroid)
        draw_asteroid_trail(asteroid['trail_particles'])

        # Then draw the asteroid itself
        glPushMatrix()
        glTranslatef(asteroid['pos'][0], asteroid['pos'][1], asteroid['pos'][2])
        draw_asteroid(asteroid['size'], asteroid['type'], asteroid['rotation'], asteroid['heat_level'])
        glPopMatrix()

    # Draw player ship
    damage_state = 0
    if game_state.player_lives <= 6:
        damage_state = 1
    if game_state.player_lives <= 3:
        damage_state = 2

    glPushMatrix()
    glTranslatef(game_state.player_pos[0], game_state.player_pos[1], game_state.player_pos[2])

    # Calculate proper orientation
    angle = math.degrees(math.atan2(game_state.player_direction[0], game_state.player_direction[1]))
    glRotatef(angle, 0, 0, 1)
    draw_stealth_fighter(damage_state, is_helper=False)  # Using the updated fighter model

    # Draw shield if cheat mode is active
    if game_state.cheat_mode:
        draw_shield()

    glPopMatrix()

    # Draw helper aircraft if active
    if game_state.helper_active:
        # Position helper aircraft relative to player
        helper_pos = [
            game_state.player_pos[0] + game_state.helper_offset[0],
            game_state.player_pos[1] + game_state.helper_offset[1],
            game_state.player_pos[2] + game_state.helper_offset[2]
        ]

        glPushMatrix()
        glTranslatef(helper_pos[0], helper_pos[1], helper_pos[2])

        # Helper aircraft follows same orientation as player
        glRotatef(angle, 0, 0, 1)
        draw_stealth_fighter(0, is_helper=True)  # Helper aircraft (undamaged)
        glPopMatrix()

    # Draw enemy UFO with evolution-based color
    if game_state.enemy_visible:
        damage_level = 1.0 - (game_state.enemy_lives / game_state.enemy_max_lives)
        glPushMatrix()
        glTranslatef(game_state.enemy_pos[0], game_state.enemy_pos[1], game_state.enemy_pos[2])
        glRotatef(time.time() * 30 % 360, 0, 0, 1)  # Spin effect
        draw_ufo_enemy(damage_level, game_state.enemy_color)  # Pass color based on evolution
        glPopMatrix()

    # Draw life gift pickups
    for gift in game_state.life_gifts:
        draw_life_gift(gift)

    # Draw player bullets
    for bullet in game_state.player_bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        draw_bullet(True, is_helper=bullet.get('is_helper', False))
        glPopMatrix()

    # Draw enemy bullets
    for bullet in game_state.enemy_bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        draw_bullet(False)
        glPopMatrix()

    # Draw explosions
    for explosion in game_state.explosions:
        glPushMatrix()
        glTranslatef(explosion['pos'][0], explosion['pos'][1], explosion['pos'][2])
        draw_explosion(explosion['size'], explosion['age'])
        glPopMatrix()

    # Draw pause message if game is paused
    if game_state.paused:
        # Switch to orthographic projection for 2D overlay
        # Removed glPushAttrib/glPopAttrib and glEnable(GL_BLEND)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Draw black overlay - simulate transparency with dark color
        # instead of using alpha blending
        glColor3f(0, 0, 0)  # Solid black instead of transparent
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Draw pause text - using direct screen coordinates to ensure visibility
        draw_centered_text_2d(game_state.pause_message, 0, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 1.0, 1.0)
        draw_centered_text_2d("Press SPACEBAR to continue", -40, GLUT_BITMAP_HELVETICA_18, 0.8, 0.8, 1.0)

    # Draw resume countdown if resuming
    elif game_state.resuming:
        # Switch to orthographic projection for 2D overlay
        # Removed glPushAttrib/glPopAttrib
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Draw black overlay - removed alpha blending
        glColor3f(0, 0, 0)  # Solid black instead of transparent
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Calculate how far into the resume process we are
        elapsed = time.time() - game_state.countdown_start_time

        # Show the "Get Ready" message for first 2 seconds
        if elapsed < game_state.resume_message_duration:
            draw_centered_text_2d(game_state.resume_message, 0, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 1.0, 0.3)
        # Then show countdown 3,2,1
        else:
            countdown_elapsed = elapsed - game_state.resume_message_duration
            countdown_number = 3 - int(countdown_elapsed)

            if countdown_number >= 1:
                # Draw countdown number with bright yellow color - larger size
                countdown_text = str(countdown_number)
                draw_centered_text_2d(countdown_text, 0, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 1.0, 0.0)

    # Draw game over message if needed
    if game_state.game_over:
        # Switch to orthographic projection for 2D overlay
        # Removed glPushAttrib/glPopAttrib
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Draw black overlay - without alpha
        glColor3f(0, 0, 0)  # Solid black instead of transparent
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        # Draw game over text with red color
        draw_centered_text_2d("GAME OVER", 20, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 0.2, 0.2)
        draw_centered_text_2d("Press 'R' to restart", -40, GLUT_BITMAP_HELVETICA_18, 1.0, 0.7, 0.7)

    # IMPORTANT: Draw the HUD text at the very end, on top of everything else
    draw_hud_text()

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    if game_state.first_person_mode:
        # First-person view from player ship
        px, py, pz = game_state.player_pos

        # Calculate look-at point based on player direction
        dx, dy, dz = game_state.player_direction

        # Look from slightly above the ship for better view
        gluLookAt(px, py, pz + 10,  # Camera position (player position + slight height)
                  px + dx * 100, py + dy * 100, pz,  # Look-at point (forward direction)
                  0, 0, 1)  # Up vector (z-axis)
    else:
        # Third-person/overview camera
        x, y, z = camera_pos
        gluLookAt(x, y, z,  # Camera position
                  0, 0, 0,  # Look-at target (origin)
                  0, 0, 1)  # Up vector (z-axis)


def idle():
    """
    Idle function that runs continuously:
    - Updates game state
    - Triggers screen redraw for real-time updates.
    """
    update_game_state()

    # Ensure the screen updates with the latest changes
    glutPostRedisplay()




# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"Space Shooter Game")  # Create the window

    # Enable alpha blending for transparent effects


    # Set background color to black for space
    # glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)  # Register special key listener
    glutMouseFunc(mouseListener)  # Register mouse listener
    glutIdleFunc(idle)  # Register the idle function

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()