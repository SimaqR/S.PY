import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# LOAD IMAGES

player_img = pygame.image.load("fighterjet25.png").convert_alpha()
enemy_normal_img = pygame.image.load("enemy2.png").convert_alpha()
enemy_fast_img = pygame.image.load("enemy3.png").convert_alpha()
enemy_tank_img = pygame.image.load("enemy4.png").convert_alpha()
boss_img = pygame.image.load("boss.png").convert_alpha()

# STAR IMAGE
star_img = pygame.image.load("star.png").convert_alpha()

# SCALE IMAGES

player_img = pygame.transform.scale(player_img, (64, 48))
enemy_normal_img = pygame.transform.scale(enemy_normal_img, (90, 70))
enemy_fast_img = pygame.transform.scale(enemy_fast_img, (90, 70))
enemy_tank_img = pygame.transform.scale(enemy_tank_img, (120, 90))
boss_img = pygame.transform.scale(boss_img, (220, 180))

# SCALE STAR
star_img = pygame.transform.scale(star_img, (32, 32))

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
wave_timer = 0

shoot_delay = 550
last_shot = 0
bullet_speed = 10
shake = 0

# DIFFICULTY

difficulty_settings = {
    "easy":   {"spawn_rate": 1.5, "enemy_speed": 0.8, "enemy_hp": 0.8},
    "normal": {"spawn_rate": 1.0, "enemy_speed": 1.0, "enemy_hp": 1.0},
    "hard":   {"spawn_rate": 0.7, "enemy_speed": 1.3, "enemy_hp": 1.4},
    "insane": {"spawn_rate": 0.5, "enemy_speed": 1.8, "enemy_hp": 2.0}
}

difficulty_levels = {

    "easy": [10, 25, 50],

    "normal": [20, 40, 70],

    "hard": [30, 60, 100],

    "insane": [80, 140, 200]
}

difficulty = "easy"

current_star = 0
boss_spawned = False
game_won = False

# STATE

state = "start"

# POWERUPS

particles = []

# DASH
dash_speed = 18
dash_cooldown = 1000
last_dash = 0

# SCREEN FLASH
flash_timer = 0

# BOSS WARNING
warning_timer = 0
def spawn_powerup(x, y):

    return {
        "rect": pygame.Rect(x, y, 20, 20),
        "type": random.choice(["heal", "rapid", "spread"])
    }

# DRAW DIFFICULTY STARS

def draw_difficulty(y, label, color, values, key_num):

    text = font.render(f"[{key_num}] {label}", True, color)
    screen.blit(text, (80, y))

    x = 260

    # 1 STAR
    screen.blit(star_img, (x, y - 5))

    wave1 = font.render(str(values[0]), True, (255,255,255))
    screen.blit(wave1, (x + 40, y))

    # 2 STARS
    x += 120

    screen.blit(star_img, (x, y - 5))
    screen.blit(star_img, (x + 28, y - 5))

    wave2 = font.render(str(values[1]), True, (255,255,255))
    screen.blit(wave2, (x + 75, y))

    # 3 STARS
    x += 170

    screen.blit(star_img, (x, y - 5))
    screen.blit(star_img, (x + 28, y - 5))
    screen.blit(star_img, (x + 56, y - 5))

    wave3 = font.render(str(values[2]), True, (255,255,255))
    screen.blit(wave3, (x + 105, y))

# ENEMY SPAWN

def spawn_enemy():

    y = random.randint(0, HEIGHT - 70)
    diff = difficulty_settings[difficulty]

    enemy_type = random.choice(["normal", "zigzag", "tank"])

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

    elif enemy_type == "tank":

        return {
            "rect": pygame.Rect(WIDTH, y, 120, 90),
            "speed": 3 * diff["enemy_speed"],
            "hp": int(8 * diff["enemy_hp"]),
            "type": "tank",
            "reward": 6,
            "shoot_timer": 0
        }

    return {
        "rect": pygame.Rect(WIDTH, y, 90, 70),
        "speed": 3 * diff["enemy_speed"],
        "hp": int(3 * diff["enemy_hp"]),
        "type": "normal",
        "reward": 2,
        "shoot_timer": 0
    }

# FINAL BOSS

def spawn_boss():

    return {
        "rect": pygame.Rect(WIDTH - 250, HEIGHT//2 - 90, 220, 180),
        "speed": 2,
        "hp": 300,
        "type": "boss",
        "reward": 100,
        "shoot_timer": 0
    }

# MAIN LOOP

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_b:

                if state == "Playing":
                    state = "shop"

                elif state == "shop":
                    state = "Playing"

            if event.key == pygame.K_p:

                if state == "Playing":
                    state = "pause"

                elif state == "pause":
                    state = "Playing"

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

            if state == "start":

                if event.key == pygame.K_1:
                    difficulty = "easy"

                elif event.key == pygame.K_2:
                    difficulty = "normal"

                elif event.key == pygame.K_3:
                    difficulty = "hard"

                elif event.key == pygame.K_4:
                    difficulty = "insane"

                if event.key == pygame.K_SPACE:
                    state = "Playing"

            if state == "gameover":

                if event.key == pygame.K_SPACE:

                    player.x, player.y = 50, HEIGHT // 2

                    bullets.clear()
                    enemy_bullets.clear()
                    enemies.clear()
                    powerups.clear()

                    score = 0
                    lives = 3
                    wave = 1
                    current_star = 0
                    game_won = False
                    boss_spawned = False

                    state = "start"

            if game_won:

                if event.key == pygame.K_SPACE:

                    player.x, player.y = 50, HEIGHT // 2

                    bullets.clear()
                    enemy_bullets.clear()
                    enemies.clear()
                    powerups.clear()

                    score = 0
                    lives = 3
                    wave = 1
                    current_star = 0
                    game_won = False
                    boss_spawned = False
                    difficulty = "easy"

                    state = "start"

    # SHOP

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

        title = font.render("SELECT DIFFICULTY", True, (255,255,255))
        screen.blit(title, (250,120))

        draw_difficulty(
            220,
            "EASY",
            (0,255,0),
            difficulty_levels["easy"],
            1
        )

        draw_difficulty(
            280,
            "NORMAL",
            (0,150,255),
            difficulty_levels["normal"],
            2
        )

        draw_difficulty(
            340,
            "HARD",
            (255,60,60),
            difficulty_levels["hard"],
            3
        )

        draw_difficulty(
            400,
            "INSANE",
            (180,0,255),
            difficulty_levels["insane"],
            4
        )

        selected = font.render(
            f"Selected: {difficulty.upper()}",
            True,
            (255,255,255)
        )

        screen.blit(selected, (280,470))

        start_text = font.render(
            "Press SPACE to start",
            True,
            (255,255,0)
        )

        screen.blit(start_text, (240,520))

        pygame.display.flip()

        continue

    # PAUSE

    if state == "pause":

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

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

        screen.blit(
            font.render("Press SPACE to return to menu", True, (255,255,255)),
            (220,320)
        )

        pygame.display.flip()
        continue

    # WIN SCREEN

    if game_won:

        screen.fill((0,0,0))

        win = font.render("YOU BEAT THE GAME!", True, (255,255,0))
        screen.blit(win, (230, 260))
        screen.blit(
            font.render("Press SPACE to return to menu", True, (255,255,255)),
            (210,320)
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

    if keys[pygame.K_SPACE]:

        if pygame.time.get_ticks() - last_shot > shoot_delay:

            last_shot = pygame.time.get_ticks()

            for i in range(bullet_count):

                spread_width = 40
                spread = ((i / (bullet_count - 1) - 0.5) * spread_width if bullet_count > 1 else 0)

                bullets.append([
                    player.x + player.width,
                    player.y + player.height / 2 + spread
                ])

    if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and pygame.time.get_ticks() - last_dash > dash_cooldown:

        last_dash = pygame.time.get_ticks()

        if keys[pygame.K_w]:
            player.y -= dash_speed
        if keys[pygame.K_s]:
            player.y += dash_speed
        if keys[pygame.K_a]:
            player.x -= dash_speed
        if keys[pygame.K_d]:
            player.x += dash_speed

        flash_timer = 10

    wave_timer += 1

    if wave_timer >= 600:
        wave += 1
        wave_timer = 0

    final_wave = difficulty_levels[difficulty][current_star]
    diff = difficulty_settings[difficulty]
    spawn_chance = max(10, int((40 - wave * 2) * diff["spawn_rate"]))

    if wave < final_wave:
        if random.randint(1, spawn_chance) == 1:
            enemies.append(spawn_enemy())
    elif wave >= final_wave and not boss_spawned:
        enemies.append(spawn_boss())
        boss_spawned = True

    for b in bullets[:]:
        b[0] += bullet_speed
        if b[0] > WIDTH:
            bullets.remove(b)

    for eb in enemy_bullets[:]:
        eb[0] += eb[2]
        eb[1] += eb[3]

        if player.collidepoint((eb[0], eb[1])):
            enemy_bullets.remove(eb)
            lives -= 1
            shake = 10
            continue

        if eb[0] < 0 or eb[0] > WIDTH or eb[1] < 0 or eb[1] > HEIGHT:
            enemy_bullets.remove(eb)

    for e in enemies[:]:
        dx = player.centerx - e["rect"].centerx
        dy = player.centery - e["rect"].centery
        dist = math.hypot(dx, dy)

        if dist != 0:
            dx /= dist
            dy /= dist

        e["rect"].x += dx * e["speed"] * 0.8
        e["rect"].y += dy * e["speed"] * 0.8

        e["shoot_timer"] += 1

        if e["shoot_timer"] > 90:
            e["shoot_timer"] = 0
            enemy_bullets.append([
                e["rect"].centerx,
                e["rect"].centery,
                dx * 8,
                dy * 8
            ])

        if e["type"] == "zigzag":
            e["angle"] += 0.2
            e["rect"].y += math.sin(e["angle"]) * 4

        for b in bullets[:]:
            if e["rect"].collidepoint(b):
                bullets.remove(b)
                e["hp"] -= damage
                shake = 5

                if e["hp"] <= 0:
                    if e["type"] == "boss":
                        current_star += 1
                        boss_spawned = False
                        wave = 1
                        enemies.clear()
                        enemy_bullets.clear()

                        if current_star >= 3:
                            current_star = 0
                            if difficulty == "easy":
                                difficulty = "normal"
                            elif difficulty == "normal":
                                difficulty = "hard"
                            elif difficulty == "hard":
                                difficulty = "insane"
                            elif difficulty == "insane":
                                game_won = True

                    enemies.remove(e)
                    score += 1
                    coins += e["reward"]

                    if random.random() < 0.2:
                        powerups.append(spawn_powerup(e["rect"].x, e["rect"].y))

                    break

        if player.colliderect(e["rect"]):
            enemies.remove(e)
            lives -= 1
            shake = 10

        if e["rect"].x < -100:
            enemies.remove(e)

    for p in powerups[:]:
        if player.colliderect(p["rect"]):
            if p["type"] == "heal":
                lives += 1
            elif p["type"] == "rapid":
                shoot_delay = max(100, shoot_delay - 50)
            elif p["type"] == "spread":
                bullet_count += 1
            powerups.remove(p)

    if lives <= 0:
        state = "gameover"

    offset_x = random.randint(-shake, shake)
    offset_y = random.randint(-shake, shake)
    shake = max(0, shake - 1)

    screen.fill((30,30,30))


    if flash_timer > 0:
        flash = pygame.Surface((WIDTH, HEIGHT))
        flash.fill((255,255,255))
        flash.set_alpha(80)
        screen.blit(flash, (0,0))
        flash_timer -= 1

    screen.blit(
        player_img,
        (player.x + offset_x, player.y + offset_y)
    )

    for b in bullets:
        pygame.draw.rect(
            screen,
            (255,255,0),
            (b[0] + offset_x, b[1] + offset_y, 10, 5)
        )

    for eb in enemy_bullets:
        pygame.draw.circle(
            screen,
            (255, 50, 50),
            (int(eb[0]), int(eb[1])),
            4
        )

    for e in enemies:
        dx = player.centerx - e["rect"].centerx
        dy = player.centery - e["rect"].centery
        angle = math.degrees(math.atan2(-dy, dx))

        if e["type"] == "tank":
            rotated = pygame.transform.rotate(enemy_tank_img, angle)
        elif e["type"] == "zigzag":
            rotated = pygame.transform.rotate(enemy_fast_img, angle)
        elif e["type"] == "boss":
            rotated = pygame.transform.rotate(boss_img, angle)
        else:
            rotated = pygame.transform.rotate(enemy_normal_img, angle)

        rect = rotated.get_rect(center=e["rect"].center)
        screen.blit(rotated, (rect.x + offset_x, rect.y + offset_y))

    for e in enemies:
        if e["type"] == "boss":
            pygame.draw.rect(screen, (255,0,0), (200, 20, 400, 30))
            pygame.draw.rect(screen, (0,255,0), (200, 20, 400 * max(0, e["hp"]/300), 30))
            text = font.render("FINAL BOSS", True, (255,255,255))
            screen.blit(text, (320, 25))
            break

    for p in powerups:
        color = (0,255,255) if p["type"] == "heal" else (255,0,255)
        if p["type"] == "rapid":
            color = (255,255,0)
        elif p["type"] == "spread":
            color = (0,255,0)
        pygame.draw.rect(screen, color, p["rect"])

    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,10))
    screen.blit(font.render(f"Lives: {lives}", True, (255,100,100)), (10,40))
    screen.blit(font.render(f"Wave: {wave}", True, (100,255,100)), (10,70))
    screen.blit(font.render(f"Coins: {coins}", True, (255,255,0)), (10,100))
    screen.blit(font.render(f"Difficulty: {difficulty}", True, (180,180,255)), (300,10))
    screen.blit(font.render(f"Star: {current_star + 1}/3", True, (255,255,0)), (300,40))
    screen.blit(font.render(f"Goal Wave: {final_wave}", True, (255,255,255)), (300,70))

    pygame.display.flip()
    clock.tick(60)