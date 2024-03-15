import pygame
import random
from enum import Enum
from collections import namedtuple
from tsp_new import TSP
import numpy as np

pygame.init()
font = pygame.font.Font(None, 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 40
SPEED = 40

# Load background image
background = pygame.image.load("../assets/background.jpg")  # Replace with your image path


class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head]
                    #   Point(self.head.x-BLOCK_SIZE, self.head.y),
                    #   Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self.all_food = []
        self.obstacles = []
        self._place_obstacles()
        self._place_food()
        self.frame_iteration = 0
            


    def _place_obstacles(self):
        num_obstacles = 3  # You can adjust the number of obstacles
        for _ in range(num_obstacles):
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            obstacle = Point(x, y)
            if obstacle not in self.snake and obstacle != self.food:
                self.obstacles.append(obstacle)


    def _place_food(self, num_food=3):
        food_locations = []
        foods = []
        for _ in range(num_food):
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            food = Point(x, y)
            if food not in self.snake and food not in self.obstacles:
                food_locations.append((x, y))
                foods.append(food)

        # print(food_locations)
        tour = TSP().solve_tsp(food_locations)
        # print(tour)

        for i in tour:
            self.all_food.append(foods[i])

        self.food = self.all_food[0] #TODO: Also do this to the food in the play_step method and what to do when the food is eaten


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = -0.1
        game_over = False
        
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food: #TODO: include all the food
            self.score += 1
            reward = 10
            # self._place_food()
            self.all_food.pop(0)
            if len(self.all_food) == 0:
                game_over = True
                return reward, game_over, self.score
            self.food = self.all_food[0]
            self.snake.pop()
        elif self.head in self.all_food[1:]:
            self.score += 1
            reward = 10
            self.all_food.remove(self.head)
            if len(self.all_food) == 0:
                game_over = True
                return reward, game_over, self.score
            self.food = self.all_food[0]
            self.snake.pop()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:] or pt in self.obstacles:
            return True

        return False


    def _update_ui(self):
        self.display.blit(background, (0, 0))

        # Draw obstacles
        for obstacle_index in range(len(self.obstacles)):
            obstacle = self.obstacles[obstacle_index]
            obstacle_image = pygame.image.load(f"../assets/obstacle_{obstacle_index+1}.png")
            obstacle_image = pygame.transform.scale(obstacle_image, (BLOCK_SIZE, BLOCK_SIZE))
            self.display.blit(obstacle_image, (obstacle.x, obstacle.y))

        # Draw snake
        for i, pt in enumerate(self.snake):
            if i == 0:
                snake_head_image = pygame.image.load("../assets/boat.png")
                snake_head_image = pygame.transform.scale(snake_head_image, (BLOCK_SIZE, BLOCK_SIZE))
                self.display.blit(snake_head_image, (pt.x, pt.y))
            else:
                pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw food
        food_image = pygame.image.load("../assets/sample.png")
        food_image = pygame.transform.scale(food_image, (BLOCK_SIZE, BLOCK_SIZE))
        # print(len(self.all_food))
        for food in self.all_food:
            self.display.blit(food_image, (food.x, food.y))
        # self.display.blit(food_image, (self.food.x, self.food.y))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)