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
GRID_SIZE = 100 # This is only for adding a turbulent flow field. It does not mean the environement is discrete. 

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
        self.flow_factor = 0.2

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

        # Get the boat's position in grid coordinates
        grid_x = int(self.rect.x / GRID_SIZE)
        grid_y = int(self.rect.y / GRID_SIZE)

        # Get the flow direction at the boat's position
        flow_direction = self.flow_field.get_flow_direction(grid_x, grid_y)

        # Adjust the boat's position based on the flow direction
        self.rect.x += self.flow_factor * speed * math.cos(flow_direction)
        self.rect.y -= self.flow_factor * speed * math.sin(flow_direction)

    def draw_sensing_circle(self, screen, radius):
        # Draw a red circle around the agent
        pygame.draw.circle(screen, RED, (int(self.rect.centerx), int(self.rect.centery)), radius, 5)

    def _set_flow_field(self, flow_field):
        self.flow_field = flow_field


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

# Flow field class
class FlowField:
    def __init__(self, width, height, grid_size):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.arrow_size = (20, 20)  # Set the size of the arrow image
        self.flow_field = self.create_flow_field()
        # Load the arrow image
        self.arrow_image = pygame.image.load("assets/arrow.png")
        self.arrow_image = pygame.transform.scale(self.arrow_image, (20, 20))


    def create_flow_field(self):
        # Initialize a flow field with a general direction and slight variations in angle
        flow_field = []
        base_angle = random.uniform(0, 2 * math.pi)  # General direction

        for _ in range(self.width // self.grid_size):
            row = []
            angle_variation = random.uniform(-math.pi / 8, math.pi / 8)  # Angle variation

            for _ in range(self.height // self.grid_size):
                angle = base_angle + angle_variation
                row.append(angle)

                # Update angle for the next cell with a slight variation
                angle_variation += random.uniform(-math.pi / 16, math.pi / 16)

            flow_field.append(row)

        return flow_field


    def get_flow_direction(self, x, y):
        # Get the flow direction at a specific position
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        if 0 <= grid_x < len(self.flow_field) and 0 <= grid_y < len(self.flow_field[0]):
            return self.flow_field[grid_x][grid_y]
        return 0  # Default to no flow

    def draw_arrows(self, screen):
        # Draw arrows on the screen to visualize the flow field
        for x in range(0, self.width, self.grid_size):
            for y in range(0, self.height, self.grid_size):
                direction = self.flow_field[x // self.grid_size][y // self.grid_size]
                arrow_length = min(self.grid_size // 2, 20)
                arrow_tip = (
                    x + arrow_length * math.cos(direction),
                    y - arrow_length * math.sin(direction),
                )

                # Calculate the angle of rotation for the arrow image
                arrow_rotation = math.degrees(-direction)

                # Rotate and draw the arrow image at the arrow's position
                rotated_arrow = pygame.transform.rotate(self.arrow_image, arrow_rotation)
                screen.blit(rotated_arrow, (arrow_tip[0] - self.arrow_size[0] // 2, arrow_tip[1] - self.arrow_size[1] // 2))


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

# Set the flow field for the boat
flow_field = FlowField(WIDTH, HEIGHT, GRID_SIZE)
boat._set_flow_field(flow_field)

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

        boat.move(speed = 2)

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
        flow_field.draw_arrows(screen)
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
