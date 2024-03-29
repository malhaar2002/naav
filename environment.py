import gym
from gym import spaces
import pygame
import random
import math
import sys
from naav_gui import Sample, Obstacle, Boat

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Load background image
background = pygame.image.load("assets/background.jpg")  # Replace with your image path
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

class NaavEnvironment(gym.Env):
    def __init__(self, num_obstacles=4, num_rewards=5, max_steps=5000):
        super(NaavEnvironment, self).__init__()

        self.num_obstacles = num_obstacles
        self.num_rewards = num_rewards
        self.max_steps = max_steps
        self.collected_samples_count = 0
        self.current_step = 0
        self.visible_obstacles = []

        self.trail_points = []
        self.font = pygame.font.Font(None, 30)

        # reward policy
        self.reward_policy = {
            "obstacle": -10,
            "sample": 10,
            "step": -1,
        }

        self.action_space = spaces.Discrete(4)  # Four discrete actions: 0, 1, 2, 3
        self.observation_space = spaces.Box(low=0, high=255, shape=(HEIGHT, WIDTH, 3), dtype=int)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Naav")

        # Initialize your game objects here (similar to your Pygame code)
        self.all_sprites = pygame.sprite.Group()
        self.samples = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        self._place_obstacles(self.num_obstacles)
        self._place_samples(self.num_rewards)

        # Create the boat
        self.boat_position = (WIDTH // 2, HEIGHT // 2)
        boat = Boat(self.boat_position[0], self.boat_position[1])
        self.agent = boat
        self.all_sprites.add(boat)
        self.reset()

    def _place_samples(self, num_rewards):
        self.reward_positions = self._generate_positions(self.num_rewards)
        for i in range(num_rewards):
            sample = Sample(self.reward_positions[i][0], self.reward_positions[i][1])
            self.samples.add(sample)
            self.all_sprites.add(sample)

    def _place_obstacles(self, num_obstacles):
        self.obstacle_positions = self._generate_positions(self.num_obstacles)
        for i in range(num_obstacles):
            obstacle = Obstacle(self.obstacle_positions[i][0], self.obstacle_positions[i][1], f"assets/obstacle_{i+1}.png")
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

   
    def _generate_positions(self, num_positions):
        positions = []
        for _ in range(num_positions):
            while True:
                position = (
                    random.randint(50, WIDTH - 50),
                    random.randint(50, HEIGHT - 50),
                )
                if not self._check_collision(position, positions):
                    positions.append(position)
                    break
        return positions

    def _check_collision(self, position, existing_positions):
        for existing_position in existing_positions:
            if self._is_collision(position, existing_position):
                return True
        return False

    def _is_collision(self, position1, position2):
        x1, y1 = position1
        x2, y2 = position2
        distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return distance < 70

    def _is_valid_position(self, position):
        x, y = position
        return 0 <= x < WIDTH and 0 <= y < HEIGHT

    def _check_termination_conditions(self, reward):
        # check if all samples collected
        if self.collected_samples_count == self.num_rewards:
            done = True

        # check if out of bounds
        elif not self._is_valid_position((self.agent.rect.x, self.agent.rect.y)):
            reward = self.reward_policy["obstacle"]
            done = True

        # check if max steps reached
        elif self.current_step >= self.max_steps:
            done = True

        # Check for collisions with obstacles
        elif pygame.sprite.spritecollide(self.agent, self.obstacles, False):
            reward = self.reward_policy["obstacle"]
            done = True 
        
        else:
            done = False

        return done, reward

    def _is_within_sensing_range(self, position, sensing_range=60):
        agent_x, agent_y = self.agent.rect.x, self.agent.rect.y
        x, y = position
        distance = math.sqrt((x - agent_x)**2 + (y - agent_y)**2)
        if distance <= sensing_range:
            return position


    def step(self, action):
        """
        0 = move forwards
        1 = rotate left
        2 = rotate right
        3 = do nothing
        """
        assert self.action_space.contains(action), f"Invalid action {action}"
        self.current_step += 1
        if action == 0:
            if self.agent.velocity < self.agent.MAX_VELOCITY:
                vel_new = (self.agent.FORCE / self.agent.MASS) + self.agent.velocity
                self.agent.velocity = vel_new
            self.agent.move(self.agent.velocity)
        elif action == 1:
            self.agent.angle -= 2
        elif action == 2:
            self.agent.angle += 2
        elif action == 3:
            pass

        # Update the environment based on the given action
        self.all_sprites.update()

        # default reward
        reward = self.reward_policy["step"]
        done = False

        # Check for sample collection
        sample_hits = pygame.sprite.spritecollide(self.agent, self.samples, True)
        for _ in sample_hits:
            self.collected_samples_count += 1
            reward = self.reward_policy["sample"]

        for obstacle in self.obstacle_positions:
            if self._is_within_sensing_range(obstacle):
                self.visible_obstacles.append(obstacle)

        # Check for termination conditions
        done, reward = self._check_termination_conditions(reward)        

        # Return observation, reward, done, info
        observation = (self.agent.rect.x, self.agent.rect.y, self.agent.angle, self.agent.velocity, self.reward_positions, self.visible_obstacles)
        info = {}  # Any additional information you want to return

        return observation, reward, done, info

    def reset(self):
        # Reset the environment to its initial state
        # Return the initial observation
        self.current_step = 0
        self.collected_samples_count = 0
        self.agent.rect.x = WIDTH // 2
        self.agent.rect.y = HEIGHT // 2

        # remove previously drawn trail
        self.trail_points = []

        # change obstacle and reward positions
        self.all_sprites = pygame.sprite.Group()
        self.samples = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self._place_obstacles(self.num_obstacles)
        self._place_samples(self.num_rewards)

        self.boat_position = (WIDTH // 2, HEIGHT // 2)
        boat = Boat(self.boat_position[0], self.boat_position[1])
        self.agent = boat
        self.all_sprites.add(boat)
        self.all_sprites.update()

        observation = (self.agent.rect.x, self.agent.rect.y, self.agent.angle, self.agent.velocity, self.reward_positions, self.visible_obstacles)
        return observation


    def render(self):
        self.screen.blit(background, (0, 0))

        # Draw the trail
        self.trail_points.append((self.agent.rect.x, self.agent.rect.y))
        if len(self.trail_points) >= 2:  # Check if there are enough points to draw a line
            pygame.draw.lines(self.screen, (255, 0, 0), False, self.trail_points, 2)

        # Draw the number of samples collected at the top of the screen
        sample_text = self.font.render(f'Samples Collected: {self.collected_samples_count}', True, (255, 255, 255))
        self.screen.blit(sample_text, (10, 10))

        self.all_sprites.draw(self.screen)
        # Draw the sensing circle
        self.agent.draw_sensing_circle(self.screen, 60)
        pygame.display.flip()


    def close(self):
        # Cleanup any resources when the environment is closed
        pygame.quit()
        sys.exit()

# Your Pygame initialization and game loop code here...

# Example of a training loop
if __name__ == '__main__':
    env = NaavEnvironment()
    for episode in range(1000):
        observation = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()  # Replace with your agent's action
            observation, reward, done, info = env.step(action)

            # Your training logic goes here

            env.render()

    env.close()