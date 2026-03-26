import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# PLAYER
player = pygame.Rect(50, HEIGHT // 2, 40, 40)
player_speed = 5

# GAME
bullets = []
enemy_bullets = []
enemies  = []
powerups = []

score = 0
lives = 3
wave = 1

shoot_delay = 300
last_shot = 0

triple_shot = False
bullet_speed = 8

# ENEMY TYPES
def spawn_enemy():
    y = random.randint(0, HEIGHT - 40)
    enemy_type = random.choice(["red", "blue", "orange"])

    if enemy_type == "red":
        return {"rect": pygame.Rect(WIDTH, y, 40, 40), "speed": 5, "color": (255,0,0), "type":"normal"}

    # 🔵 BLÅ ER NÅ RASKERE
    if enemy_type == "blue":
        return {"rect": pygame.Rect(WIDTH, y, 40, 40), "speed": 7, "color": (0,100,255), "type":"fast"}

    if enemy_type == "orange":
        return {"rect": pygame.Rect(WIDTH, y, 40, 40), "speed": 4, "color": (255,150,0), "type":"shooter"}


# POWER
def spawn_powerup(x, y):
    kind = random.choice(["triple", "fast", "slow"])
    return {"rect": pygame.Rect(x, y, 20, 20), "type": kind}


while True:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # PLAYER MOVEMENT (WASD)
    if keys[pygame.K_w] and player.y > 0:
        player.y -= player_speed
    if keys[pygame.K_s] and player.y < HEIGHT - 40:
        player.y += player_speed
    if keys[pygame.K_a] and player.x > 0:
        player.x -= player_speed
    if keys[pygame.K_d] and player.x < WIDTH - 40:
        player.x += player_speed

    # SHOOT
    if keys[pygame.K_SPACE]:
        if pygame.time.get_ticks() - last_shot > shoot_delay:
            last_shot = pygame.time.get_ticks()

            if triple_shot:
                bullets.append([player.x+40, player.y+5])
                bullets.append([player.x+40, player.y+15])
                bullets.append([player.x+40, player.y+25])
            else:
                bullets.append([player.x+40, player.y+15])

    # SPAWN ENEMIES
    if random.randint(1, max(5, 40 - wave*2)) == 1:
        enemies.append(spawn_enemy())

    # MOVE BULLETS
    for b in bullets[:]:
        b[0] += bullet_speed
        if b[0] > WIDTH:
            bullets.remove(b)

    # MOVE ENEMIES
    for e in enemies[:]:
        e["rect"].x -= e["speed"]

        # ORANGE SHOOT
        if e["type"] == "shooter" and random.randint(1, 100) == 1:
            enemy_bullets.append([e["rect"].x, e["rect"].y+15])

        # HIT PLAYER
        if player.colliderect(e["rect"]):
            enemies.remove(e)
            lives -= 1

        # HIT BY BULLET
        for b in bullets[:]:
            if e["rect"].collidepoint(b):
                bullets.remove(b)
                enemies.remove(e)
                score += 1

                # DROP POWERUP
                if random.randint(1,5) == 1:
                    powerups.append(spawn_powerup(e["rect"].x, e["rect"].y))
                break

        if e in enemies and e["rect"].x < 0:
            enemies.remove(e)

    # ENEMY BULLETS
    for eb in enemy_bullets[:]:
        eb[0] -= 6
        if player.collidepoint(eb):
            enemy_bullets.remove(eb)
            lives -= 1
        elif eb[0] < 0:
            enemy_bullets.remove(eb)

    # POWER
    for p in powerups[:]:
        p["rect"].x -= 3

        if player.colliderect(p["rect"]):
            if p["type"] == "triple":
                triple_shot = True
            elif p["type"] == "fast":
                shoot_delay = 150
            elif p["type"] == "slow":
                shoot_delay = 500

            powerups.remove(p)

        elif p["rect"].x < 0:
            powerups.remove(p)

    # WAVE SYSTEM
    if score > wave * 10 and wave < 10:
        wave += 1

    # DRAW
    screen.fill((30,30,30))

    pygame.draw.rect(screen, (0,255,0), player)

    for b in bullets:
        pygame.draw.rect(screen, (255,255,0), (b[0], b[1], 10,5))

    for eb in enemy_bullets:
        pygame.draw.rect(screen, (255,100,0), (eb[0], eb[1], 8,4))

    for e in enemies:
        pygame.draw.rect(screen, e["color"], e["rect"])

    for p in powerups:
        color = (255,255,0)
        if p["type"] == "fast": color = (0,255,255)
        if p["type"] == "slow": color = (255,0,255)
        pygame.draw.rect(screen, color, p["rect"])

    screen.blit(font.render(f"Score: {score}", True, (255,255,255)), (10,10))
    screen.blit(font.render(f"Lives: {lives}", True, (255,100,100)), (10,50))
    screen.blit(font.render(f"Wave: {wave}/10", True, (100,255,100)), (10,90))

    if lives <= 0:
        screen.blit(font.render("GAME OVER", True, (255,0,0)), (300,250))

    pygame.display.flip()
    clock.tick(60)