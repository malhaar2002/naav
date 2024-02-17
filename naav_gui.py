import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Load background image
background = pygame.image.load("assets/background.jpg")  # Replace with your image path
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Water Body Simulation")

# Boat class
class Boat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = pygame.image.load("assets/boat.png")  # Replace with your boat sprite path
        self.original_image = pygame.transform.scale(self.original_image, (70, 70))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        self.velocity = 0
        self.max_velocity = 5
        self.mass = 5
        self.force = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.move(2)
        if keys[pygame.K_DOWN]:
            self.move(-2)
        if keys[pygame.K_LEFT]:
            self.angle -= 15 
        if keys[pygame.K_RIGHT]:
            self.angle += 15 

        # Rotate the boat image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self, speed):
        # Update the boat's position based on its angle
        self.rect.x += speed * math.cos(math.radians(self.angle))
        self.rect.y -= speed * math.sin(math.radians(self.angle))

    def draw_sensing_circle(self, screen, radius):
        # Draw a red circle around the agent
        pygame.draw.circle(screen, RED, (int(self.rect.centerx), int(self.rect.centery)), radius, 5)


# Sample class
class Sample(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("assets/sample.png")  # Replace with your obstacle sprite path
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))

# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_path):
        super().__init__()
        self.image = pygame.image.load(sprite_path)  # Replace with your obstacle sprite path
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))

# Sprite groups
all_sprites = pygame.sprite.Group()
samples = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

# Create samples
for _ in range(3):
    sample = Sample(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
    samples.add(sample)
    all_sprites.add(sample)

# Create obstacles
for i in range(1, 5):
    obstacle = Obstacle(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50), f"assets/obstacle_{i}.png")
    obstacles.add(obstacle)
    all_sprites.add(obstacle)

# Create the boat
boat = Boat(WIDTH // 2, HEIGHT // 2)
all_sprites.add(boat)

# Counters
sample_count = 0
collision_count = 0
collision_occurred = False


if __name__ == '__main__':
    # Game loop
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update()

        # Check for collisions with samples
        sample_hits = pygame.sprite.spritecollide(boat, samples, True)
        for sample in sample_hits:
            # Increment the sample counter
            sample_count += 1
            print(f"Sample collected! Total samples: {sample_count}")

        # Check for collisions with obstacles
        obstacle_hits = pygame.sprite.spritecollide(boat, obstacles, False)
        if obstacle_hits and not collision_occurred:
            # Increment the collision counter
            collision_count += 1
            print(f"Boat collided with an obstacle! Total collisions: {collision_count}")
            collision_occurred = True
        elif not obstacle_hits:
            collision_occurred = False  # Reset the collision flag

        # Draw everything
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
