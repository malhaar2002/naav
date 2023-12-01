import numpy as np
import gym
from gym import spaces
import pygame

class CustomGridWorldEnv(gym.Env):
    def __init__(self, grid_size=5, num_obstacles=5, num_rewards=5, max_steps=50):
        super(CustomGridWorldEnv, self).__init__()

        self.grid_size = grid_size
        self.num_obstacles = num_obstacles
        self.num_rewards = num_rewards
        self.max_steps = max_steps
        self.nrows = grid_size
        self.ncols = grid_size

        # reward policy
        self.reward_policy = {
            "obstacle": -1,
            "sample": 3,
            "step": 0,
        }

        # Action space: Discrete space with 4 actions (up, down, left, right)
        self.action_space = spaces.Discrete(4)

        # Observation space: Discrete space representing the grid cells
        self.observation_space = spaces.Discrete(grid_size * grid_size)

        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int8)
        self.agent_position = (0, 0)  # Agent starts at the top-left corner

        self.obstacle_positions = self._generate_positions(self.num_obstacles)
        self.reward_positions = self._generate_positions(self.num_rewards)

        self.current_step = 0
        self.total_reward = 0

    def _generate_positions(self, num_positions):
        positions = []
        for _ in range(num_positions):
            while True:
                position = (
                    np.random.randint(self.grid_size),
                    np.random.randint(self.grid_size),
                )
                if position not in positions:
                    positions.append(position)
                    break
        return positions

    def _is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def _update_grid(self):
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int8)
        for position in self.obstacle_positions:
            self.grid[position] = self.reward_policy["obstacle"]  # Mark obstacles with -1
        for position in self.reward_positions:
            self.grid[position] = self.reward_policy["sample"]  # Mark rewards with 1
        self.grid[self.agent_position] = 2  # Mark the agent with 2

    def step(self, action):
        assert self.action_space.contains(action), "Invalid action"

        self.current_step += 1

        # Define action effects (movement)
        if action == 0:  # Up
            new_position = (self.agent_position[0] - 1, self.agent_position[1])
        elif action == 1:  # Down
            new_position = (self.agent_position[0] + 1, self.agent_position[1])
        elif action == 2:  # Left
            new_position = (self.agent_position[0], self.agent_position[1] - 1)
        else:  # Right
            new_position = (self.agent_position[0], self.agent_position[1] + 1)

        if self._is_valid_position(new_position):
            # Calculate reward
            reward = self.grid[new_position]
            # Update agent position
            self.agent_position = new_position
        else:
            reward = -1  # Penalty for out-of-bounds move

        self._update_grid()

        # Update total reward
        self.total_reward += reward

        # Calculate the observation as current_row * nrows + current_col
        current_row, current_col = self.agent_position
        observation = current_row * self.nrows + current_col

        # Termination conditions
        done = self.current_step >= self.max_steps or len(self.reward_positions) == 0

        # Remove collected rewards
        if reward == self.reward_policy["sample"]:
            self.reward_positions.remove(self.agent_position)

        return observation, reward, done

    def reset(self):
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int8)
        self.agent_position = (0, 0)
        self.obstacle_positions = self._generate_positions(self.num_obstacles)
        self.reward_positions = self._generate_positions(self.num_rewards)
        self.current_step = 0
        self.total_reward = 0

        self._update_grid()

        # Calculate the initial observation as current_row * nrows + current_col
        current_row, current_col = self.agent_position
        observation = current_row * self.nrows + current_col

        return observation

    def render(self, mode="CLI"):
        if mode == "CLI":
            for row in self.grid:
                print(" ".join(map(self._render_symbol, row)))
            print("\n")
        elif mode == "GUI":
            self._render_gui()
        else:
            assert False, "Invalid rendering mode"

    
    def _render_gui(self):
        pygame.init()
        screen_width = 400
        screen_height = 400
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Custom Grid World")

        clock = pygame.time.Clock()  # Create a clock object to control frame rate

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))

            cell_width = screen_width // self.grid_size
            cell_height = screen_height // self.grid_size

            for x in range(self.grid_size):
                for y in range(self.grid_size):
                    rect = pygame.Rect(
                        x * cell_width, y * cell_height, cell_width, cell_height)
                    if self.grid[y][x] == -1:  # Obstacle
                        pygame.draw.rect(screen, (0, 0, 0), rect)
                    elif self.grid[y][x] == 1:  # Reward
                        pygame.draw.rect(screen, (0, 255, 0), rect)
                    elif self.grid[y][x] == 2:  # Boat
                        pygame.draw.rect(screen, (255, 0, 0), rect)

            pygame.display.flip()
            clock.tick(30)  # Limit the frame rate to 30 FPS

        pygame.quit()  # Quit Pygame when the loop exits


    def _render_symbol(self, val):
        if val == -1:
            return "X"  # Obstacle
        elif val == 1:
            return "R"  # Reward
        elif val == 2:
            return "B"  # Boat
        else:
            return "O"  # Empty

    def close(self):
        pass


if __name__ == '__main__':
    env = CustomGridWorldEnv()
    env.reset()
    env.step(3)
    env.step(3)
    env.step(1)