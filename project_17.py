from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

class AlphaRenderer:
    def __init__(self):
        self.effect_type = "none"
        self.base_brightness = 1.0

    def start_effect(self, effect_type, brightness=1.0):
        self.effect_type = effect_type
        self.base_brightness = brightness
        pass

    def end_effect(self):
        self.effect_type = "none"
        self.base_brightness = 1.0
        pass

    def set_color(self, r, g, b, a):
        if self.effect_type == "glow":
            brightness = self.base_brightness * a
            enhanced_r = r * brightness + 0.1 * a
            enhanced_g = g * brightness + 0.2 * a
            enhanced_b = b * brightness + 0.3 * a
            glColor3f(enhanced_r, enhanced_g, enhanced_b)

        elif self.effect_type == "fade":
            glColor3f(r * a, g * a, b * a)

        elif self.effect_type == "ghost":
            glColor3f(r * 0.7 + 0.2, g * 0.7 + 0.2, b * 0.7 + 0.4)

        else:
            glColor3f(r, g, b)

alpha_fx = AlphaRenderer()
class GameState:
    def __init__(self):
        self.player_pos = [0, 0, 50]
        self.player_direction = [0, 1, 0]
        self.player_lives = 9
        self.player_bullets = []
        self.player_missed_bullets = 0
        self.player_bullet_count = 1
        self.player_shooting_speed = 1.0
        self.first_person_mode = False
        self.last_shield_hit = 0.0
        self.player_flicker = False
        self.flicker_start_time = 0
        self.flicker_duration = 0.5
        self.cheat_mode = False
        self.shield_radius = 45
        self.shield_opacity = 0.3
        self.shield_color = [0.3, 0.7, 1.0]
        self.shield_pulse = 0

        self.enemies_killed = 0
        self.helper_active = False
        self.helper_offset = [-30, 0, 0]
        self.helper_target = None
        self.helper_last_shot_time = 0
        self.helper_shooting_interval = 1.0

        self.life_gifts = []
        self.gift_pulse = 0

        self.paused = False
        self.pause_message = "Waiting for your arrival"

        self.resuming = False
        self.resume_message = "Get Ready to Fight, Astronaut!"
        self.resume_countdown = 3
        self.countdown_start_time = 0
        self.countdown_interval = 1.0
        self.resume_message_duration = 2.0

        self.enemy_pos = self.generate_random_position(upper_area_only=True)
        self.enemy_lives = 1
        self.enemy_bullets = []
        self.enemy_shooting_style = 0
        self.enemy_bullet_color = [1.0, 0.0, 0.0]
        self.enemy_max_lives = 1
        self.enemy_color = [0.5, 0.5, 0.5]
        self.enemy_evolution = 0
        self.enemy_size = 2.0

        self.enemy_speed = 1.0
        self.enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1), 0]
        self.enemy_teleport_time = time.time()
        self.enemy_teleport_interval = 5.0
        self.enemy_visible = True
        self.enemy_target_pos = self.generate_random_position(upper_area_only=True)

        self.explosions = []

        self.asteroids = []
        for _ in range(10):
            vel_x = random.uniform(-3.0, 3.0)
            vel_y = random.uniform(-3.0, 3.0)
            if abs(vel_x) < 1.0: vel_x *= 2.0
            if abs(vel_y) < 1.0: vel_y *= 2.0

            self.asteroids.append({
                'pos': self.generate_random_position(),
                'size': random.uniform(8, 18),
                'type': random.randint(0, 2),
                'rotation': [random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)],
                'rotation_speed': [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)],
                'velocity': [vel_x, vel_y, 0],
                'trail_particles': [],
                'heat_level': random.uniform(0.7, 1.0)
            })

        self.stars = []
        for _ in range(300):
            self.stars.append({
                'pos': [random.uniform(-2000, 2000), random.uniform(-2000, 2000), random.uniform(-800, -200)],
                'brightness': random.uniform(0.5, 1.0),
                'blink_rate': random.uniform(0.5, 2.0)
            })

        self.planets = []
        for _ in range(15):
            self.planets.append({
                'pos': [random.uniform(-1500, 1500), random.uniform(-1500, 1500), random.uniform(-700, -300)],
                'size': random.uniform(20, 80),
                'color': [random.uniform(0.2, 0.8), random.uniform(0.2, 0.8), random.uniform(0.2, 0.8)],
                'rings': random.random() > 0.7,
                'ring_color': [random.uniform(0.2, 0.9), random.uniform(0.2, 0.9), random.uniform(0.2, 0.9)],
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(0.01, 0.05) * (1 if random.random() > 0.5 else -1)
            })

        self.aurora_effect = False
        self.aurora_time = 0
        self.aurora_colors = []

        self.last_shot_time = 0
        self.game_over = False

    def generate_random_position(self, upper_area_only=False):
        safe_boundary_x = GRID_LENGTH * 0.8
        if upper_area_only:
            y_min = -0.2 * GRID_LENGTH
            y_max = safe_boundary_x
        else:
            y_min = -safe_boundary_x
            y_max = safe_boundary_x
        pos = [random.uniform(-safe_boundary_x, safe_boundary_x),
               random.uniform(y_min, y_max),
               random.uniform(30, 80)]

        while True:
            distance = math.sqrt((pos[0] - self.player_pos[0]) ** 2 +
                                 (pos[1] - self.player_pos[1]) ** 2 +
                                 (pos[2] - self.player_pos[2]) ** 2)
            if distance > 150:
                return pos

            pos = [random.uniform(-safe_boundary_x, safe_boundary_x),
                   random.uniform(y_min, y_max),
                   random.uniform(30, 80)]

    def generate_enemy_color(self, evolution_level):
        if evolution_level == 0:
            return [0.5, 0.5, 0.5]
        elif evolution_level == 1:
            return [0.7, 0.2, 0.2]
        elif evolution_level == 2:
            return [0.2, 0.7, 0.2]
        elif evolution_level == 3:
            return [0.2, 0.2, 0.8]
        else:
            return [0.8, 0.2, 0.8]

    def generate_random_aurora_colors(self):
        colors = []
        for _ in range(5):
            hue = random.random()
            h = hue * 6.0
            i = int(h)
            f = h - i
            
            p = 0.0
            q = 1.0 * (1.0 - f)
            t = 1.0 * f
            
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

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960
GRID_LENGTH = 1000

game_state = GameState()

camera_pos = [0, -800, 800]
fovY = 65


def draw_hud_text():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0.0, WINDOW_WIDTH, 0.0, WINDOW_HEIGHT, -1.0, 1.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    left_margin = 20
    top_margin = WINDOW_HEIGHT - 30
    line_height = 25
    def draw_hud_line(y_pos, text, color=(1.0, 1.0, 1.0)):
        glColor3f(0.0, 0.0, 0.0)
        glRasterPos2i(left_margin + 1, y_pos - 1)

        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

        glColor3f(color[0], color[1], color[2])
        glRasterPos2f(left_margin, y_pos)

        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

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

    if game_state.helper_active:
        draw_hud_line(current_y, "Helper Active: YES", color=(0.0, 1.0, 0.0))
    else:
        draw_hud_line(current_y, f"Helper Active: NO ({game_state.enemies_killed}/3)",
                      color=(1.0, 0.5, 0.0))
    current_y -= line_height

    if game_state.cheat_mode:
        draw_hud_line(current_y, "INVINCIBLE MODE ACTIVE", color=(1.0, 0.3, 0.3))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text_2d(x, y, text, font=GLUT_BITMAP_HELVETICA_18, r=1.0, g=1.0, b=1.0):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def draw_centered_text_2d(text, y_offset=0, font=GLUT_BITMAP_TIMES_ROMAN_24, r=1.0, g=1.0, b=1.0):
    width = 0
    for char in text:
        width += glutBitmapWidth(font, ord(char))
    x = (WINDOW_WIDTH - width) / 2
    y = WINDOW_HEIGHT / 2 + y_offset
    draw_text_2d(x, y, text, font, r, g, b)


def draw_stealth_fighter(damaged_state=0, is_helper=False):
    glPushMatrix()
    if is_helper:
        glScalef(0.7, 0.7, 0.7)
    else:
        glScalef(1.5, 1.5, 1.5)

    if game_state.player_flicker and not is_helper:
        elapsed = time.time() - game_state.flicker_start_time
        if elapsed < game_state.flicker_duration:
            flicker_speed = 15.0
            if int(elapsed * flicker_speed) % 2 == 0:
                glColor3f(0.2, 0.5, 1.0)
            else:
                glColor3f(0.3, 0.4, 0.8)
        else:
            game_state.player_flicker = False
            glColor3f(0.3, 0.4, 0.8)
    else:

        if is_helper:

            glColor3f(0.3, 0.8, 0.9)
        else:
            if damaged_state == 0:
                glColor3f(0.3, 0.4, 0.8)
            elif damaged_state == 1:
                glColor3f(0.5, 0.3, 0.3)
            elif damaged_state == 2:
                glColor3f(0.6, 0.2, 0.2)

    glPushMatrix()
    glScalef(1.5, 3, 0.4)
    glBegin(GL_QUADS)
    glVertex3f(0, 10, 0)
    glVertex3f(0, 10, 0)
    glVertex3f(-5, 0, 2)
    glVertex3f(5, 0, 2)
    glVertex3f(0, 10, 0)
    glVertex3f(0, 10, 0)
    glVertex3f(-5, 0, -2)
    glVertex3f(5, 0, -2)
    glVertex3f(-5, 0, 2)
    glVertex3f(5, 0, 2)
    glVertex3f(7, -10, 2)
    glVertex3f(-7, -10, 2)
    glVertex3f(-5, 0, -2)
    glVertex3f(5, 0, -2)
    glVertex3f(7, -10, -2)
    glVertex3f(-7, -10, -2)
    glEnd()
    glPopMatrix()
    def draw_wing(is_right=True):
        multiplier = 1 if is_right else -1
        glBegin(GL_QUADS)
        glVertex3f(0, 5, 0)
        glVertex3f(0, 5, 0)
        glVertex3f(multiplier * 20, -10, 0)
        glVertex3f(0, -10, 0)
        glEnd()
    def draw_tail_fin(is_right=True):
        multiplier = 1 if is_right else -1
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(multiplier * 3, -5, 0)
        glVertex3f(0, -5, 8)
        glEnd()

    if not is_helper or damaged_state < 2:
        glPushMatrix()
        glTranslatef(-15, 0, 0)
        if is_helper:
            glColor3f(0.2, 0.7, 0.8)
        else:
            glColor3f(0.2, 0.3, 0.7)
        draw_wing(is_right=False)
        glPopMatrix()

    if not is_helper or damaged_state < 1:
        glPushMatrix()
        glTranslatef(15, 0, 0)
        if is_helper:
            glColor3f(0.2, 0.7, 0.8)
        else:
            glColor3f(0.2, 0.3, 0.7)
        draw_wing(is_right=True)
        glPopMatrix()

    if not is_helper or damaged_state < 2:
        glPushMatrix()
        glTranslatef(-5, -20, 2)
        if is_helper:
            glColor3f(0.25, 0.75, 0.85)
        else:
            glColor3f(0.25, 0.35, 0.75)
        draw_tail_fin(is_right=False)
        glPopMatrix()

    if not is_helper or damaged_state < 1:
        glPushMatrix()
        glTranslatef(5, -20, 2)
        if is_helper:
            glColor3f(0.25, 0.75, 0.85)
        else:
            glColor3f(0.25, 0.35, 0.75)
        draw_tail_fin(is_right=True)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0, 3)

    if is_helper:
        glColor3f(0.4, 0.9, 1.0)
    elif damaged_state < 2:
        glColor3f(0.7, 0.9, 1.0)
    else:
        glColor3f(0.7, 0.3, 0.3)

    glPushMatrix()
    glScalef(4, 8, 2)
    glBegin(GL_QUADS)
    glVertex3f(0, 1, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(-1, 0, 0)
    glVertex3f(1, 0, 0)
    glVertex3f(-1, 0, 0)
    glVertex3f(1, 0, 0)
    glVertex3f(0, -1, 1)
    glVertex3f(0, -1, 1)
    glEnd()

    glPopMatrix()
    glPopMatrix()
    if not is_helper or damaged_state < 2:
        glPushMatrix()
        glTranslatef(-4, -25, 0)

        if is_helper:
            glColor3f(0.0, 0.8, 1.0)
        elif damaged_state < 1:
            glColor3f(1.0, 0.5, 0.0)
        else:
            glColor3f(0.5, 0.2, 0.1)

        glutSolidCone(2, 5, 10, 3)
        glPopMatrix()

    if not is_helper or damaged_state < 1:
        glPushMatrix()
        glTranslatef(4, -25, 0)
        if is_helper:
            glColor3f(0.0, 0.8, 1.0)
        else:
            glColor3f(1.0, 0.5, 0.0)

        glutSolidCone(2, 5, 10, 3)
        glPopMatrix()
    if is_helper:
        glColor3f(0.4, 0.8, 0.9)
    else:
        glColor3f(0.6, 0.6, 0.6)
    if not is_helper or damaged_state < 1:
        glPushMatrix()
        glTranslatef(-8, 5, -1)
        glScalef(0.5, 2, 0.5)
        glutSolidCube(3)
        glPopMatrix()
    if not is_helper or damaged_state < 1:
        glPushMatrix()
        glTranslatef(8, 5, -1)
        glScalef(0.5, 2, 0.5)
        glutSolidCube(3)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 5, -1)
    glScalef(0.8, 2.5, 0.5)
    glutSolidCube(3)
    glPopMatrix()
    if not is_helper or damaged_state < 2:
        glPushMatrix()
        glTranslatef(0, -27, 0)
        if is_helper:
            glColor3f(0.0, 0.9, 1.0)
        else:
            glColor3f(1.0, 0.7, 0.2)
        glutSolidSphere(3, 10, 10)
        glPopMatrix()

    glPopMatrix()

def draw_wireframe_sphere(radius, lats, longs):
    vertices = []
    for i in range(lats + 1):
        lat = math.pi * (-0.5 + float(i) / lats)
        z = math.sin(lat)
        zr = math.cos(lat)

        for j in range(longs + 1):
            lng = 2 * math.pi * float(j) / longs
            x = math.cos(lng) * zr
            y = math.sin(lng) * zr
            vertices.append((x * radius, y * radius, z * radius))
    glBegin(GL_LINES)
    for i in range(lats + 1):
        for j in range(longs):
            idx1 = i * (longs + 1) + j
            idx2 = i * (longs + 1) + j + 1
            glVertex3f(*vertices[idx1])
            glVertex3f(*vertices[idx2])
    glEnd()
    glBegin(GL_LINES)
    for i in range(lats):
        for j in range(longs + 1):
            idx1 = i * (longs + 1) + j
            idx2 = (i + 1) * (longs + 1) + j
            glVertex3f(*vertices[idx1])
            glVertex3f(*vertices[idx2])
    glEnd()


def draw_shield():
    alpha_fx.start_effect("glow", brightness=1.8)
    time_factor = time.time() * 2.5
    pulse_primary = 0.7 + 0.3 * math.sin(time_factor)
    pulse_secondary = 0.7 + 0.3 * math.sin(time_factor * 1.3 + 0.7)

    shield_opacity = 0.5 * pulse_primary
    alpha_fx.set_color(0.4, 0.7, 1.0, shield_opacity * 0.3)
    draw_wireframe_sphere(game_state.shield_radius + 5, 16, 16)


    alpha_fx.set_color(0.3, 0.6, 1.0, shield_opacity * 0.7)
    draw_wireframe_sphere(game_state.shield_radius, 20, 20)

    alpha_fx.set_color(0.4, 0.7, 1.0, shield_opacity * 0.6)
    draw_wireframe_sphere(game_state.shield_radius - 4, 18, 18)

    alpha_fx.set_color(0.5, 0.8, 1.0, shield_opacity * 0.8)
    draw_wireframe_sphere(game_state.shield_radius - 8, 16, 16)

    alpha_fx.set_color(0.7, 0.9, 1.0, shield_opacity * 0.7)
    draw_wireframe_sphere(game_state.shield_radius - 15, 12, 12)

    num_rings = 3
    for i in range(num_rings):
        ring_opacity = shield_opacity * (0.7 - i * 0.1) * pulse_secondary
        angle_x = (time.time() * 15 + i * 40) % 360
        angle_z = (time.time() * 20 + i * 60) % 360

        glPushMatrix()
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_z, 0, 0, 1)
        r = 0.4 + i * 0.2
        g = 0.6 + i * 0.2
        b = 1.0
        alpha_fx.set_color(r, g, b, ring_opacity)
        ring_radius = game_state.shield_radius * (0.9 - i * 0.15)
        tube_radius = 1.0 + i * 0.5
        draw_solid_torus(tube_radius, ring_radius, 8, 24)

        glPopMatrix()
    num_sparkles = 15
    for i in range(num_sparkles):
        angle1 = i * 137.5
        angle2 = i * 94.2 + time.time() * 20
        rad1 = math.radians(angle1)
        rad2 = math.radians(angle2)
        x = math.sin(rad1) * math.cos(rad2) * game_state.shield_radius
        y = math.sin(rad1) * math.sin(rad2) * game_state.shield_radius
        z = math.cos(rad1) * game_state.shield_radius
        glPushMatrix()
        glTranslatef(x, y, z)
        sparkle_size = 2.0 + 1.0 * math.sin(time.time() * 3.0 + i * 0.5)
        alpha_fx.set_color(1.0, 1.0, 1.0, 0.7 * pulse_secondary)
        glBegin(GL_LINES)
        glVertex3f(-sparkle_size, 0, 0)
        glVertex3f(sparkle_size, 0, 0)
        glVertex3f(0, -sparkle_size, 0)
        glVertex3f(0, sparkle_size, 0)
        glVertex3f(0, 0, -sparkle_size)
        glVertex3f(0, 0, sparkle_size)
        glEnd()

        glPopMatrix()
    if hasattr(game_state, 'last_shield_hit') and time.time() - game_state.last_shield_hit < 0.8:
        hit_progress = (time.time() - game_state.last_shield_hit) / 0.8
        ripple_size = hit_progress * 0.5
        ripple_opacity = (1.0 - hit_progress) * 0.9
        alpha_fx.set_color(0.7, 0.9, 1.0, ripple_opacity)
        draw_wireframe_sphere(game_state.shield_radius * (1.0 + ripple_size), 16, 16)
        if hit_progress > 0.2:
            second_ripple = (hit_progress - 0.2) / 0.8
            second_size = second_ripple * 0.3
            second_opacity = (1.0 - second_ripple) * 0.7

            alpha_fx.set_color(0.5, 0.8, 1.0, second_opacity)
            draw_wireframe_sphere(game_state.shield_radius * (1.0 + second_size), 12, 12)

    alpha_fx.end_effect()


def draw_ufo_enemy(damage_level=0, color=[0.5, 0.5, 0.5]):
    if not game_state.enemy_visible:
        return

    glPushMatrix()
    glScalef(game_state.enemy_size, game_state.enemy_size, game_state.enemy_size)
    r, g, b = color
    if damage_level == 0:
        glColor3f(r, g, b)
    elif damage_level < 0.5:
        glColor3f(r * 0.8, g * 0.8, b * 0.8)
    else:
        glColor3f(r * 0.6, g * 0.6, b * 0.6)

    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    draw_solid_torus(7, 20, 20, 20)
    glPopMatrix()

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

    light_count = 8 - int(damage_level * 5)
    for i in range(light_count):
        angle = i * (360.0 / light_count)
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(18, 0, -3)

        glColor3f(1.0 - r * 0.5, 1.0 - g * 0.5, 1.0 - b * 0.5)

        glutSolidSphere(3, 10, 10)
        glPopMatrix()
    if damage_level < 0.8:
        intensity = 0.9 - damage_level * 0.5
        glColor3f(1.0 - r * 0.7, 1.0 - g * 0.7, 1.0 - b * 0.7)
        glPushMatrix()
        glTranslatef(0, 0, -5)

        radius = 5.0
        height = 5.0
        slices = 10

        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, 0.0, 0.0)
        for i in range(slices + 1):
            angle = 2.0 * math.pi * i / slices
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glVertex3f(x, y, 0.0)
        glEnd()

        glBegin(GL_TRIANGLES)
        for i in range(slices):
            angle1 = 2.0 * math.pi * i / slices
            angle2 = 2.0 * math.pi * (i + 1) / slices

            x1 = radius * math.cos(angle1)
            y1 = radius * math.sin(angle1)

            x2 = radius * math.cos(angle2)
            y2 = radius * math.sin(angle2)

            glVertex3f(0.0, 0.0, -height)

            glVertex3f(x1, y1, 0.0)
            glVertex3f(x2, y2, 0.0)
        glEnd()

        glPopMatrix()

    glPopMatrix()
def draw_life_gift(gift):

    glPushMatrix()
    glTranslatef(gift['pos'][0], gift['pos'][1], gift['pos'][2])

    gift_scale = 5.0
    glScalef(gift_scale, gift_scale, gift_scale)

    rotation_speed = 90
    angle = (time.time() * rotation_speed) % 360
    glRotatef(angle, 0, 0, 1)

    pulse_factor = 0.3 * math.sin(game_state.gift_pulse) + 0.7

    glow_intensity = 0.5 * pulse_factor
    glColor3f(0.0 * glow_intensity, 1.0 * glow_intensity, 0.8 * glow_intensity)
    draw_wireframe_sphere(16, 16, 16)

    glow2_intensity = 0.2 * pulse_factor
    glColor3f(0.0 * glow2_intensity, 0.8 * glow2_intensity, 1.0 * glow2_intensity)
    draw_wireframe_sphere(20, 12, 12)

    glColor3f(1.0, 0.2, 0.5)

    glBegin(GL_QUADS)
    glVertex3f(-7, 0, 0)
    glVertex3f(-7, 0, 0)
    glVertex3f(0, -10, 0)
    glVertex3f(0, 7, 0)

    glVertex3f(7, 0, 0)
    glVertex3f(7, 0, 0)
    glVertex3f(0, -10, 0)
    glVertex3f(0, 7, 0)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(4.0)

    glBegin(GL_LINES)
    glVertex3f(0, 4, 1)
    glVertex3f(0, -4, 1)

    glVertex3f(-4, 0, 1)
    glVertex3f(4, 0, 1)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glPointSize(3.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 2)
    glEnd()

    glPopMatrix()


def draw_asteroid_trail(particles):
    for particle in particles:
        alpha = 1.0 - particle['age']

        if particle['age'] < 0.3:
            glColor3f(1.0 * alpha, 1.0 * alpha, 0.8 * alpha)
        elif particle['age'] < 0.6:
            scaled_alpha = alpha * 0.8
            glColor3f(1.0 * scaled_alpha, 0.6 * scaled_alpha, 0.0)
        else:
            scaled_alpha = alpha * 0.6
            glColor3f(0.8 * scaled_alpha, 0.2 * scaled_alpha, 0.0)

        glPointSize(particle['size'])

        if particle['age'] < 0.4:
            half_size = particle['size'] * 0.5
            glBegin(GL_QUADS)
            glVertex3f(particle['pos'][0] - half_size, particle['pos'][1] - half_size, particle['pos'][2])
            glVertex3f(particle['pos'][0] + half_size, particle['pos'][1] - half_size, particle['pos'][2])
            glVertex3f(particle['pos'][0] + half_size, particle['pos'][1] + half_size, particle['pos'][2])
            glVertex3f(particle['pos'][0] - half_size, particle['pos'][1] + half_size, particle['pos'][2])
            glEnd()
        else:
            glBegin(GL_POINTS)
            glVertex3f(particle['pos'][0], particle['pos'][1], particle['pos'][2])
            glEnd()


def draw_asteroid(size, type_id, rotation, heat_level=1.0):
    glPushMatrix()

    glRotatef(rotation[0], 1, 0, 0)
    glRotatef(rotation[1], 0, 1, 0)
    glRotatef(rotation[2], 0, 0, 1)

    if type_id == 0:
        glColor3f(1.0, 0.95, 0.8)
        glutSolidSphere(size, 12, 12)

        glColor3f(0.9, 0.6, 0.1)
        for _ in range(3):
            x = random.uniform(-0.7, 0.7) * size
            y = random.uniform(-0.7, 0.7) * size
            z = random.uniform(-0.7, 0.7) * size

            length = math.sqrt(x * x + y * y + z * z)
            if length > 0:
                x = x * size / length
                y = y * size / length
                z = z * size / length

            glPushMatrix()
            glTranslatef(x, y, z)
            glutSolidSphere(size * 0.2, 8, 8)
            glPopMatrix()

        heat_intensity = 0.8
        glColor3f(1.0 * heat_intensity, 0.8 * heat_intensity, 0.0)
        glPushMatrix()

        for i in range(5):
            scale_factor = 1.2 + (i * 0.15)
            intensity_factor = 1.0 - (i * 0.2)
            if intensity_factor > 0:
                glColor3f(1.0 * heat_intensity * intensity_factor,
                          0.7 * heat_intensity * intensity_factor,
                          0.0)
                draw_wireframe_sphere(size * scale_factor, 12 - i, 12 - i)
        glPopMatrix()

    elif type_id == 1:
        glColor3f(1.0, 0.6, 0.1)
        glScalef(1, 0.9, 0.9)
        glutSolidSphere(size, 12, 12)

        glColor3f(1.0, 0.5, 0.0)
        for _ in range(4):
            angle = random.uniform(0, 360)
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)
            glTranslatef(size * 0.8, 0, 0)

            glBegin(GL_QUADS)
            glVertex3f(0, -size * 0.2, 0)
            glVertex3f(size * 0.6, -size * 0.1, 0)
            glVertex3f(size * 0.6, size * 0.1, 0)
            glVertex3f(0, size * 0.2, 0)
            glEnd()
            glPopMatrix()

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
        glColor3f(0.9, 0.3, 0.1)

        glutSolidSphere(size, 12, 12)

        glColor3f(1.0, 0.4, 0.0)

        for i in range(3):
            angle = i * 120
            glPushMatrix()
            glRotatef(angle, 0, 0, 1)

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
    glPushMatrix()

    if is_player:
        if is_helper:
            glColor3f(0.0, 0.8, 1.0)
            glScalef(0.5, 2.0, 0.5)
        else:
            glColor3f(0.2, 0.5, 1.0)
            glScalef(0.8, 2.5, 0.8)
        glutSolidCube(3)
    else:
        r, g, b = game_state.enemy_bullet_color
        glColor3f(r, g, b)

        if game_state.enemy_shooting_style == 0:
            glutSolidCube(4)
        elif game_state.enemy_shooting_style == 1:
            glutSolidSphere(3, 10, 10)
        elif game_state.enemy_shooting_style == 2:
            glScalef(1.5, 1.5, 1.5)
            glBegin(GL_QUADS)

            glVertex3f(0, 0, 4)
            glVertex3f(-2, -2, 0)
            glVertex3f(2, -2, 0)
            glVertex3f(0, 0, 4)

            glVertex3f(0, 0, 4)
            glVertex3f(2, -2, 0)
            glVertex3f(2, 2, 0)
            glVertex3f(0, 0, 4)

            glVertex3f(0, 0, 4)
            glVertex3f(2, 2, 0)
            glVertex3f(-2, 2, 0)
            glVertex3f(0, 0, 4)

            glVertex3f(0, 0, 4)
            glVertex3f(-2, 2, 0)
            glVertex3f(-2, -2, 0)
            glVertex3f(0, 0, 4)
            glVertex3f(0, 0, -4)
            glVertex3f(-2, -2, 0)
            glVertex3f(2, -2, 0)
            glVertex3f(0, 0, -4)

            glVertex3f(0, 0, -4)
            glVertex3f(2, -2, 0)
            glVertex3f(2, 2, 0)
            glVertex3f(0, 0, -4)

            glVertex3f(0, 0, -4)
            glVertex3f(2, 2, 0)
            glVertex3f(-2, 2, 0)
            glVertex3f(0, 0, -4)

            glVertex3f(0, 0, -4)
            glVertex3f(-2, 2, 0)
            glVertex3f(-2, -2, 0)
            glVertex3f(0, 0, -4)

            glEnd()

        elif game_state.enemy_shooting_style == 3:
            glutSolidCube(5)
        else:
            glRotatef(90, 1, 0, 0)
            radius = 3
            height = 7
            slices = 12
            stacks = 4

            glBegin(GL_QUAD_STRIP)
            for i in range(slices + 1):
                angle = 2.0 * math.pi * i / slices
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                glVertex3f(x, y, height / 2)
                glVertex3f(x, y, -height / 2)
            glEnd()

            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, height / 2)
            for i in range(slices + 1):
                angle = 2.0 * math.pi * i / slices
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                glVertex3f(x, y, height / 2)
            glEnd()
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, -height / 2)
            for i in range(slices + 1):
                angle = -2.0 * math.pi * i / slices
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                glVertex3f(x, y, -height / 2)
            glEnd()

    glPopMatrix()


def draw_solid_torus(inner_radius, outer_radius, sides, rings):
    two_pi = 2.0 * math.pi

    for i in range(rings):
        ring_angle1 = i * two_pi / rings
        ring_angle2 = (i + 1) * two_pi / rings

        cos_ring1 = math.cos(ring_angle1)
        sin_ring1 = math.sin(ring_angle1)
        cos_ring2 = math.cos(ring_angle2)
        sin_ring2 = math.sin(ring_angle2)
        glBegin(GL_TRIANGLES)

        for j in range(sides):
            side_angle1 = j * two_pi / sides
            side_angle2 = (j + 1) * two_pi / sides
            cos_side1 = math.cos(side_angle1)
            sin_side1 = math.sin(side_angle1)
            cos_side2 = math.cos(side_angle2)
            sin_side2 = math.sin(side_angle2)
            x1 = (outer_radius + inner_radius * cos_side1) * cos_ring1
            y1 = (outer_radius + inner_radius * cos_side1) * sin_ring1
            z1 = inner_radius * sin_side1
            nx1 = cos_side1 * cos_ring1
            ny1 = cos_side1 * sin_ring1
            nz1 = sin_side1
            x2 = (outer_radius + inner_radius * cos_side1) * cos_ring2
            y2 = (outer_radius + inner_radius * cos_side1) * sin_ring2
            z2 = inner_radius * sin_side1
            nx2 = cos_side1 * cos_ring2
            ny2 = cos_side1 * sin_ring2
            nz2 = sin_side1
            x3 = (outer_radius + inner_radius * cos_side2) * cos_ring1
            y3 = (outer_radius + inner_radius * cos_side2) * sin_ring1
            z3 = inner_radius * sin_side2
            nx3 = cos_side2 * cos_ring1
            ny3 = cos_side2 * sin_ring1
            nz3 = sin_side2
            x4 = (outer_radius + inner_radius * cos_side2) * cos_ring2
            y4 = (outer_radius + inner_radius * cos_side2) * sin_ring2
            z4 = inner_radius * sin_side2
            nx4 = cos_side2 * cos_ring2
            ny4 = cos_side2 * sin_ring2
            nz4 = sin_side2

            glNormal3f(nx1, ny1, nz1)
            glVertex3f(x1, y1, z1)

            glNormal3f(nx2, ny2, nz2)
            glVertex3f(x2, y2, z2)

            glNormal3f(nx3, ny3, nz3)
            glVertex3f(x3, y3, z3)
            glNormal3f(nx2, ny2, nz2)
            glVertex3f(x2, y2, z2)

            glNormal3f(nx4, ny4, nz4)
            glVertex3f(x4, y4, z4)

            glNormal3f(nx3, ny3, nz3)
            glVertex3f(x3, y3, z3)

        glEnd()

def draw_explosion(size, age):
    alpha_fx.start_effect("glow", brightness=1.5)

    if age < 0.3:
        current_size = size * (age * 3.0)
    else:
        current_size = size * (1.0 - (age - 0.3) / 0.7)

    core_opacity = 1.0 - age

    alpha_fx.set_color(1.0, 0.2, 0.0, core_opacity * 0.6)
    draw_wireframe_sphere(current_size, 8, 8)

    alpha_fx.set_color(1.0, 0.5, 0.0, core_opacity * 0.8)
    draw_wireframe_sphere(current_size * 0.7, 6, 6)

    alpha_fx.set_color(1.0, 0.9, 0.6, core_opacity)
    draw_wireframe_sphere(current_size * 0.5, 4, 4)

    if size > 15:
        glBegin(GL_LINES)
        for i in range(15):
            angle = i * 24
            rad = math.radians(angle)
            length = current_size * 1.5

            x_offset = math.cos(rad) * length
            y_offset = math.sin(rad) * length
            z_offset = random.uniform(-0.5, 0.5) * length

            alpha_fx.set_color(1.0, 0.9, 0.2, core_opacity * 0.8)
            glVertex3f(0, 0, 0)

            alpha_fx.set_color(1.0, 0.3, 0.0, 0.1)
            glVertex3f(x_offset, y_offset, z_offset)
        glEnd()

    alpha_fx.end_effect()

def draw_stars_and_planets():

    glPointSize(2)
    for star in game_state.stars:

        brightness = star['brightness'] * (0.7 + 0.3 * math.sin(time.time() * star['blink_rate']))
        glColor3f(brightness, brightness, brightness)

        glBegin(GL_POINTS)
        glVertex3f(star['pos'][0], star['pos'][1], star['pos'][2])
        glEnd()

    for planet in game_state.planets:
        r, g, b = planet['color']
        glColor3f(r, g, b)

        glPushMatrix()
        glTranslatef(planet['pos'][0], planet['pos'][1], planet['pos'][2])

        glRotatef(planet['rotation'], 0, 0, 1)

        glutSolidSphere(planet['size'], 20, 20)

        if planet['rings']:
            ring_r, ring_g, ring_b = planet['ring_color']
            glColor3f(ring_r, ring_g, ring_b)
            glRotatef(75, 1, 0, 0)

            glPushMatrix()
            glutSolidTorus(planet['size'] / 10, planet['size'] * 1.8, 20, 30)
            glPopMatrix()

        glPopMatrix()


def draw_aurora_effect():

    fade_time = time.time() - game_state.aurora_time
    if fade_time < 0.3:
        opacity = fade_time / 0.3
    elif fade_time > 1.2:
        opacity = 1.0 - ((fade_time - 1.2) / 0.3)
    else:
        opacity = 1.0

    alpha_fx.start_effect("glow", brightness=1.2)

    color1 = game_state.aurora_colors[0]
    color2 = game_state.aurora_colors[1]
    for layer in range(5):
        wave_time = time.time() * (0.5 + layer * 0.1)
        layer_height = -200 + layer * 100
        layer_opacity = opacity * (0.3 + layer * 0.2)
        grid_size = 50
        glBegin(GL_QUADS)
        for i in range(-grid_size, grid_size - 2, 2):
            for j in range(-grid_size, grid_size - 4, 4):
                x1 = i * 10
                y1 = j * 10
                x2 = (i + 2) * 10
                y2 = (j + 4) * 10

                wave1_bl = 20 * math.sin(x1 / 100 + wave_time)
                wave2_bl = 15 * math.cos(y1 / 120 + wave_time * 0.7)
                z1 = layer_height + wave1_bl + wave2_bl

                wave1_br = 20 * math.sin(x2 / 100 + wave_time)
                wave2_br = 15 * math.cos(y1 / 120 + wave_time * 0.7)
                z2 = layer_height + wave1_br + wave2_br

                wave1_tr = 20 * math.sin(x2 / 100 + wave_time)
                wave2_tr = 15 * math.cos(y2 / 120 + wave_time * 0.7)
                z3 = layer_height + wave1_tr + wave2_tr

                wave1_tl = 20 * math.sin(x1 / 100 + wave_time)
                wave2_tl = 15 * math.cos(y2 / 120 + wave_time * 0.7)
                z4 = layer_height + wave1_tl + wave2_tl
                avg_x = (x1 + x2) / 2
                t = (math.sin(avg_x / 200 + wave_time) + 1) / 2
                r = color1[0] * (1 - t) + color2[0] * t
                g = color1[1] * (1 - t) + color2[1] * t
                b = color1[2] * (1 - t) + color2[2] * t
                alpha_fx.set_color(r, g, b, layer_opacity)
                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y1, z2)
                glVertex3f(x2, y2, z3)
                glVertex3f(x1, y2, z4)
        glEnd()

    alpha_fx.end_effect()


def draw_transparent_grid():
    pass

def update_asteroid_trail(asteroid, dt):

    max_particles = 15 if asteroid['size'] > 15 else 8

    if random.random() < 0.3:
        if 'heat_level' not in asteroid:
            asteroid['heat_level'] = random.uniform(0.5, 1.0)

        particle = {
            'pos': asteroid['pos'].copy(),
            'size': asteroid['size'] * 0.8 * random.uniform(0.5, 1.0),
            'age': 0.0,
            'lifetime': random.uniform(0.5, 1.5),
            'color': [0.9, 0.6, 0.2],
            'heat_level': asteroid['heat_level']
        }

        offset_range = asteroid['size'] * 0.2
        particle['pos'][0] += random.uniform(-offset_range, offset_range)
        particle['pos'][1] += random.uniform(-offset_range, offset_range)
        particle['pos'][2] += random.uniform(-offset_range, offset_range)

        asteroid['trail_particles'].append(particle)

    for particle in asteroid['trail_particles'][:]:
        particle['age'] += dt

        if particle['age'] > particle['lifetime']:
            asteroid['trail_particles'].remove(particle)
            continue
        age_ratio = particle['age'] / particle['lifetime']
        particle['size'] *= (1.0 - dt * 0.5)
        fade_factor = 1.0 - age_ratio
        particle['color'][0] = 0.9 * fade_factor
        particle['color'][1] = 0.6 * fade_factor
        particle['color'][2] = 0.2 * fade_factor

    while len(asteroid['trail_particles']) > max_particles:
        asteroid['trail_particles'].pop(0)

def initialize_asteroids(count=5):
    asteroids = []

    for _ in range(count):
        pos = [
            random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50),
            random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50),
            random.uniform(-100, -50)
        ]

        while math.sqrt(pos[0] ** 2 + pos[1] ** 2) < 200:
            pos[0] = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            pos[1] = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)

        size = random.uniform(15, 30)

        velocity = [
            random.uniform(-1.5, 1.5),
            random.uniform(-1.5, 1.5),
            random.uniform(-0.2, 0.2)
        ]

        speed = math.sqrt(velocity[0] ** 2 + velocity[1] ** 2 + velocity[2] ** 2)
        if speed < 0.5:
            factor = 0.5 / speed
            velocity = [v * factor for v in velocity]
        asteroid_type = random.randint(0, 2)

        asteroid = {
            'pos': pos,
            'size': size,
            'velocity': velocity,
            'rotation': [random.uniform(0, 360) for _ in range(3)],
            'rotation_speed': [random.uniform(-2, 2) for _ in range(3)],
            'trail_particles': [],
            'heat_level': random.uniform(0.5, 1.0),
            'type': asteroid_type
        }

        asteroids.append(asteroid)

    return asteroids

def update_enemy_movement(dt):
    current_time = time.time()
    if current_time - game_state.enemy_teleport_time > game_state.enemy_teleport_interval:
        game_state.enemy_teleport_time = current_time
        
        if game_state.enemy_visible:
            game_state.enemy_visible = False
        else:
            game_state.enemy_pos = game_state.generate_random_position(upper_area_only=True)
            game_state.enemy_direction = [random.uniform(-1, 1), random.uniform(-1, 1), 0]
            game_state.enemy_visible = True

            game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)

    if game_state.enemy_visible:
        if game_state.enemy_target_pos:
            dx = game_state.enemy_target_pos[0] - game_state.enemy_pos[0]
            dy = game_state.enemy_target_pos[1] - game_state.enemy_pos[1]
            dz = game_state.enemy_target_pos[2] - game_state.enemy_pos[2]
            
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)

            if dist < 10:
                game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)
            else:
                if dist > 0:
                    dx /= dist
                    dy /= dist
                    dz /= dist

                game_state.enemy_pos[0] += dx * game_state.enemy_speed * dt * 60
                game_state.enemy_pos[1] += dy * game_state.enemy_speed * dt * 60
                game_state.enemy_pos[2] += dz * game_state.enemy_speed * dt * 60
                bottom_boundary = -0.2 * GRID_LENGTH
                if game_state.enemy_pos[1] < bottom_boundary:
                    game_state.enemy_pos[1] = bottom_boundary
                    game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)
        else:
            game_state.enemy_target_pos = game_state.generate_random_position(upper_area_only=True)


def update_helper_aircraft(dt):
    if not game_state.helper_active:
        return

    helper_pos = [
        game_state.player_pos[0] + game_state.helper_offset[0],
        game_state.player_pos[1] + game_state.helper_offset[1],
        game_state.player_pos[2] + game_state.helper_offset[2]
    ]

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

    if closest_asteroid:
        game_state.helper_target = closest_asteroid

    current_time = time.time()
    if current_time - game_state.helper_last_shot_time > game_state.helper_shooting_interval:
        if game_state.helper_target:
            game_state.helper_last_shot_time = current_time

            dx = game_state.helper_target['pos'][0] - helper_pos[0]
            dy = game_state.helper_target['pos'][1] - helper_pos[1]
            dz = game_state.helper_target['pos'][2] - helper_pos[2]
            
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist > 0:
                dx /= dist
                dy /= dist
                dz /= dist

            game_state.player_bullets.append({
                'pos': helper_pos.copy(),
                'direction': [dx, dy, dz],
                'is_helper': True
            })


def update_life_gifts(dt):
    game_state.gift_pulse = (game_state.gift_pulse + dt * 3) % (math.pi * 2)

    for gift in game_state.life_gifts[:]:
        dx = gift['pos'][0] - game_state.player_pos[0]
        dy = gift['pos'][1] - game_state.player_pos[1]
        dz = gift['pos'][2] - game_state.player_pos[2]
        
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < 35:
            game_state.player_lives += 1
            game_state.life_gifts.remove(gift)

            game_state.player_flicker = True
            game_state.flicker_start_time = time.time()
            game_state.explosions.append({
                'pos': game_state.player_pos.copy(),
                'size': 15,
                'age': 0.0,
                'duration': 0.3
            })


def update_enemy_bullets():
    bullets_to_remove = []
    for idx, bullet in enumerate(game_state.enemy_bullets):
        prev_position = [bullet['pos'][0], bullet['pos'][1], bullet['pos'][2]]

        bullet['pos'][0] += bullet['vel'][0] * game_state.delta_time
        bullet['pos'][1] += bullet['vel'][1] * game_state.delta_time
        bullet['pos'][2] += bullet['vel'][2] * game_state.delta_time

        if (abs(bullet['pos'][0]) > GAME_AREA_SIZE or
                abs(bullet['pos'][1]) > GAME_AREA_SIZE or
                bullet['pos'][2] < -200 or bullet['pos'][2] > 200):
            bullets_to_remove.append(idx)
            continue

        if not game_state.cheat_mode:
            player_radius = 10.0
            bullet_radius = 5.0

            direction = [
                bullet['pos'][0] - prev_position[0],
                bullet['pos'][1] - prev_position[1],
                bullet['pos'][2] - prev_position[2]
            ]

            movement_length = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)

            if movement_length > 0:
                direction[0] /= movement_length
                direction[1] /= movement_length
                direction[2] /= movement_length

                to_player = [
                    game_state.player_pos[0] - prev_position[0],
                    game_state.player_pos[1] - prev_position[1],
                    game_state.player_pos[2] - prev_position[2]
                ]

                dot_product = (to_player[0] * direction[0] +
                               to_player[1] * direction[1] +
                               to_player[2] * direction[2])

                dot_product = max(0, min(dot_product, movement_length))

                closest_point = [
                    prev_position[0] + direction[0] * dot_product,
                    prev_position[1] + direction[1] * dot_product,
                    prev_position[2] + direction[2] * dot_product
                ]

                distance_squared = ((closest_point[0] - game_state.player_pos[0]) ** 2 +
                                    (closest_point[1] - game_state.player_pos[1]) ** 2 +
                                    (closest_point[2] - game_state.player_pos[2]) ** 2)

                if distance_squared < (player_radius + bullet_radius) ** 2:
                    handle_player_hit()
                    bullets_to_remove.append(idx)
                    continue

    for idx in sorted(bullets_to_remove, reverse=True):
        game_state.enemy_bullets.pop(idx)

def update_game_state():
    if game_state.game_over:
        return

    current_time = time.time()
    dt = 0.016
    if game_state.resuming:
        elapsed = current_time - game_state.countdown_start_time

        if elapsed >= game_state.resume_message_duration + 3.0:
            game_state.resuming = False

        return

    if game_state.paused:
        return

    update_enemy_movement(dt)

    if game_state.helper_active:
        update_helper_aircraft(dt)

    update_life_gifts(dt)

    for bullet in game_state.player_bullets[:]:
        bullet_speed = 6.0 if bullet.get('is_helper', False) else 8.0
        bullet['pos'][0] += bullet_speed * bullet['direction'][0]
        bullet['pos'][1] += bullet_speed * bullet['direction'][1]
        if 'direction' in bullet and len(bullet['direction']) > 2:
            bullet['pos'][2] += bullet_speed * bullet['direction'][2]

        if abs(bullet['pos'][0]) > GRID_LENGTH or abs(bullet['pos'][1]) > GRID_LENGTH:
            if not bullet.get('is_helper', False):
                game_state.player_missed_bullets += 1
                if game_state.player_missed_bullets >= 100:
                    game_state.game_over = True

            game_state.player_bullets.remove(bullet)
        for asteroid in game_state.asteroids[:]:
            if bullet in game_state.player_bullets:
                dx = bullet['pos'][0] - asteroid['pos'][0]
                dy = bullet['pos'][1] - asteroid['pos'][1]
                dz = bullet['pos'][2] - asteroid['pos'][2]

                distance = math.sqrt(dx * dx + dy * dy + dz * dz)

                if distance < asteroid['size'] + 5:
                    game_state.explosions.append({
                        'pos': [bullet['pos'][0], bullet['pos'][1], bullet['pos'][2]],
                        'size': 10,
                        'age': 0.0,
                        'duration': 0.3
                    })

                    if bullet in game_state.player_bullets:
                        game_state.player_bullets.remove(bullet)

                    asteroid['size'] -= 5
                    if asteroid['size'] < 10:
                        game_state.explosions.append({
                            'pos': asteroid['pos'].copy(),
                            'size': 15,
                            'age': 0.0,
                            'duration': 0.5
                        })

                        if len(game_state.asteroids) < 20:
                            for _ in range(2):
                                new_size = random.uniform(7, 12)

                                new_vel = [
                                    asteroid['velocity'][0] * random.uniform(0.8, 1.2),
                                    asteroid['velocity'][1] * random.uniform(0.8, 1.2),
                                    asteroid['velocity'][2] * random.uniform(0.8, 1.2)
                                ]

                                speed_factor = 1.2
                                new_vel = [v * speed_factor for v in new_vel]

                                offset = 10
                                new_pos = [
                                    asteroid['pos'][0] + random.uniform(-offset, offset),
                                    asteroid['pos'][1] + random.uniform(-offset, offset),
                                    asteroid['pos'][2] + random.uniform(-offset, offset)
                                ]

                                if random.random() < 0.1 and 'type' in asteroid:
                                    new_type = asteroid['type']
                                else:
                                    new_type = random.randint(0, 2)

                                game_state.asteroids.append({
                                    'pos': new_pos,
                                    'size': new_size,
                                    'velocity': new_vel,
                                    'rotation': [random.uniform(0, 360) for _ in range(3)],
                                    'rotation_speed': [random.uniform(-2, 2) for _ in range(3)],
                                    'trail_particles': [],
                                    'heat_level': random.uniform(0.5, 1.0),
                                    'type': new_type
                                })

                        game_state.asteroids.remove(asteroid)
                    break
    for bullet in game_state.enemy_bullets[:]:
        initial_pos = bullet['pos'].copy()

        speed = 5.0 if game_state.enemy_shooting_style < 3 else 4.0
        delta_x = speed * bullet['direction'][0]
        delta_y = speed * bullet['direction'][1]
        delta_z = speed * bullet['direction'][2]

        bullet['pos'][0] += delta_x
        bullet['pos'][1] += delta_y
        bullet['pos'][2] += delta_z

        if abs(bullet['pos'][0]) > GRID_LENGTH or abs(bullet['pos'][1]) > GRID_LENGTH:
            if bullet in game_state.enemy_bullets:
                game_state.enemy_bullets.remove(bullet)
            continue

        collision_detected = False
        player_radius = 60
        for t in range(11):
            t_fraction = t / 10.0
            check_point = [
                initial_pos[0] + t_fraction * delta_x,
                initial_pos[1] + t_fraction * delta_y,
                initial_pos[2] + t_fraction * delta_z
            ]

            dx = check_point[0] - game_state.player_pos[0]
            dy = check_point[1] - game_state.player_pos[1]
            dz = check_point[2] - game_state.player_pos[2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            if not game_state.cheat_mode and distance < player_radius:
                collision_detected = True
                game_state.player_lives -= 1

                game_state.explosions.append({
                    'pos': check_point.copy(),
                    'size': 20,
                    'age': 0.0,
                    'duration': 0.5
                })

                if game_state.player_lives <= 0:
                    game_state.game_over = True

                if bullet in game_state.enemy_bullets:
                    game_state.enemy_bullets.remove(bullet)
                break

            elif game_state.cheat_mode and distance < game_state.shield_radius:
                collision_detected = True

                game_state.last_shield_hit = time.time()

                game_state.explosions.append({
                    'pos': check_point.copy(),
                    'size': 12,
                    'age': 0.0,
                    'duration': 0.3
                })

                if bullet in game_state.enemy_bullets:
                    game_state.enemy_bullets.remove(bullet)
                break

        if collision_detected:
            continue

    if game_state.enemy_visible and random.random() < 0.03:
        angle_h = random.uniform(0, 360)
        angle_v = random.uniform(-30, 30)

        dx = math.cos(math.radians(angle_h)) * math.cos(math.radians(angle_v))
        dy = math.sin(math.radians(angle_h)) * math.cos(math.radians(angle_v))
        dz = math.sin(math.radians(angle_v))

        game_state.enemy_bullets.append({
            'pos': game_state.enemy_pos.copy(),
            'direction': [dx, dy, dz]
        })

    for bullet in game_state.player_bullets[:]:
        if not game_state.enemy_visible:
            continue

        dx = bullet['pos'][0] - game_state.enemy_pos[0]
        dy = bullet['pos'][1] - game_state.enemy_pos[1]
        dz = bullet['pos'][2] - game_state.enemy_pos[2]

        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        if distance < 35 * game_state.enemy_size:
            if bullet in game_state.player_bullets:
                game_state.player_bullets.remove(bullet)
                game_state.enemy_lives -= 1

                game_state.explosions.append({
                    'pos': [bullet['pos'][0], bullet['pos'][1], bullet['pos'][2]],
                    'size': 10,
                    'age': 0.0,
                    'duration': 0.5
                })

                if game_state.enemy_lives <= 0:
                    game_state.enemies_killed += 1

                    if game_state.enemies_killed >= 3 and not game_state.helper_active:
                        game_state.helper_active = True

                    game_state.life_gifts.append({
                        'pos': game_state.enemy_pos.copy(),
                        'age': 0.0
                    })

                    game_state.player_bullet_count += 1
                    game_state.player_shooting_speed += 0.1

                    game_state.explosions.append({
                        'pos': [game_state.enemy_pos[0], game_state.enemy_pos[1], game_state.enemy_pos[2]],
                        'size': 30,
                        'age': 0.0,
                        'duration': 1.0
                    })

                    game_state.enemy_pos = game_state.generate_random_position(upper_area_only=True)
                    game_state.enemy_max_lives = min(5, game_state.enemy_max_lives + 1)
                    game_state.enemy_lives = game_state.enemy_max_lives
                    game_state.enemy_visible = True
                    game_state.enemy_teleport_time = current_time

                    game_state.enemy_evolution = min(4, game_state.enemy_evolution + 1)
                    game_state.enemy_color = game_state.generate_enemy_color(game_state.enemy_evolution)

                    game_state.enemy_shooting_style = random.randint(0, 4)
                    game_state.enemy_bullet_color = [
                        random.uniform(0.5, 1.0),
                        random.uniform(0.2, 0.8),
                        random.uniform(0.2, 0.8)
                    ]

                    game_state.aurora_effect = True
                    game_state.aurora_time = current_time
                    game_state.aurora_colors = game_state.generate_random_aurora_colors()

    for p_bullet in game_state.player_bullets[:]:
        for e_bullet in game_state.enemy_bullets[:]:
            dx = p_bullet['pos'][0] - e_bullet['pos'][0]
            dy = p_bullet['pos'][1] - e_bullet['pos'][1]
            dz = p_bullet['pos'][2] - e_bullet['pos'][2]

            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance < 15:
                game_state.explosions.append({
                    'pos': [(p_bullet['pos'][0] + e_bullet['pos'][0]) / 2,
                            (p_bullet['pos'][1] + e_bullet['pos'][1]) / 2,
                            (p_bullet['pos'][2] + e_bullet['pos'][2]) / 2],
                    'size': 15,
                    'age': 0.0,
                    'duration': 0.7
                })

                if p_bullet in game_state.player_bullets:
                    game_state.player_bullets.remove(p_bullet)
                if e_bullet in game_state.enemy_bullets:
                    game_state.enemy_bullets.remove(e_bullet)
                break

    for asteroid in game_state.asteroids:
        asteroid['pos'][0] += asteroid['velocity'][0]
        asteroid['pos'][1] += asteroid['velocity'][1]
        asteroid['pos'][2] += asteroid['velocity'][2]

        asteroid['rotation'][0] += asteroid['rotation_speed'][0]
        asteroid['rotation'][1] += asteroid['rotation_speed'][1]
        asteroid['rotation'][2] += asteroid['rotation_speed'][2]
        for i in range(3):
            asteroid['rotation'][i] %= 360
        update_asteroid_trail(asteroid, dt)
        boundary = GRID_LENGTH - asteroid['size']
        if abs(asteroid['pos'][0]) > boundary or abs(asteroid['pos'][1]) > boundary:
            if asteroid['pos'][0] > boundary:
                asteroid['pos'][0] = -boundary + asteroid['size']
            elif asteroid['pos'][0] < -boundary:
                asteroid['pos'][0] = boundary - asteroid['size']

            if asteroid['pos'][1] > boundary:
                asteroid['pos'][1] = -boundary + asteroid['size']
            elif asteroid['pos'][1] < -boundary:
                asteroid['pos'][1] = boundary - asteroid['size']

            asteroid['trail_particles'] = []
            speed = math.sqrt(asteroid['velocity'][0] ** 2 + asteroid['velocity'][1] ** 2)
            angle_change = random.uniform(-30, 30)
            angle = math.degrees(math.atan2(asteroid['velocity'][1], asteroid['velocity'][0])) + angle_change
            asteroid['velocity'][0] = speed * math.cos(math.radians(angle))
            asteroid['velocity'][1] = speed * math.sin(math.radians(angle))
    if not game_state.cheat_mode:
        for asteroid in game_state.asteroids:
            dx = asteroid['pos'][0] - game_state.player_pos[0]
            dy = asteroid['pos'][1] - game_state.player_pos[1]
            dz = asteroid['pos'][2] - game_state.player_pos[2]

            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance < (35 + asteroid['size']):
                game_state.player_lives -= 1

                game_state.explosions.append({
                    'pos': [asteroid['pos'][0], asteroid['pos'][1], asteroid['pos'][2]],
                    'size': asteroid['size'] + 5,
                    'age': 0.0,
                    'duration': 0.7
                })
                new_pos = game_state.generate_random_position()
                asteroid['pos'] = new_pos
                asteroid['trail_particles'] = []
                if game_state.player_lives <= 0:
                    game_state.game_over = True
    else:
        for asteroid in game_state.asteroids:
            dx = asteroid['pos'][0] - game_state.player_pos[0]
            dy = asteroid['pos'][1] - game_state.player_pos[1]
            dz = asteroid['pos'][2] - game_state.player_pos[2]

            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            collision_distance = game_state.shield_radius + asteroid['size'] - 5

            if distance < collision_distance:
                game_state.last_shield_hit = time.time()
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
                if distance > 0:
                    nx = dx / distance
                    ny = dy / distance
                    nz = dz / distance
                    dot = (asteroid['velocity'][0] * nx +
                           asteroid['velocity'][1] * ny +
                           asteroid['velocity'][2] * nz)
                    bounce_factor = -1.5
                    randomness = random.uniform(0.8, 1.2)

                    asteroid['velocity'][0] += dot * nx * bounce_factor * randomness
                    asteroid['velocity'][1] += dot * ny * bounce_factor * randomness
                    asteroid['velocity'][2] += dot * nz * bounce_factor * randomness
                    push_distance = collision_distance + 5
                    asteroid['pos'][0] = game_state.player_pos[0] + nx * push_distance
                    asteroid['pos'][1] = game_state.player_pos[1] + ny * push_distance
                    asteroid['pos'][2] = game_state.player_pos[2] + nz * push_distance
    if game_state.enemy_visible and not game_state.cheat_mode:
        dx = game_state.player_pos[0] - game_state.enemy_pos[0]
        dy = game_state.player_pos[1] - game_state.enemy_pos[1]
        dz = game_state.player_pos[2] - game_state.enemy_pos[2]

        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        collision_radius = 40 + 30 * game_state.enemy_size

        if distance < collision_radius:
            game_state.player_lives -= 1
            game_state.enemy_lives -= 1
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
            direction_x = dx / distance if distance > 0 else 0
            direction_y = dy / distance if distance > 0 else 0
            game_state.player_pos[0] += direction_x * 20
            game_state.player_pos[1] += direction_y * 20
            game_state.enemy_pos = game_state.generate_random_position(upper_area_only=True)
            if game_state.player_lives <= 0:
                game_state.game_over = True

            if game_state.enemy_lives <= 0:
                game_state.enemies_killed += 1

                if game_state.enemies_killed >= 3 and not game_state.helper_active:
                    game_state.helper_active = True

                game_state.life_gifts.append({
                    'pos': collision_point.copy(),
                    'age': 0.0
                })

                game_state.player_bullet_count += 1
                game_state.player_shooting_speed += 0.1
                game_state.enemy_max_lives = min(5, game_state.enemy_max_lives + 1)
                game_state.enemy_lives = game_state.enemy_max_lives
                game_state.enemy_evolution = min(4, game_state.enemy_evolution + 1)
                game_state.enemy_color = game_state.generate_enemy_color(game_state.enemy_evolution)
                game_state.enemy_shooting_style = random.randint(0, 4)
                game_state.enemy_bullet_color = [
                    random.uniform(0.5, 1.0),
                    random.uniform(0.2, 0.8),
                    random.uniform(0.2, 0.8)
                ]
                game_state.aurora_effect = True
                game_state.aurora_time = time.time()
                game_state.aurora_colors = game_state.generate_random_aurora_colors()
    for explosion in game_state.explosions[:]:
        time_factor = 1.0 / explosion['duration'] if explosion['duration'] > 0 else 1.0
        explosion['age'] += dt * time_factor
        if explosion['age'] >= 1.0:
            game_state.explosions.remove(explosion)
    if game_state.aurora_effect:
        if current_time - game_state.aurora_time > 1.5:
            game_state.aurora_effect = False
    boundary = GRID_LENGTH - 40
    game_state.player_pos[0] = max(-boundary, min(boundary, game_state.player_pos[0]))
    game_state.player_pos[1] = max(-boundary, min(boundary, game_state.player_pos[1]))
    for star in game_state.stars:
        star['blink_rate'] = star['blink_rate'] * 0.999 + random.uniform(0.45, 2.1) * 0.001
    for planet in game_state.planets:
        planet['rotation'] += planet['rotation_speed']
        if planet['rotation'] > 360:
            planet['rotation'] -= 360

def keyboardListener(key, x, y):
    global game_state
    if key == b' ':
        if game_state.game_over:
            return
            
        if game_state.resuming:
            return
            
        if game_state.paused:
            game_state.paused = False
            game_state.resuming = True
            game_state.countdown_start_time = time.time()
        else:
            game_state.paused = True
        
        return
    if key == b'i':
        game_state.cheat_mode = not game_state.cheat_mode
        return

    if game_state.game_over:
        if key == b'r':
            game_state = GameState()
        return
    if game_state.paused or game_state.resuming:
        return

    movement_speed = 15
    if key == b'w':
        game_state.player_pos[1] += movement_speed
    if key == b's':
        game_state.player_pos[1] -= movement_speed
    if key == b'a':
        game_state.player_pos[0] -= movement_speed
    if key == b'd':
        game_state.player_pos[0] += movement_speed
    if key == b'q':
        game_state.player_pos[0] -= movement_speed * 0.7
        game_state.player_pos[1] += movement_speed * 0.7
    if key == b'e':
        game_state.player_pos[0] += movement_speed * 0.7
        game_state.player_pos[1] += movement_speed * 0.7
    if key == b'z':
        game_state.player_pos[0] -= movement_speed * 0.7
        game_state.player_pos[1] -= movement_speed * 0.7
    if key == b'c':
        game_state.player_pos[0] += movement_speed * 0.7
        game_state.player_pos[1] -= movement_speed * 0.7
    boundary = GRID_LENGTH - 40
    game_state.player_pos[0] = max(-boundary, min(boundary, game_state.player_pos[0]))
    game_state.player_pos[1] = max(-boundary, min(boundary, game_state.player_pos[1]))


def specialKeyListener(key, x, y):
    global camera_pos
    if game_state.paused or game_state.resuming:
        return

    if not game_state.first_person_mode:
        x, y, z = camera_pos
        if key == GLUT_KEY_UP:
            z = min(2000, z + 10)
        if key == GLUT_KEY_DOWN:
            z = max(20, z - 10)
        if key == GLUT_KEY_LEFT:
            x = max(-2000, x - 10)
        if key == GLUT_KEY_RIGHT:
            x = min(2000, x + 10)

        camera_pos = (x, y, z)


def mouseListener(button, state, x, y):
    if game_state.game_over or game_state.paused or game_state.resuming:
        return

    current_time = time.time()
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_time - game_state.last_shot_time > (1.0 / game_state.player_shooting_speed):
            game_state.last_shot_time = current_time
            direction = game_state.player_direction.copy()
            spread_angle = 10.0

            if game_state.player_bullet_count == 1:
                bullet_pos = game_state.player_pos.copy()
                bullet_pos[1] += 15

                game_state.player_bullets.append({
                    'pos': bullet_pos,
                    'direction': direction
                })
            else:
                start_angle = -spread_angle * (game_state.player_bullet_count - 1) / 2

                for i in range(game_state.player_bullet_count):
                    angle = start_angle + i * spread_angle
                    angle_rad = math.radians(angle)
                    bullet_dir = direction.copy()
                    bullet_dir[0] = direction[0] * math.cos(angle_rad) - direction[1] * math.sin(angle_rad)
                    bullet_dir[1] = direction[0] * math.sin(angle_rad) + direction[1] * math.cos(angle_rad)
                    length = math.sqrt(bullet_dir[0] ** 2 + bullet_dir[1] ** 2)
                    if length > 0:
                        bullet_dir[0] /= length
                        bullet_dir[1] /= length

                    bullet_pos = game_state.player_pos.copy()
                    bullet_pos[1] += 15
                    game_state.player_bullets.append({
                        'pos': bullet_pos,
                        'direction': bullet_dir
                    })
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        game_state.first_person_mode = not game_state.first_person_mode


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()

    draw_stars_and_planets()
    if game_state.aurora_effect:
        draw_aurora_effect()
    draw_transparent_grid()

    for asteroid in game_state.asteroids:
        draw_asteroid_trail(asteroid['trail_particles'])
        glPushMatrix()
        glTranslatef(asteroid['pos'][0], asteroid['pos'][1], asteroid['pos'][2])
        draw_asteroid(asteroid['size'], asteroid['type'], asteroid['rotation'], asteroid['heat_level'])
        glPopMatrix()

    damage_state = 0
    if game_state.player_lives <= 6:
        damage_state = 1
    if game_state.player_lives <= 3:
        damage_state = 2

    glPushMatrix()
    glTranslatef(game_state.player_pos[0], game_state.player_pos[1], game_state.player_pos[2])
    angle = math.degrees(math.atan2(game_state.player_direction[0], game_state.player_direction[1]))
    glRotatef(angle, 0, 0, 1)
    draw_stealth_fighter(damage_state, is_helper=False)
    if game_state.cheat_mode:
        draw_shield()

    glPopMatrix()
    if game_state.helper_active:
        helper_pos = [
            game_state.player_pos[0] + game_state.helper_offset[0],
            game_state.player_pos[1] + game_state.helper_offset[1],
            game_state.player_pos[2] + game_state.helper_offset[2]
        ]

        glPushMatrix()
        glTranslatef(helper_pos[0], helper_pos[1], helper_pos[2])
        glRotatef(angle, 0, 0, 1)
        draw_stealth_fighter(0, is_helper=True)
        glPopMatrix()
    if game_state.enemy_visible:
        damage_level = 1.0 - (game_state.enemy_lives / game_state.enemy_max_lives)
        glPushMatrix()
        glTranslatef(game_state.enemy_pos[0], game_state.enemy_pos[1], game_state.enemy_pos[2])
        glRotatef(time.time() * 30 % 360, 0, 0, 1)
        draw_ufo_enemy(damage_level, game_state.enemy_color)
        glPopMatrix()
    for gift in game_state.life_gifts:
        draw_life_gift(gift)
    for bullet in game_state.player_bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        draw_bullet(True, is_helper=bullet.get('is_helper', False))
        glPopMatrix()
    for bullet in game_state.enemy_bullets:
        glPushMatrix()
        glTranslatef(bullet['pos'][0], bullet['pos'][1], bullet['pos'][2])
        draw_bullet(False)
        glPopMatrix()
    for explosion in game_state.explosions:
        glPushMatrix()
        glTranslatef(explosion['pos'][0], explosion['pos'][1], explosion['pos'][2])
        draw_explosion(explosion['size'], explosion['age'])
        glPopMatrix()
    if game_state.paused:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(0, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        draw_centered_text_2d(game_state.pause_message, 0, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 1.0, 1.0)
        draw_centered_text_2d("Press SPACEBAR to continue", -40, GLUT_BITMAP_HELVETICA_18, 0.8, 0.8, 1.0)
    elif game_state.resuming:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(0, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        elapsed = time.time() - game_state.countdown_start_time
        if elapsed < game_state.resume_message_duration:
            draw_centered_text_2d(game_state.resume_message, 0, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 1.0, 0.3)
        else:
            countdown_elapsed = elapsed - game_state.resume_message_duration
            countdown_number = 3 - int(countdown_elapsed)

            if countdown_number >= 1:
                countdown_text = str(countdown_number)
                draw_centered_text_2d(countdown_text, 0, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 1.0, 0.0)
    if game_state.game_over:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(0, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        draw_centered_text_2d("GAME OVER", 20, GLUT_BITMAP_TIMES_ROMAN_24, 1.0, 0.2, 0.2)
        draw_centered_text_2d("Press 'R' to restart", -40, GLUT_BITMAP_HELVETICA_18, 1.0, 0.7, 0.7)
    draw_hud_text()

    glutSwapBuffers()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if game_state.first_person_mode:
        px, py, pz = game_state.player_pos
        dx, dy, dz = game_state.player_direction
        gluLookAt(px, py, pz + 10,
                  px + dx * 100, py + dy * 100, pz,
                  0, 0, 1)
    else:
        x, y, z = camera_pos
        gluLookAt(x, y, z,
                  0, 0, 0,
                  0, 0, 1)


def idle():
    update_game_state()
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Space Shooter Game")
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()