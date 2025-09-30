import utils.session
import pygame
import serial
import time

# ----------------------
# CONFIG
# ----------------------
win_width, win_height = 800, 600
character_size = 50
character_speed = 5
arduino_port = 'COM3'
baud_rate = 9600
DEADZONE = 20  # Small joystick deadzone to prevent drift

# ----------------------
# INIT
# ----------------------
pygame.init()
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Joystick Game")
clock = pygame.time.Clock()

# ----------------------
# CHARACTER
# ----------------------
character_x, character_y = win_width // 2, win_height // 2
character_color = (0, 255, 0)

# ----------------------
# SERIAL
# ----------------------
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=0)  # Non-blocking
    time.sleep(2)  # Arduino reset
except serial.SerialException as e:
    print(f"Error opening serial port {arduino_port}: {e}")
    exit()

# ----------------------
# STORE LATEST JOYSTICK VALUES
# ----------------------
joy_x, joy_y, button_state = 512, 512, 1

# ----------------------
# MAIN LOOP
# ----------------------
running = True
while running:
    # --- HANDLE EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- READ SERIAL NON-BLOCKING ---
    try:
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                parts = line.split(',')
                if len(parts) == 3:
                    try:
                        joy_x, joy_y, button_state = map(int, parts)
                    except ValueError:
                        pass  # ignore invalid data
    except serial.SerialException:
        print("Lost connection to Arduino.")
        break

    # --- APPLY DEADZONE AND SCALE MOVEMENT ---
    if abs(joy_x - 512) > DEADZONE:
        move_x = ((joy_x - 512) / 512) * character_speed
    else:
        move_x = 0

    if abs(joy_y - 512) > DEADZONE:
        move_y = ((joy_y - 512) / 512) * character_speed
    else:
        move_y = 0

    # --- UPDATE CHARACTER POSITION ---
    character_x += move_x
    character_y += move_y

    # --- KEEP CHARACTER INSIDE WINDOW ---
    character_x = max(character_size // 2, min(win_width - character_size // 2, character_x))
    character_y = max(character_size // 2, min(win_height - character_size // 2, character_y))

    # --- BUTTON COLOR ---
    character_color = (0, 0, 255) if button_state == 0 else (255, 0, 0)

    # --- DRAW ---
    win.fill((255, 255, 255))
    pygame.draw.circle(win, character_color, (int(character_x), int(character_y)), character_size // 2)
    pygame.display.flip()

    # --- LIMIT FPS ---
    clock.tick(60)

# --- CLEANUP ---
ser.close()
pygame.quit()
