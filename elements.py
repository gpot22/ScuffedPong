import pygame
import random

class Paddle:
    def __init__(self, screen, x, y, width, height, vel, colour, facing, comp=False):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = vel
        self.colour = colour
        self.facing = facing
        self.comp = comp
        self.shape = pygame.Rect(self.x, self.y, self.width, self.height)  # used to track position more easily
        self.score = 0

# ---------- Movement Functions ----------
    def moveLeft(self):
        self.x -= self.vel
        self.dimensions()

    def moveRight(self):
        self.x += self.vel
        self.dimensions()

    def moveUp(self):
        self.y -= self.vel
        self.dimensions()

    def moveDown(self):
        self.y += self.vel
        self.dimensions()
    
    # Update rect dimensions
    def dimensions(self, inverse=False):
        if not inverse:
            self.shape.x = self.x
            self.shape.y = self.y
        else:
            self.x = self.shape.x
            self.y = self.shape.y

    def draw(self):
        pygame.draw.rect(self.screen, self.colour, [self.x, self.y, self.width, self.height])


class Ball:
    def __init__(self, screen, x, y, size, x_vel, y_vel, colour):
        self.screen = screen
        self.x = x
        self.y = y
        self.size = size
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.colour = colour
        self.shape = pygame.Rect(self.x, self.y, self.size, self.size)

    # ball movement function
    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.dimensions()

    # Update rect dimensions
    def dimensions(self, inverse=False):
        if not inverse:
            self.shape.x = self.x
            self.shape.y = self.y
        else:
            self.x = self.shape.x
            self.y = self.shape.y

    # Method called in main file when collision occurs
    def bounce(self, sound, facing='v'):
        sound.play()
        direction_change = facing if facing in ['v', 'h'] else 'v'
        i = random.randint(1, 100)
        vel_change = 0 if i <= 10 else 0.75 if 10 < i <= 50 else 0.5 if 50 < i <= 70 else 1  # random possibilities for velocity change amounts
        j = random.randint(1, 10)
        vel_change *= -1 if j == 1 else 1 # 10% chance velocity decreases, 90% of the time it increases
        if direction_change == 'v':
            self.y_vel *= -1
            self.y_vel += - vel_change if self.y_vel < 0 else vel_change
            self.y_vel -= 1 if self.y_vel > 21 else 1 if self.y_vel < -21 else 0 # velocity can not go over 20
        else:
            self.x_vel *= -1
            self.x_vel += -vel_change if self.x_vel < 0 else vel_change
            self.x_vel -= 1 if self.x_vel > 21 else 1 if self.x_vel < -21 else 0 # x velocity can not go over 20

    def draw(self):
        pygame.draw.rect(self.screen, self.colour, [self.x, self.y, self.size, self.size])

# Parent class for walls and goal lines
class Boundary:
    def __init__(self, screen, x, y, width, height, colour):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.shape = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        pygame.draw.rect(self.screen, self.colour, [self.x, self.y, self.width, self.height])

class Wall(Boundary):
    def __init__(self, screen, x, y, width, height, colour):
        super().__init__(screen, x, y, width, height, colour)


class GoalLine(Boundary):
    def __init__(self, screen, x, y, width, height, colour):
        super().__init__(screen, x, y, width, height, colour)
