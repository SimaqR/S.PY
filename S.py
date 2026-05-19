import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# LOAD IMAGES
player_img = pygame.image.load("fighterjet25.png").convert_alpha()
enemy_normal_img = pygame.image.load("enemy2.png").convert_alpha()
enemy_fast_img = pygame.image.load("enemy3.png").convert_alpha()
enemy_tank_img = pygame.image.load("enemy4.png").convert_alpha()

# SCALE IMAGES

player_img = pygame.transform.scale(player_img, (64, 48))
enemy_normal_img = pygame.transform.scale(enemy_normal_img, (90, 70))
enemy_fast_img = pygame.transform.scale(enemy_fast_img, (90, 70))
enemy_tank_img = pygame.transform.scale(enemy_tank_img, (120, 90))

# PLAYER

player = pygame.Rect(50, HEIGHT // 2, 64, 48)
player_speed = 4

# STATS

damage = 1
bullet_count = 1
coins = 150

# GAME OBJECTS

bullets = []
enemy_bullets = []
enemies = []
powerups = []

score = 0
lives = 3
wave = 1

shoot_delay = 550
last_shot = 0
bullet_speed = 10
shake = 0

# DIFFICULTY

difficulty_settings = {
    "easy":   {"spawn_rate": 1.5, "enemy_speed": 0.8, "enemy_hp": 0.8},
    "normal": {"spawn_rate": 1.0, "enemy_speed": 1.0, "enemy_hp": 1.0},
    "hard":   {"spawn_rate": 0.7, "enemy_speed": 1.3, "enemy_hp": 1.4},
}

difficulty = "normal"

# STATE

state = "start"

# POWERUPS

def spawn_powerup(x, y):
    return {
        "rect": pygame.Rect(x, y, 20, 20),
        "type": random.choice(["heal", "rapid", "spread"])
    }

# ENEMY SPAWN

def spawn_enemy():

    y = random.randint(0, HEIGHT - 70)
    diff = difficulty_settings[difficulty]

    enemy_type = random.choice(["normal", "zigzag", "tank"])

    # FAST ENEMY

    if enemy_type == "zigzag":

        return {
            "rect": pygame.Rect(WIDTH, y, 90, 70),
            "speed": 6 * diff["enemy_speed"],
            "hp": int(2 * diff["enemy_hp"]),
            "type": "zigzag",
            "angle": 0,
            "reward": 3,
            "shoot_timer": 0
        }

    # TANK ENEMY

    elif enemy_type == "tank":

        return {
            "rect": pygame.Rect(WIDTH, y, 120, 90),
            "speed": 3 * diff["enemy_speed"],
            "hp": int(8 * diff["enemy_hp"]),
            "type": "tank",
            "reward": 6,
            "shoot_timer": 0
        }

    # NORMAL ENEMY

    return {
        "rect": pygame.Rect(WIDTH, y, 90, 70),
        "speed": 3 * diff["enemy_speed"],
        "hp": int(3 * diff["enemy_hp"]),
        "type": "normal",
        "reward": 2,
        "shoot_timer": 0
    }

# MAIN LOOP

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # SHOP TOGGLE

            if event.key == pygame.K_b:

                if state == "Playing":
                    state = "shop"

                elif state == "shop":
                    state = "Playing"

            # PAUSE

            if event.key == pygame.K_p:

                if state == "Playing":
                    state = "pause"

                elif state == "pause":
                    state = "Playing"
                    

            # SHOP CONTROLS

            if state == "shop":

                if event.key == pygame.K_1 and coins >= 20:

                    damage += 1
                    coins -= 20

                elif event.key == pygame.K_2 and coins >= 30:

                    shoot_delay = max(50, shoot_delay - 50)
                    coins -= 30

                elif event.key == pygame.K_3 and coins >= 25:

                    player_speed += 1
                    coins -= 25

                elif event.key == pygame.K_4 and coins >= 40:

                    bullet_count += 1
                    coins -= 40

            # START MENU

            if state == "start":

                if event.key == pygame.K_1:
                    difficulty = "easy"

                elif event.key == pygame.K_2:
                    difficulty = "normal"

                elif event.key == pygame.K_3:
                    difficulty = "hard"

                if event.key == pygame.K_SPACE:
                    state = "Playing"

            # GAME OVER

            if state == "gameover":

                if event.key == pygame.K_SPACE:

                    player.x, player.y = 50, HEIGHT // 2

                    bullets.clear()
                    enemy_bullets.clear()
                    enemies.clear()
                    powerups.clear()

                    score = 0
                    lives = 4

                    state = "start"

    # SHOP SCREEN

    if state == "shop":

        screen.fill((10, 10, 10))

        options = [
            f"[1] Damage +1 (20 coins) [{damage}]",
            f"[2] Attack Speed -50ms (30 coins) [{shoot_delay} ms]",
            f"[3] Move Speed +1 (25 coins) [{player_speed}]",
            f"[4] Multi Shot +1 (40 coins) [{bullet_count}]"
        ]

        screen.blit(font.render("SHOP (B to exit)", True, (255,255,0)), (260, 100))

        for i, text in enumerate(options):

            screen.blit(
                font.render(text, True, (255,255,255)),
                (220, 200 + i*50)
            )

        screen.blit(
            font.render(f"Coins: {coins}", True, (255,255,0)),
            (300, 400)
        )

        pygame.display.flip()
        continue

    # START SCREEN

    if state == "start":

        screen.fill((0,0,0))

        screen.blit(
            font.render("Press SPACE to start", True, (255,255,255)),
            (280,250)
        )

        screen.blit(
            font.render("1 Easy | 2 Normal | 3 Hard", True, (200,200,200)),
            (250,300)
        )

        screen.blit(
            font.render(f"Selected: {difficulty}", True, (180,180,255)),
            (300,340)
        )

        pygame.display.flip()
        continue

    # PAUSE
    if state == "pause":

       
     #overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 20))
        screen.blit(overlay, (0, 0))

        # Animated text
        t = pygame.time.get_ticks()
        bounce = int(math.sin(t * 0.005) * 10)

        pause_text = font.render("PAUSED", True, (255, 255, 255))
        hint_text = font.render("Press P to resume", True, (200, 200, 200))

        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 60 + bounce))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT//2))

        pygame.display.flip()
        continue

    # GAME OVER

    if state == "gameover":

        screen.fill((0,0,0))

        screen.blit(
            font.render("GAME OVER", True, (255,0,0)),
            (320,260)
        )

        pygame.display.flip()
        continue

    # GAMEPLAY

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player.y -= player_speed

    if keys[pygame.K_s]:
        player.y += player_speed

    if keys[pygame.K_a]:
        player.x -= player_speed

    if keys[pygame.K_d]:
        player.x += player_speed

    player.x = max(0, min(player.x, WIDTH - player.width))
    player.y = max(0, min(player.y, HEIGHT - player.height))

    # PLAYER SHOOTING

    if keys[pygame.K_SPACE]:

        if pygame.time.get_ticks() - last_shot > shoot_delay:

            last_shot = pygame.time.get_ticks()

            for i in range(bullet_count):

                spread_width = 40

                spread = (
                    (i / (bullet_count - 1) - 0.5) * spread_width
                    if bullet_count > 1 else 0
                )

                bullets.append([
                    player.x + player.width,
                    player.y + player.height / 2 + spread
                ])

    # SPAWN ENEMIES

    diff = difficulty_settings[difficulty]

    spawn_chance = max(10, int((40 - wave * 2) * diff["spawn_rate"]))

    if random.randint(1, spawn_chance) == 1:
        enemies.append(spawn_enemy())

    # PLAYER BULLETS

    for b in bullets[:]:

        b[0] += bullet_speed

        if b[0] > WIDTH:
            bullets.remove(b)

    # ENEMY BULLETS

    for eb in enemy_bullets[:]:

        eb[0] += eb[2]
        eb[1] += eb[3]

        # HIT PLAYER

        if player.collidepoint((eb[0], eb[1])):

            enemy_bullets.remove(eb)

            lives -= 1
            shake = 10

            continue

        # REMOVE OFFSCREEN

        if eb[0] < 0 or eb[0] > WIDTH or eb[1] < 0 or eb[1] > HEIGHT:

            enemy_bullets.remove(eb)

    # ENEMIES

    for e in enemies[:]:

        dx = player.centerx - e["rect"].centerx
        dy = player.centery - e["rect"].centery

        dist = math.hypot(dx, dy)

        if dist != 0:

            dx /= dist
            dy /= dist

        e["rect"].x += dx * e["speed"] * 0.8
        e["rect"].y += dy * e["speed"] * 0.8

        # ENEMY SHOOTING

        e["shoot_timer"] += 1

        if e["shoot_timer"] > 90:

            e["shoot_timer"] = 0

            enemy_bullets.append([
                e["rect"].centerx,
                e["rect"].centery,
                dx * 8,
                dy * 8
            ])

        # ZIGZAG

        if e["type"] == "zigzag":

            e["angle"] += 0.2
            e["rect"].y += math.sin(e["angle"]) * 4

        # PLAYER BULLET HIT

        for b in bullets[:]:

            if e["rect"].collidepoint(b):

                bullets.remove(b)

                e["hp"] -= damage

                shake = 5

                if e["hp"] <= 0:

                    enemies.remove(e)

                    score += 1
                    coins += e["reward"]

                    if random.random() < 0.2:

                        powerups.append(
                            spawn_powerup(e["rect"].x, e["rect"].y)
                        )

                    break

        # PLAYER COLLISION

        if player.colliderect(e["rect"]):

            enemies.remove(e)

            lives -= 1
            shake = 10

        # REMOVE OFFSCREEN

        if e["rect"].x < 0:
            enemies.remove(e)

    # POWERUPS

    for p in powerups[:]:

        if player.colliderect(p["rect"]):

            if p["type"] == "heal":
                lives += 1

            elif p["type"] == "rapid":
                shoot_delay = max(100, shoot_delay - 50)

            elif p["type"] == "spread":
                bullet_count += 1

            powerups.remove(p)

    # GAME OVER

    if lives <= 0:
        state = "gameover"

    # SCREEN SHAKE

    offset_x = random.randint(-shake, shake)
    offset_y = random.randint(-shake, shake)

    shake = max(0, shake - 1)

    # DRAW

    screen.fill((30,30,30))

    # PLAYER

    screen.blit(
        player_img,
        (player.x + offset_x, player.y + offset_y)
    )

    # PLAYER BULLETS

    for b in bullets:

        pygame.draw.rect(
            screen,
            (255,255,0),
            (b[0] + offset_x, b[1] + offset_y, 10, 5)
        )

    # ENEMY BULLETS

    for eb in enemy_bullets:

        pygame.draw.circle(
            screen,
            (255, 50, 50),
            (int(eb[0]), int(eb[1])),
            4
        )

    # ENEMIES

    for e in enemies:

        # TANK

        if e["type"] == "tank":

            flipped_img = pygame.transform.flip(enemy_tank_img, True, False)

            screen.blit(
                flipped_img,
                (e["rect"].x + offset_x, e["rect"].y + offset_y)
            )

        # FAST

        elif e["type"] == "zigzag":

            flipped_img = pygame.transform.flip(enemy_fast_img, True, False)

            screen.blit(
                flipped_img,
                (e["rect"].x + offset_x, e["rect"].y + offset_y)
            )

        # NORMAL

        else:

            flipped_img = pygame.transform.flip(enemy_normal_img, True, False)

            screen.blit(
                flipped_img,
                (e["rect"].x + offset_x, e["rect"].y + offset_y)
            )

    # POWERUPS

    for p in powerups:

        color = (0,255,255) if p["type"] == "heal" else (255,0,255)
        if p["type"] == "rapid":
            color = (255,255,0)

        elif p["type"] == "spread":
            color = (0,255,0)                   
        pygame.draw.rect(screen, color, p["rect"])

    # UI
    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,10))
    screen.blit(font.render(f"Lives: {lives}", True, (255,100,100)), (10,40))
    screen.blit(font.render(f"Wave: {wave}", True, (100,255,100)), (10,70))
    screen.blit(font.render(f"Coins: {coins}", True, (255,255,0)), (10,100))
    screen.blit(
        font.render(f"Atk Speed: {shoot_delay} ms", True, (200,200,255)),
        (500,10)
    )
    screen.blit(
        font.render(f"Move Speed: {player_speed}", True, (200,255,200)),
        (10,160)
    )
    screen.blit(
        font.render(f"Damage: {damage}", True, (255,200,200)),
        (10,190)
    )
    screen.blit(
        font.render(f"Difficulty: {difficulty}", True, (180,180,255)),
        (300,10)
    )

    pygame.display.flip()

    clock.tick(60)