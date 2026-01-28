"""
GitWars - Bot Template
======================
CONSOLE Tank Tournament

This is your STARTER CODE! Edit this file to control your tank.
Read the comments carefully to understand the API.

Your tank will call your update() function every frame.
You must return an action tuple: (ACTION, PARAMETER)

ACTIONS:
--------
("MOVE", (dx, dy))   - Move in direction (dx, dy). Values are normalized.
                       Example: ("MOVE", (1, 0)) = move right
                       Example: ("MOVE", (0, -1)) = move up
                       Example: ("MOVE", (-1, 1)) = move down-left

("SHOOT", angle)     - Fire a bullet at the given angle (in degrees).
                       Example: ("SHOOT", 0) = shoot right
                       Example: ("SHOOT", 90) = shoot down
                       Example: ("SHOOT", 180) = shoot left

("STOP", None)       - Stop moving, stay in place.

CONTEXT DICTIONARY:
-------------------
The engine passes you a `context` dictionary every frame with this structure:

context = {
    "me": {
        "x": float,      # Your tank's X position
        "y": float,      # Your tank's Y position  
        "angle": float,  # Your tank's facing angle (degrees)
        "health": int,   # Your current health (0-100)
        "ammo": int,     # Your remaining bullets
        "coins": int     # Coins collected (Mode 1 only)
    },
    "enemies": [
        {"x": float, "y": float, "id": int},  # List of enemy positions
        ...
    ],
    "coins": [
        {"x": float, "y": float},  # List of coin positions (Mode 1 only)
        ...
    ],
    "walls": [
        {"x": float, "y": float, "width": float, "height": float},  # Walls
        ...
    ],
    "bullets": [
        {"x": float, "y": float, "vx": float, "vy": float},  # Enemy bullets
        ...
    ],
    "sensors": {
        "front": float,  # Distance to wall ahead (max 300 pixels)
        "left": float,   # Distance to wall at -30 degrees
        "right": float   # Distance to wall at +30 degrees
    },
    "game_mode": int,     # 1=Scramble, 2=Labyrinth, 3=Duel
    "time_left": float    # Time remaining in seconds
}

SENSORS (Obstacle Avoidance):
-----------------------------
The 'sensors' key contains raycast distances to walls in 3 directions:
- "front": Distance to wall straight ahead (0 degrees from facing)
- "left":  Distance to wall at -30 degrees (left whisker)
- "right": Distance to wall at +30 degrees (right whisker)

Max range is 300 pixels. If no wall is detected, the value is 300.

Example Usage:
    sensors = context["sensors"]
    if sensors["front"] < 50:  # Wall is close ahead!
        if sensors["left"] > sensors["right"]:
            # More space on left - turn left
            return ("MOVE", (-1, 0))
        else:
            # More space on right - turn right
            return ("MOVE", (1, 0))

TIPS:
-----
1. Don't try to modify the context - it's a read-only copy!
2. Your update() function has a 100ms time limit - keep it fast!
3. If your code crashes, your tank will freeze but the game continues.
4. Use math.atan2(dy, dx) to calculate angles to targets.
5. In Mode 1 (Scramble), bullets only knock back - they don't damage!
6. Use sensors["front"] < 50 to detect walls ahead and avoid them!

HELPER FUNCTIONS:
-----------------
Below are some useful helper functions you can use or modify.
"""

import math
import random


def distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def angle_to(x1, y1, x2, y2):
    """Calculate angle from point (x1, y1) to point (x2, y2) in degrees."""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def find_nearest(my_x, my_y, targets):
    """
    Find the nearest target from a list of targets.
    Each target must have 'x' and 'y' keys.
    Returns (target, distance) or (None, float('inf')) if list is empty.
    """
    nearest = None
    min_dist = float('inf')
    
    for target in targets:
        dist = distance(my_x, my_y, target["x"], target["y"])
        if dist < min_dist:
            min_dist = dist
            nearest = target
    
    return nearest, min_dist


def will_bullet_hit_me(my_x, my_y, bullet, danger_radius=50):
    """
    Predict if a bullet will come close to your position.
    Returns True if bullet is dangerous.
    """
    # Future position of bullet
    future_x = bullet["x"] + bullet["vx"] * 10
    future_y = bullet["y"] + bullet["vy"] * 10
    
    # Check if bullet path intersects with our position
    dist_now = distance(my_x, my_y, bullet["x"], bullet["y"])
    dist_future = distance(my_x, my_y, future_x, future_y)
    
    # Bullet is approaching if it gets closer
    return dist_future < dist_now and dist_now < danger_radius * 2


# =============================================================================
# YOUR CODE STARTS HERE!
# =============================================================================

def update(context):
    """
    This function is called every frame.
    
    Args:
        context: Dictionary containing game state (see above for structure)
    
    Returns:
        (ACTION, PARAMETER) tuple - your tank's action for this frame
    """
    
    # Get my tank's info
    me = context["me"]
    my_x = me["x"]
    my_y = me["y"]
    
    enemies = context["enemies"]
    coins = context["coins"]
    bullets = context["bullets"]
    game_mode = context["game_mode"]
    
    # =========================================================================
    # EXAMPLE STRATEGY: This is a basic bot, modify it!
    # =========================================================================
    
    # PRIORITY 0: OBSTACLE AVOIDANCE REFLEX (Prevents getting stuck!)
    sensors = context["sensors"]
    my_angle = me["angle"]
    
    # EMERGENCY REVERSE: If face-planted into wall (< 10 pixels)
    if sensors["front"] < 10:
        # Full reverse! Move opposite to facing direction
        reverse_angle = math.radians(my_angle + 180)
        return ("MOVE", (math.cos(reverse_angle), math.sin(reverse_angle)))
    
    # STANDARD AVOIDANCE: Wall approaching (< 50 pixels)
    elif sensors["front"] < 50:
        # Turn toward open space
        if sensors["left"] > sensors["right"]:
            # More space on left - turn left (perpendicular to facing)
            turn_angle = math.radians(my_angle - 90)
        else:
            # More space on right - turn right
            turn_angle = math.radians(my_angle + 90)
        dx = math.cos(turn_angle)
        dy = math.sin(turn_angle)
        return ("MOVE", (dx, dy))
    
    elif sensors["left"] < 30:
        # Wall on left - nudge right
        turn_angle = math.radians(my_angle + 45)
        return ("MOVE", (math.cos(turn_angle), math.sin(turn_angle)))
    
    elif sensors["right"] < 30:
        # Wall on right - nudge left
        turn_angle = math.radians(my_angle - 45)
        return ("MOVE", (math.cos(turn_angle), math.sin(turn_angle)))
    
    # =========================================================================
    # LEVEL 3: ACCUMULATIVE LOGIC (Move + Shoot independently)
    # =========================================================================
    if game_mode == 3:
        # 1. CALCULATE MOVEMENT (Survival) - Accumulate vectors
        total_move_x, total_move_y = 0.0, 0.0
        
        # A. Dodge Juggernaut (Critical - High weight)
        juggernaut = context.get("juggernaut")
        if juggernaut:
            jug_x, jug_y = juggernaut["x"], juggernaut["y"]
            jug_dist = distance(my_x, my_y, jug_x, jug_y)
            
            if jug_dist < 300:  # Fear radius
                # Vector AWAY from Juggernaut (weighted by proximity)
                flee_strength = (300 - jug_dist) / 300  # 1.0 at 0 dist, 0.0 at 300
                dx = my_x - jug_x
                dy = my_y - jug_y
                mag = max((dx*dx + dy*dy)**0.5, 1)
                total_move_x += (dx / mag) * flee_strength * 2  # High priority
                total_move_y += (dy / mag) * flee_strength * 2
        
        # B. Dodge Bullets (Add to movement)
        for bullet in bullets:
            if will_bullet_hit_me(my_x, my_y, bullet):
                # Perpendicular dodge
                dodge_angle = math.degrees(math.atan2(bullet["vy"], bullet["vx"])) + 90
                total_move_x += math.cos(math.radians(dodge_angle))
                total_move_y += math.sin(math.radians(dodge_angle))
        
        # C. Chase Enemy or Wander
        target_enemy = None
        if enemies:
            target_enemy, enemy_dist = find_nearest(my_x, my_y, enemies)
            
            # Only add chase vector if not in danger/dodging hard
            move_mag = (total_move_x**2 + total_move_y**2)**0.5
            if target_enemy and move_mag < 0.5:
                chase_dx = target_enemy["x"] - my_x
                chase_dy = target_enemy["y"] - my_y
                chase_mag = max((chase_dx**2 + chase_dy**2)**0.5, 1)
                
                # Orbit/Strafe logic: Don't run straight at them, keep distance
                desired_dist = 200
                if enemy_dist > desired_dist:
                    # Chase
                    total_move_x += (chase_dx / chase_mag) * 0.6
                    total_move_y += (chase_dy / chase_mag) * 0.6
                else:
                    # Strafe (perpendicular)
                    total_move_x += -(chase_dy / chase_mag) * 0.6
                    total_move_y += (chase_dx / chase_mag) * 0.6
        
        # D. Wander if idle (prevents freezing)
        move_mag = (total_move_x**2 + total_move_y**2)**0.5
        if move_mag < 0.1:
            # Move towards center-ish but stay away from exact center
            center_angle = math.atan2(300 - my_y, 400 - my_x)
            total_move_x += math.cos(center_angle + context.get("time_left", 0)) * 0.5
            total_move_y += math.sin(center_angle + context.get("time_left", 0)) * 0.5

        # Normalize movement vector
        move_mag = (total_move_x**2 + total_move_y**2)**0.5
        if move_mag > 0:
            total_move_x /= move_mag
            total_move_y /= move_mag
        
        # 2. CALCULATE SHOOTING (Aggression)
        shoot_angle = None
        if target_enemy and me["ammo"] > 0:
            shoot_angle = angle_to(my_x, my_y, target_enemy["x"], target_enemy["y"])
            shoot_angle += random.uniform(-5, 5) # Slight spread
        
        # 3. RETURN COMBINED ACTION
        if shoot_angle is not None:
            # Move AND shoot simultaneously
            return ("MOVE_AND_SHOOT", ((total_move_x, total_move_y), shoot_angle))
        
        # Fallback: Just Move
        return ("MOVE", (total_move_x, total_move_y))
    
    # =========================================================================
    # LEVEL 1 & 2: ORIGINAL LOGIC (Unchanged)
    # =========================================================================
    
    # Priority 1: Dodge incoming bullets (standard MOVE - Level 1 & 2 only)
    if game_mode != 3:
        for bullet in bullets:
            if will_bullet_hit_me(my_x, my_y, bullet):
                dodge_angle = math.degrees(math.atan2(bullet["vy"], bullet["vx"])) + 90
                dx = math.cos(math.radians(dodge_angle))
                dy = math.sin(math.radians(dodge_angle))
                return ("MOVE", (dx, dy))
    
    # Game Mode specific behavior
    if game_mode == 1:  # THE SCRAMBLE - Collect coins!
        if coins:
            nearest_coin, dist = find_nearest(my_x, my_y, coins)
            if nearest_coin:
                dx = nearest_coin["x"] - my_x
                dy = nearest_coin["y"] - my_y
                return ("MOVE", (dx, dy))
    
    elif game_mode == 2:  # THE LABYRINTH - Original combat logic
        if enemies and me["ammo"] > 0:
            nearest_enemy, dist = find_nearest(my_x, my_y, enemies)
            if nearest_enemy:
                if dist < 200:
                    target_angle = angle_to(my_x, my_y, nearest_enemy["x"], nearest_enemy["y"])
                    return ("SHOOT", target_angle)
                else:
                    dx = nearest_enemy["x"] - my_x
                    dy = nearest_enemy["y"] - my_y
                    return ("MOVE", (dx, dy))
    
    # Default: Wander around
    angle = random.uniform(0, 360)
    dx = math.cos(math.radians(angle))
    dy = math.sin(math.radians(angle))
    return ("MOVE", (dx, dy))