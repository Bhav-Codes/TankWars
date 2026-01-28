"""
GitWars - My Bot (Beginner-Friendly Strategy)
==============================================
CONSOLE Tank Tournament - Example Bot

This is a 'Smart Bot' that demonstrates how to use the GitWars API.
A beginner should read these comments to understand how to read the 
game state and make decisions for their tank.

RULES FOR YOUR BOT:
1. Don't modify the 'context' - it's a read-only copy!
2. You have a 100ms time limit per frame.
3. If your code crashes, your tank will freeze.
"""

import math
import random

# --- HELPER FUNCTIONS ---
# These functions handle common math tasks so the main logic stays clean.

def distance(x1, y1, x2, y2):
    """
    Calculates the straight-line distance between two points (x1, y1) and (x2, y2).
    Uses the Pythagorean theorem (A^2 + B^2 = C^2).
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def angle_to(x1, y1, x2, y2):
    """
    Calculates the angle (in degrees) from point 1 to point 2.
    Essential for aiming your barrel at a target.
    """
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def find_nearest(my_x, my_y, targets):
    """
    Searches through a list of 'targets' (like coins or enemies) and finds 
    the one closest to your current position.
    Returns: (nearest_object, distance_to_it)
    """
    nearest = None
    min_dist = float('inf') # Start with 'infinity'
    for target in targets:
        # Calculate distance to this specific target
        dist = distance(my_x, my_y, target["x"], target["y"])
        # If it's closer than the best we've seen so far, save it!
        if dist < min_dist:
            min_dist = dist
            nearest = target
    return nearest, min_dist


def is_bullet_dangerous(my_x, my_y, bullet, threshold=100):
    """
    Checks if a bullet is likely to hit you.
    A bullet is 'dangerous' if it is:
    1. Nearby (closer than 'threshold' pixels)
    2. Moving TOWARD you (not away from you)
    """
    # Check current distance
    dist = distance(my_x, my_y, bullet["x"], bullet["y"])
    if dist > threshold:
        return False # Too far away to care
    
    # Check direction: Does the bullet's velocity point toward our position?
    # We use 'dot product' math to check alignment of vectors.
    to_us_x = my_x - bullet["x"]
    to_us_y = my_y - bullet["y"]
    
    # If dot > 0, the bullet is moving toward us.
    dot = to_us_x * bullet["vx"] + to_us_y * bullet["vy"]
    return dot > 0


def update(context):
    """
    MAIN Logic: Runs every frame (60 times per second).
    You must return an action like ("MOVE", (dx, dy)) or ("SHOOT", angle).
    """
    
    # 1. EXTRACT DATA: Get info about ourselves and the world
    me = context["me"]           # Your tank's info (x, y, health, ammo)
    my_x, my_y = me["x"], me["y"] # Simplified variables for position
    my_angle = me["angle"]        # Tank's facing direction
    enemies = context["enemies"] # List of other tanks
    coins = context["coins"]     # List of coins (Round 1 only)
    bullets = context["bullets"] # List of all flying bullets
    sensors = context["sensors"] # Raycast sensors for wall detection
    game_mode = context["game_mode"] # 1: Scramble, 2: Labyrinth, 3: Duel
    
    # 2. PRIORITY 0 - OBSTACLE AVOIDANCE: Don't get stuck on walls!
    
    # EMERGENCY REVERSE: If face-planted into wall (< 10 pixels)
    if sensors["front"] < 10:
        # Full reverse! Move opposite to facing direction
        reverse_angle = math.radians(my_angle + 180)
        return ("MOVE", (math.cos(reverse_angle), math.sin(reverse_angle)))
    
    # STANDARD AVOIDANCE: Wall approaching (< 50 pixels)
    elif sensors["front"] < 50:
        # Turn toward open space
        if sensors["left"] > sensors["right"]:
            turn_angle = math.radians(my_angle - 90)  # Turn left
        else:
            turn_angle = math.radians(my_angle + 90)  # Turn right
        return ("MOVE", (math.cos(turn_angle), math.sin(turn_angle)))
    
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
                flee_strength = (300 - jug_dist) / 300
                dx = my_x - jug_x
                dy = my_y - jug_y
                mag = max((dx*dx + dy*dy)**0.5, 1)
                total_move_x += (dx / mag) * flee_strength * 2
                total_move_y += (dy / mag) * flee_strength * 2
        
        # B. Dodge Bullets (Add to movement)
        for bullet in bullets:
            if is_bullet_dangerous(my_x, my_y, bullet, 120):
                perp_angle = math.degrees(math.atan2(bullet["vy"], bullet["vx"])) + 90
                total_move_x += math.cos(math.radians(perp_angle))
                total_move_y += math.sin(math.radians(perp_angle))
        
        # C. Chase/Strafe Enemy
        target_enemy = None
        if enemies:
            target_enemy, enemy_dist = find_nearest(my_x, my_y, enemies)
            
            move_mag = (total_move_x**2 + total_move_y**2)**0.5
            if target_enemy:
                enemy_x, enemy_y = target_enemy["x"], target_enemy["y"]
                target_angle = angle_to(my_x, my_y, enemy_x, enemy_y)
                
                if move_mag < 0.5:  # Not dodging much - add combat movement
                    if enemy_dist < 80:
                        # Too close - retreat
                        retreat_angle = target_angle + 180
                        total_move_x += math.cos(math.radians(retreat_angle))
                        total_move_y += math.sin(math.radians(retreat_angle))
                    elif enemy_dist < 250:
                        # Mid range - strafe
                        strafe_angle = target_angle + 90 * (1 if random.random() > 0.5 else -1)
                        total_move_x += math.cos(math.radians(strafe_angle)) * 0.5
                        total_move_y += math.sin(math.radians(strafe_angle)) * 0.5
                    else:
                        # Far - chase
                        chase_dx = enemy_x - my_x
                        chase_dy = enemy_y - my_y
                        chase_mag = max((chase_dx**2 + chase_dy**2)**0.5, 1)
                        total_move_x += (chase_dx / chase_mag) * 0.5
                        total_move_y += (chase_dy / chase_mag) * 0.5
        
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
        
        # 2. CALCULATE SHOOTING (Aggression) - INDEPENDENT of movement
        shoot_angle = None
        if target_enemy and me["ammo"] > 0:
            aim_angle = angle_to(my_x, my_y, target_enemy["x"], target_enemy["y"])
            shoot_angle = aim_angle + random.uniform(-3, 3)  # Slight spray
        
        # 3. RETURN COMBINED ACTION
        if shoot_angle is not None:
            return ("MOVE_AND_SHOOT", ((total_move_x, total_move_y), shoot_angle))
        
        # Fallback: Just Move (ensures we are always doing something)
        return ("MOVE", (total_move_x, total_move_y))
    
    # =========================================================================
    # LEVEL 1 & 2: ORIGINAL LOGIC (Unchanged)
    # =========================================================================
    
    # Priority 1: Dodge incoming bullets (Level 1 & 2 only)
    for bullet in bullets:
        if is_bullet_dangerous(my_x, my_y, bullet, 120):
            perp_angle = math.degrees(math.atan2(bullet["vy"], bullet["vx"])) + 90
            dx = math.cos(math.radians(perp_angle))
            dy = math.sin(math.radians(perp_angle))
            return ("MOVE", (dx, dy))
    
    # MODE 1: THE SCRAMBLE (Goal: Collect Coins)
    if game_mode == 1:
        if coins:
            nearest, dist = find_nearest(my_x, my_y, coins)
            if nearest:
                for enemy in enemies:
                    enemy_dist = distance(enemy["x"], enemy["y"], nearest["x"], nearest["y"])
                    if enemy_dist < dist and distance(my_x, my_y, enemy["x"], enemy["y"]) < 200:
                        if me["ammo"] > 10:
                            angle = angle_to(my_x, my_y, enemy["x"], enemy["y"])
                            return ("SHOOT", angle)
                
                dx = nearest["x"] - my_x
                dy = nearest["y"] - my_y
                return ("MOVE", (dx, dy))
    
    # MODE 2: THE LABYRINTH - Original combat logic
    elif game_mode == 2:
        if not enemies:
            center_x, center_y = 640, 360
            dx = center_x - my_x
            dy = center_y - my_y
            return ("MOVE", (dx, dy))
        
        nearest_enemy, dist = find_nearest(my_x, my_y, enemies)
        
        if nearest_enemy:
            enemy_x = nearest_enemy["x"]
            enemy_y = nearest_enemy["y"]
            target_angle = angle_to(my_x, my_y, enemy_x, enemy_y)
            
            if dist < 80:
                if me["ammo"] > 0:
                    return ("SHOOT", target_angle)
            elif dist < 250:
                if me["ammo"] > 0:
                    aim_angle = target_angle + random.uniform(-5, 5)
                    return ("SHOOT", aim_angle)
            else:
                dx = enemy_x - my_x
                dy = enemy_y - my_y
                return ("MOVE", (dx, dy))
    
    # 4. DEFAULT: Wander randomly
    angle = random.uniform(0, 360)
    return ("MOVE", (math.cos(math.radians(angle)), math.sin(math.radians(angle))))