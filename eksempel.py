import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival X")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# -------- PLAYER --------
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.hp = 100
        self.radius = 15
        self.weapon = "pistol"
        self.fire_rate = 3000
        self.last_shot = 0

    def move(self, keys):
        if keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_s]: self.y += self.speed
        if keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_d]: self.x += self.speed

    def shoot(self, mx, my, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.fire_rate:
            return
        self.last_shot = now

        if self.weapon == "pistol":
            bullets.append(Bullet(self.x, self.y, mx, my, 10))

        elif self.weapon == "shotgun":
            for spread in [-0.2, 0, 0.2]:
                bullets.append(Bullet(self.x, self.y, mx, my, 8, spread))

        elif self.weapon == "sniper":
            bullets.append(Bullet(self.x, self.y, mx, my, 18))

    def draw(self):
        pygame.draw.circle(screen, (0, 200, 255), (self.x, self.y), self.radius)

# -------- BULLET --------
class Bullet:
    def __init__(self, x, y, tx, ty, speed, spread=0):
        self.x = x
        self.y = y
        angle = math.atan2(ty - y, tx - x) + spread
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.radius = 4
        self.damage = 1

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius)

# -------- ENEMIES --------
class Enemy:
    def __init__(self, wave):
        self.type = random.choice(["normal", "fast", "tank"])
        self.x = random.choice([0, WIDTH])
        self.y = random.choice([0, HEIGHT])

        if self.type == "normal":
            self.speed = 1.5 + wave * 0.2
            self.hp = 2 + wave
            self.color = (255, 0, 0)

        elif self.type == "fast":
            self.speed = 3 + wave * 0.2
            self.hp = 1 + wave // 2
            self.color = (255, 165, 0)

        elif self.type == "tank":
            self.speed = 1
            self.hp = 5 + wave * 2
            self.color = (150, 0, 0)

        self.radius = 15

    def move(self, player):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# -------- COLLISION --------
def collide(a, b):
    return math.hypot(a.x - b.x, a.y - b.y) < a.radius + b.radius

# -------- MENU --------
def draw_menu():
    screen.fill((20, 20, 20))
    title = font.render("WAVE SURVIVAL X", True, (255, 255, 255))
    start = font.render("Press SPACE to Start", True, (200, 200, 200))
    screen.blit(title, (WIDTH//2 - 120, HEIGHT//2 - 40))
    screen.blit(start, (WIDTH//2 - 140, HEIGHT//2))
    pygame.display.flip()

# -------- GAME --------
def game_loop():
    player = Player()
    bullets = []
    enemies = []
    wave = 1
    spawn_timer = 0

    running = True
    while running:
        clock.tick(60)
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                player.shoot(mx, my, bullets)

        keys = pygame.key.get_pressed()
        player.move(keys)

        # weapon switch
        if keys[pygame.K_1]: player.weapon = "pistol"
        if keys[pygame.K_2]: player.weapon = "shotgun"
        if keys[pygame.K_3]: player.weapon = "sniper"

        # spawn enemies
        spawn_timer += 1
        if spawn_timer > 40:
            enemies.append(Enemy(wave))
            spawn_timer = 0

        # bullets
        for b in bullets[:]:
            b.move()
            if b.x < 0 or b.x > WIDTH or b.y < 0 or b.y > HEIGHT:
                bullets.remove(b)

        # enemies
        for e in enemies[:]:
            e.move(player)
            if collide(e, player):
                player.hp -= 5
                enemies.remove(e)

        # combat
        for b in bullets[:]:
            for e in enemies[:]:
                if collide(b, e):
                    e.hp -= b.damage
                    if b in bullets:
                        bullets.remove(b)
                    if e.hp <= 0:
                        enemies.remove(e)
                    break

        # next wave
        if len(enemies) == 0:
            wave += 1
            for _ in range(wave * 3):
                enemies.append(Enemy(wave))

        # draw
        player.draw()
        for b in bullets: b.draw()
        for e in enemies: e.draw()

        # UI
        screen.blit(font.render(f"HP: {player.hp}", True, (255,255,255)), (10,10))
        screen.blit(font.render(f"Wave: {wave}", True, (255,255,255)), (10,40))
        screen.blit(font.render(f"Weapon: {player.weapon}", True, (255,255,255)), (10,70))

        pygame.display.flip()

        if player.hp <= 0:
            running = False

# -------- MAIN LOOP --------
in_menu = True
while True:
    if in_menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                in_menu = False
                game_loop()
                in_menu = True
