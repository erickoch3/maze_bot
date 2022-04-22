"""This module runs a bot to navigate through a maze."""
import numpy as np 
import cv2 
import matplotlib.pyplot as plt
import PIL.Image as Image
import gym
import random
import time
from IPython import display

# Reference: https://blog.paperspace.com/creating-custom-environments-openai-gym/
from gym import Env, spaces
import time

font = cv2.FONT_HERSHEY_COMPLEX_SMALL 


class Maze(Env):
    def __init__(self):
        super(Maze, self).__init__()
        
        # Define a 2-D observation space
        self.observation_shape = (600, 800, 3)
        self.observation_space = spaces.Box(low = np.zeros(self.observation_shape), 
                                            high = np.ones(self.observation_shape),
                                            dtype = np.float16)
    
        
        # Define an action space ranging from 0 to 3
        self.action_space = spaces.Discrete(4,)
                        
        # Create a canvas to render the environment images upon 
        self.canvas = np.ones(self.observation_shape) * 1
        
        # Define elements present inside the environment
        self.elements = []
        
        # Permissible area of player to be 
        self.y_min = int (self.observation_shape[0] * 0.1)
        self.x_min = 0
        self.y_max = int (self.observation_shape[0] * 0.9)
        self.x_max = self.observation_shape[1]
    
    def draw_elements_on_canvas(self):
        # Init the canvas 
        self.canvas = np.ones(self.observation_shape) * 1

        # Draw the heliopter on canvas
        for elem in self.elements:
            elem_shape = elem.icon.shape
            x,y = elem.x, elem.y
            self.canvas[y : y + elem_shape[1], x:x + elem_shape[0]] = elem.icon

        text = 'Rewards: {}'.format(self.ep_return)

        # Put the info on canvas 
        self.canvas = cv2.putText(self.canvas, text, (10,20), font,  
                0.8, (0,0,0), 1, cv2.LINE_AA)
    
    def reset(self):
        # Reset the reward
        self.ep_return  = 0

        # Determine a place to intialise the player in
        x = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.10))
        y = random.randrange(int(self.observation_shape[1] * 0.15), int(self.observation_shape[1] * 0.20))
        
        # Intialise the player
        self.player = Player("player", self.x_max, self.x_min, self.y_max, self.y_min)
        self.player.set_position(x, y)

        # Intialise the elements 
        self.elements = [self.player]
        
        # Initialize the walls
        self.walls = []
        for _ in range(random.randrange(3, 10)):
            self.walls += self.build_wall()
        self.elements += self.walls
        
        # Determine a place to intialise the goal in
        goal_loc = self.random_goal_loc()
        # Make sure it's not on a wall.
        while self.is_a_wall(goal_loc):
            goal_loc = self.random_goal_loc()
            
        # Initialize the goal
        self.goal = Goal("goal", self.x_max, self.x_min, self.y_max, self.y_min)
        self.goal.set_position(x, y)
        self.elements += [self.goal]

        # Reset the Canvas 
        self.canvas = np.ones(self.observation_shape) * 1

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        # return the observation
        return self.canvas
    
    def random_goal_loc(self):
        x = random.randrange(int(self.observation_shape[0] * 0.3), int(self.observation_shape[0] * 0.90))
        y = random.randrange(int(self.observation_shape[1] * 0.2), int(self.observation_shape[1] * 0.95))
        return [x, y]
    
    
    def build_wall(self):
        wall = []
        # Initialize an anchor at a random point on the board.
        x = random.randrange(int(self.observation_shape[0] * 0.05), int(self.observation_shape[0] * 0.95))
        y = random.randrange(int(self.observation_shape[1] * 0.05), int(self.observation_shape[1] * 0.95))
        coords = np.array([x, y])
        wall.append(Wall("wall", self.x_max, self.x_min, self.y_max, self.y_min))
        wall[-1].set_position(x, y)
        direction = self.random_direction()
        for _ in range(random.randrange(3, 8)):
            wall.append(Wall("wall", self.x_max, self.x_min, self.y_max, self.y_min))
            coords = coords + direction
            wall[-1].set_position(coords[0], coords[1])
        return wall
    
    def random_direction(self):
        return random.choice([
            np.array([32, 0]),
            np.array([-32, 0]),
            np.array([0, 32]),
            np.array([0, -32])
        ])
    
    def render(self, mode = "human"):
        assert mode in ["human", "rgb_array"], "Invalid mode, must be either \"human\" or \"rgb_array\""
        if mode == "human":
            cv2.imshow("Game", self.canvas)
            cv2.waitKey(10)
        
        elif mode == "rgb_array":
            return self.canvas
    
    def close(self):
        cv2.destroyAllWindows()
    
    def get_action_meanings(self):
        return {0: "RIGHT", 1: "LEFT", 2: "DOWN", 3: "UP"}
        
    def step(self, action):
        # Flag that marks the termination of an episode
        done = False
        
        # Assert that it is a valid action 
        assert self.action_space.contains(action), "Invalid Action"

        action_dict = {
            0: [0, 32],
            1: [0, -32],
            2: [32, 0],
            3: [-32, 0]
        }
        direction = action_dict[action]
        new_loc = self.player.loc() + direction
        
        
        if self.is_a_wall(new_loc):
            reward = -10
    
        else:
            # apply the action to the player
            self.player.move(direction)

            # Reward for executing a step.
            reward = 1/self.goal_distance()
            
            # Check for victory
            if self.victory_check():
                reward = 1000
                done = True

        # Increment the episodic return
        self.ep_return += 1

        # Draw elements on the canvas
        self.draw_elements_on_canvas()

        return self.canvas, reward, done, []
    
    def is_a_wall(self, location):
        """ Returns True if the location is a wall. """
        for wall in self.walls:
            wall_loc = np.array([wall.x, wall.y])
            if np.allclose(location, wall_loc, atol=16):
                return True
        return False
            
    def victory_check(self):
        # Check for victory
        player = np.array([self.player.x, self.player.y])
        goal = np.array([self.goal.x, self.goal.y])
        return np.allclose(player, goal, atol=16)
    
    def goal_distance(self):
        player = np.array([self.player.x, self.player.y])
        goal = np.array([self.goal.x, self.goal.y])
        return np.linalg.norm(goal - player) 

class Point(object):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        self.x = 0
        self.y = 0
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.name = name
    
    def set_position(self, x, y):
        self.x = self.clamp(x, self.x_min, self.x_max - self.icon_w)
        self.y = self.clamp(y, self.y_min, self.y_max - self.icon_h)
    
    def get_position(self):
        return (self.x, self.y)
    
    def move(self, direction):
        self.x += direction[0]
        self.y += direction[1]
        
        self.x = self.clamp(self.x, self.x_min, self.x_max - self.icon_w)
        self.y = self.clamp(self.y, self.y_min, self.y_max - self.icon_h)

    def clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)
    
    
    def loc(self):
        return np.array([self.x, self.y])
    
class Player(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Player, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("player_icon.png") / 255.0
        self.icon_w = 32
        self.icon_h = 32
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))

    
class Wall(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Wall, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("wall_icon.png") / 255.0
        self.icon_w = 32
        self.icon_h = 32
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))
    
class Goal(Point):
    def __init__(self, name, x_max, x_min, y_max, y_min):
        super(Goal, self).__init__(name, x_max, x_min, y_max, y_min)
        self.icon = cv2.imread("goal_icon.png") / 255.0
        self.icon_w = 32
        self.icon_h = 32
        self.icon = cv2.resize(self.icon, (self.icon_h, self.icon_w))

if __name__ == "__main__":
    
    # env = Maze()
    # env.reset()
    # #for _ in range(1000):
    # screen = env.render(mode = "rgb_array")
    # plt.imshow(screen)

        # env.step(env.action_space.sample()) # take a random action
    # env.close()

    env = Maze()
    obs = env.reset()

    while True:
        time.sleep(1)
        # Take a random action
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
        
        # Render the game
        env.render()
        
        if done == True:
            break

    env.close()