import gym
from gym import spaces
import pygame
import random
import numpy as np
import sys
from naav_gui import Sample, Obstacle, DynamicObstacle, Boat, FlowField
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60
GRID_SIZE = 100 # This is only for adding a turbulent flow field. It does not mean the environement is discrete. 

# Load background image
background = pygame.image.load("assets/background.jpg")  # Replace with your image path
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

class NaavEnvironment(gym.Env):
    def __init__(self, num_obstacles=3, num_rewards=3, num_dynamic_obstacles=1, max_steps=1500):
        super(NaavEnvironment, self).__init__()

        self.num_obstacles = num_obstacles
        self.num_dynamic_obstacles = num_dynamic_obstacles
        self.num_rewards = num_rewards
        self.max_steps = max_steps
        self.collected_samples_count = 0
        self.current_step = 0
        self.visible_obstacles = [(-1, -1), (-1, -1)]

        # reward policy
        self.reward_policy = {
            "obstacle": -1000,
            "detected_obstacle": -10,
            "detected_reward": 10,
            "sample": 1000,
            "step": 0,
        }

        self.action_space = spaces.Discrete(4)  # Four discrete actions: 0, 1, 2, 3
        self.observation_space = spaces.Box(low=0, high=255, shape=(HEIGHT, WIDTH, 3), dtype=int)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Naav")

        # Initialize your game objects here (similar to your Pygame code)
        self.all_sprites = pygame.sprite.Group()
        self.samples = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.dynamic_obstacles = pygame.sprite.Group()

        self._place_obstacles(self.num_obstacles)
        self._place_dynamic_obstacles(self.num_dynamic_obstacles)
        self._place_samples(self.num_rewards)

        # Create the boat
        self.boat_position = (WIDTH // 2, HEIGHT // 2)
        boat = Boat(self.boat_position[0], self.boat_position[1])
        self.agent = boat
        self.all_sprites.add(boat)

        # initialize turblent flow field
        self.flow_field = FlowField(WIDTH, HEIGHT, GRID_SIZE)
        self.flow_field.create_flow_field()

        self.reset()

    def _place_samples(self, num_rewards):
        # self.reward_positions = self._generate_positions(self.num_rewards, self.obstacle_positions)
        self.reward_positions = [(543, 381), (360, 699), (1147, 84)]
        # print("re:", self.reward_positions)
        for i in range(num_rewards):
            sample = Sample(self.reward_positions[i][0], self.reward_positions[i][1])
            self.samples.add(sample)
            self.all_sprites.add(sample)

    def _place_obstacles(self, num_obstacles):
        # self.obstacle_positions = self._generate_positions(self.num_obstacles)
        self.obstacle_positions = [(598, 295), (961, 137), (731, 503)]
        # print("ob:", self.obstacle_positions)
        for i in range(num_obstacles):
            obstacle = Obstacle(self.obstacle_positions[i][0], self.obstacle_positions[i][1], f"assets/obstacle_{i+1}.png")
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

    def _place_dynamic_obstacles(self, num_dynamic_obstacles):
        start_x = 50
        start_y = random.randint(50, HEIGHT - 50)
        for i in range(num_dynamic_obstacles):
            dynamic_obstacle = DynamicObstacle(start_x, start_y, "assets/swimmer.png", 2, 0)
            self.dynamic_obstacles.add(dynamic_obstacle)
            self.all_sprites.add(dynamic_obstacle)

   
    def _generate_positions(self, num_positions, old_positons=[]):
        positions = []
        for _ in range(num_positions):
            while True:
                position = (
                    random.randint(50, WIDTH - 50),
                    random.randint(50, HEIGHT - 50),
                )
                if not self._check_collision(position, positions+old_positons):
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
        distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return distance < 70

    def _is_valid_position(self, position):
        x, y = position
        return 0 <= x < WIDTH and 0 <= y < HEIGHT

    def _check_termination_conditions(self, reward):
        # check if all samples collected
        if self.collected_samples_count == self.num_rewards:
            # pass in info
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

    def _is_within_sensing_range(self, position, sensing_range=150):
        agent_x, agent_y = self.agent.rect.x, self.agent.rect.y
        x, y = position
        distance = np.sqrt((x - agent_x)**2 + (y - agent_y)**2)
        if distance <= sensing_range:
            return position
        
    def _is_within_bounds(self, sensing_range=150):
        agent_x, agent_y = self.agent.rect.x, self.agent.rect.y
        if agent_x + sensing_range > WIDTH or agent_x - sensing_range < 0 or agent_y + sensing_range > HEIGHT or agent_y - sensing_range < 0:
            return False
        return True

    def step(self, action):
        """
        0 = exert force in the backward direction
        1 = exert force in the forward direction
        2 = rotate left
        3 = rotate right
        """
        assert self.action_space.contains(action), f"Invalid action {action}"
        self.current_step += 1
        self.agent.move(self.flow_field, dt, action)

        # Update the environment based on the given action
        self.all_sprites.update()

        # default reward
        reward = self.reward_policy["step"]
        done = False

        if self.visible_obstacles[0] != (-1,-1):
            # print("test:", self.visible_obstacles)
            reward = self.reward_policy["detected_obstacle"]

        if self._is_within_bounds():
            reward = self.reward_policy["detected_obstacle"]

        if self.visible_obstacles[1] != (-1,-1):
            reward = self.reward_policy["detected_reward"]

        # Check for sample collection
        sample_hits = pygame.sprite.spritecollide(self.agent, self.samples, True)
        for temp in sample_hits:
            self.collected_samples_count += 1
            self.reward_positions[self.reward_positions.index((temp.rect.centerx, temp.rect.centery))] = (-1, -1)
            # print(self.reward_positions)
            # print(temp)
            reward = self.reward_policy["sample"]

        self.visible_obstacles[0] = (-1,-1)
        for obstacle in self.obstacle_positions:
            if self._is_within_sensing_range(obstacle):
                self.visible_obstacles[0] = obstacle
        
        self.visible_obstacles[1] = (-1,-1)
        for rew in self.reward_positions:
            if self._is_within_sensing_range(rew):
                self.visible_obstacles[1] = rew

        # Check for termination conditions
        done, reward = self._check_termination_conditions(reward)        

        # Return observation, reward, done, info
        observation = (self.agent.rect.x, self.agent.rect.y, self.agent.angle, self.agent.velocity) + self.reward_positions[0] + self.reward_positions[1] + self.reward_positions[2] + self.visible_obstacles[0] + self.visible_obstacles[1]
        if done:
            info = self.collected_samples_count  # Any additional information you want to return
        else:
            info = {}

        return observation, reward, done, info

    def reset(self):
        # Reset the environment to its initial state
        # Return the initial observation
        self.current_step = 0
        self.collected_samples_count = 0
        self.agent.rect.x = WIDTH // 2
        self.agent.rect.y = HEIGHT // 2

        # change obstacle and reward positions
        self.all_sprites = pygame.sprite.Group()
        self.samples = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.dynamic_obstacles = pygame.sprite.Group()
        self._place_obstacles(self.num_obstacles)
        self._place_samples(self.num_rewards)
        self._place_dynamic_obstacles(self.num_dynamic_obstacles)

        self.flow_field.create_flow_field()
        self.flow_field.draw_arrows(self.screen)

        self.boat_position = self._generate_non_overlapping_position()
        boat = Boat(self.boat_position[0], self.boat_position[1])
        self.agent = boat
        # self.agent.angle = random.randint(0,360)
        self.all_sprites.add(boat)
        self.all_sprites.update()

        observation = (self.agent.rect.x, self.agent.rect.y, self.agent.angle, self.agent.velocity) + self.reward_positions[0] + self.reward_positions[1] + self.reward_positions[2] + self.visible_obstacles[0] + self.visible_obstacles[1]
        return observation
    
    def _generate_non_overlapping_position(self):
        while True:
            position = (
                random.randint(50, WIDTH - 50),
                random.randint(50, HEIGHT - 50),
            )
            if not self._check_collision(position, self.obstacle_positions) and not self._check_collision(position, self.reward_positions):
                return position

    def render(self):
        self.screen.blit(background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.flow_field.draw_arrows(self.screen)
        # Draw the sensing circle
        self.agent.draw_sensing_circle(self.screen, 150)
        pygame.display.flip()


    def close(self):
        # Cleanup any resources when the environment is closed
        pygame.quit()
        sys.exit()

# Your Pygame initialization and game loop code here...

# Example of a training loop
if __name__ == '__main__':
    env = NaavEnvironment()
    clock = pygame.time.Clock()  # Initialize the clock
    for episode in range(100):
        observation = env.reset()
        done = False
        while not done:
            # action = env.action_space.sample()  # Replace with your agent's action
            action = 1
            
            # Update the clock
            dt = clock.tick(FPS) / 1000  # Convert milliseconds to seconds

            observation, reward, done, info = env.step(action)

            # Your training logic goes here

            env.render()

    env.close()
