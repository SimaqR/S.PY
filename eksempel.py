import pygame
import random
import math
# Init
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Survival")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
# Player
class Player:
   def __init__(self):
       self.x = WIDTH // 2
       self.y = HEIGHT // 2
       self.speed = 5
       self.hp = 100
       self.radius = 15
   def move(self, keys):
       if keys[pygame.K_w]: self.y -= self.speed
       if keys[pygame.K_s]: self.y += self.speed
       if keys[pygame.K_a]: self.x -= self.speed
       if keys[pygame.K_d]: self.x += self.speed
   def draw(self):
       pygame.draw.circle(screen, (0, 255, 0), (self.x, self.y), self.radius)
# Bullet
class Bullet:
   def __init__(self, x, y, target_x, target_y):
       self.x = x
       self.y = y
       self.speed = 10
       angle = math.atan2(target_y - y, target_x - x)
       self.dx = math.cos(angle) * self.speed
       self.dy = math.sin(angle) * self.speed
       self.radius = 5
   def move(self):
       self.x += self.dx
       self.y += self.dy
   def draw(self):
       pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius)
# Enemy
class Enemy:
   def __init__(self, wave):
       self.x = random.choice([0, WIDTH])
       self.y = random.choice([0, HEIGHT])
       self.speed = random.uniform(1, 2 + wave * 0.2)
       self.hp = 2 + wave
       self.radius = 15
   def move(self, player):
       angle = math.atan2(player.y - self.y, player.x - self.x)
       self.x += math.cos(angle) * self.speed
       self.y += math.sin(angle) * self.speed
   def draw(self):
       pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.radius)
# Collision
def check_collision(obj1, obj2):
   dist = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
   return dist < obj1.radius + obj2.radius
# Game setup
player = Player()
bullets = []
enemies = []
wave = 1
spawn_timer = 0
running = True
# Game loop
while running:
   clock.tick(60)
   screen.fill((30, 30, 30))
   # Events
   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           running = False
       if event.type == pygame.MOUSEBUTTONDOWN:
           mx, my = pygame.mouse.get_pos()
           bullets.append(Bullet(player.x, player.y, mx, my))
   keys = pygame.key.get_pressed()
   player.move(keys)
   # Spawn enemies
   spawn_timer += 1
   if spawn_timer > 60:
       enemies.append(Enemy(wave))
       spawn_timer = 0
   # Update bullets
   for bullet in bullets[:]:
       bullet.move()
       if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
           bullets.remove(bullet)
   # Update enemies
   for enemy in enemies[:]:
       enemy.move(player)
       # Enemy hits player
       if check_collision(enemy, player):
           player.hp -= 1
           enemies.remove(enemy)
   # Bullet hits enemy
   for bullet in bullets[:]:
       for enemy in enemies[:]:
           if check_collision(bullet, enemy):
               enemy.hp -= 1
               if bullet in bullets:
                   bullets.remove(bullet)
               if enemy.hp <= 0:
                   enemies.remove(enemy)
               break
   # Next wave
   if len(enemies) == 0:
       wave += 1
       for i in range(wave * 2):
           enemies.append(Enemy(wave))
   # Draw
   player.draw()
   for bullet in bullets:
       bullet.draw()
   for enemy in enemies:
       enemy.draw()
   # UI
   hp_text = font.render(f"HP: {player.hp}", True, (255, 255, 255))
   wave_text = font.render(f"Wave: {wave}", True, (255, 255, 255))
   screen.blit(hp_text, (10, 10))
   screen.blit(wave_text, (10, 50))
   pygame.display.flip()
   # Game over
   if player.hp <= 0:
       running = False
pygame.quit()