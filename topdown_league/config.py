"""
config.py

This file stores constants and tunable settings for the project.

Keeping these values in one place makes the code easier to:
- read
- tweak
- debug
- expand later

As the game grows, we can continue adding values here instead of
hardcoding numbers throughout the project.
"""

# ----------------------------
# Window / screen settings
# ----------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
WINDOW_TITLE = "Top-Down League - Phase 5 Refinement"

# ----------------------------
# Arena / field settings
# ----------------------------
FIELD_MARGIN = 60
GOAL_HEIGHT = 180
GOAL_DEPTH = 85
CENTER_CIRCLE_RADIUS = 80

# ----------------------------
# Colors
# ----------------------------
BACKGROUND_COLOR = (18, 18, 24)
FIELD_COLOR = (35, 110, 70)
FIELD_LINE_COLOR = (230, 230, 230)
GOAL_COLOR_LEFT = (70, 170, 255)
GOAL_COLOR_RIGHT = (255, 120, 120)

HUD_TEXT_COLOR = (245, 245, 245)
HUD_SHADOW_COLOR = (30, 30, 30)

CAR_BODY_COLOR = (70, 170, 255)
CAR_NOSE_COLOR = (240, 240, 255)

AI_CAR_BODY_COLOR = (255, 120, 120)
AI_CAR_NOSE_COLOR = (255, 240, 240)

BALL_COLOR = (245, 210, 90)
BALL_OUTLINE_COLOR = (40, 40, 40)

BOOST_BAR_BG = (35, 35, 45)
BOOST_BAR_FILL = (80, 220, 255)
BOOST_BAR_BORDER = (230, 230, 230)

OVERLAY_COLOR = (0, 0, 0, 150)

# ----------------------------
# Car settings
# ----------------------------
CAR_WIDTH = 28
CAR_HEIGHT = 44

CAR_ACCELERATION = 0.22
CAR_REVERSE_ACCELERATION = 0.14
CAR_MAX_SPEED = 6.5
CAR_TURN_SPEED = 3.2
CAR_FRICTION = 0.96
CAR_BOOST_MULTIPLIER = 1.55
CAR_COLLISION_RADIUS = 22

# Boost resource system
BOOST_MAX = 100.0
BOOST_DRAIN_PER_FRAME = 1.1
BOOST_RECHARGE_PER_FRAME = 0.28
BOOST_MIN_TO_ACTIVATE = 1.0

# ----------------------------
# AI settings
# ----------------------------
AI_STEER_DEADZONE = 8.0
AI_REVERSE_ANGLE_THRESHOLD = 115.0
AI_BOOST_ANGLE_THRESHOLD = 16.0
AI_BOOST_DISTANCE_THRESHOLD = 170.0
AI_DEFEND_X = int(SCREEN_WIDTH * 0.78)

# Extra wall-recovery helpers
AI_WALL_X_BUFFER = 75
AI_WALL_Y_BUFFER = 70
AI_ESCAPE_TURN_FRAMES = 18

# ----------------------------
# Ball settings
# ----------------------------
BALL_RADIUS = CAR_WIDTH
BALL_START_X = SCREEN_WIDTH // 2
BALL_START_Y = SCREEN_HEIGHT // 2

BALL_FRICTION = 0.985
BALL_MAX_SPEED = 12.0
BALL_WALL_BOUNCE = 0.92
CAR_BALL_HIT_STRENGTH = 1.15
COLLISION_SEPARATION_BUFFER = 0.5

# ----------------------------
# Match settings
# ----------------------------
MATCH_TIME_SECONDS = 120
KICKOFF_COUNTDOWN_SECONDS = 3.0

# ----------------------------
# Kickoff spawn settings
# ----------------------------
PLAYER_KICKOFF_X = int(SCREEN_WIDTH * 0.25)
PLAYER_KICKOFF_Y = int(SCREEN_HEIGHT * 0.68)
PLAYER_KICKOFF_ANGLE = 45.0

AI_KICKOFF_X = int(SCREEN_WIDTH * 0.75)
AI_KICKOFF_Y = int(SCREEN_HEIGHT * 0.32)
AI_KICKOFF_ANGLE = -135.0

# ----------------------------
# Font settings
# ----------------------------
HUD_FONT_SIZE = 28
SMALL_FONT_SIZE = 20
LARGE_FONT_SIZE = 56
RESULT_FONT_SIZE = 72
COUNTDOWN_FONT_SIZE = 96

# ----------------------------
# Car visual settings
# ----------------------------
CAR_STRIPE_COLOR = (245, 245, 245)
CAR_WINDOW_COLOR = (85, 98, 112)
CAR_WHEEL_COLOR = (35, 35, 35)
CAR_WHEEL_HUB_COLOR = (100, 100, 100)
CAR_OUTLINE_COLOR = (20, 20, 20)

# ----------------------------
# Boost trail settings
# ----------------------------
BOOST_START_COLOR = (255, 150, 60)
BOOST_END_COLOR = (120, 120, 120)
BOOST_PUFF_LIFE = 16
BOOST_PUFF_RADIUS = 5
BOOST_PUFF_GROWTH = 0.45
BOOST_PUFF_SPAWN_INTERVAL = 2

# ----------------------------
# Ball visual settings
# ----------------------------
BALL_BASE_COLOR = (205, 205, 205)
BALL_PATCH_COLOR = (95, 95, 95)
BALL_HIGHLIGHT_COLOR = (245, 245, 245)
BALL_OUTLINE_COLOR = (50, 50, 50)
BALL_SPIN_SPEED = 5.0

# ----------------------------
# Audio settings
# ----------------------------
AUDIO_FREQUENCY = 44100
AUDIO_SIZE = -16
AUDIO_CHANNELS = 1
AUDIO_BUFFER = 512

MASTER_VOLUME = 0.45
ENGINE_VOLUME = 0.18
BOOST_VOLUME = 0.22
IMPACT_VOLUME = 0.32
GOAL_VOLUME = 0.40
COUNTDOWN_VOLUME = 0.35