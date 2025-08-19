import pygame
import random as rand
from math import pi, cos, sin

from PVector import PVector
from Perceptron import Perceptron

class Butterfly:
    def __init__(self, x, y, max_speed, max_force, max_mass):
        # Motion variables
        self.location = PVector(x, y)
        self.velocity = PVector(0, 0)
        self.acceleration = PVector(0, 0)
        self.max_speed = max_speed
        self.max_force = max_force
        self.mass = max_mass
        self.wander_theta = 0

        # Pygame variables
        try:
            self.base_image = pygame.image.load('butterfly.png').convert_alpha()
        except pygame.error:
            print("Warning: butterfly.png not found. Using a placeholder square.")
            self.base_image = pygame.Surface((10, 10))
            self.base_image.fill((255, 0, 255)) # Bright pink for visibility
            
        self.size = int(self.mass * 10)
        self.image = pygame.transform.scale(self.base_image, (self.size, self.size))
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))

        # AI/Brain variables
        nr_forces = 8
        self.brain = Perceptron(nr_forces, 0.01)
        self.forces = []
        for i in range(nr_forces):
            force = PVector(self.max_force, 0)
            force.Rotate(2 * pi * i / nr_forces)
            self.forces.append(force)

    def move(self):
        self.velocity.Add(self.acceleration)
        self.velocity.Limit(self.max_speed)
        self.location.Add(self.velocity)
        self.acceleration.Mult(0)

    def draw(self, screen):
        self.rect.center = (self.location.x, self.location.y)
        screen.blit(self.image, self.rect)

    def bounce(self, width, height):
        radius = self.size / 2
        if self.location.x < radius:
            self.location.x = radius
            self.velocity.x *= -1
        elif self.location.x > width - radius:
            self.location.x = width - radius
            self.velocity.x *= -1

        if self.location.y < radius:
            self.location.y = radius
            self.velocity.y *= -1
        elif self.location.y > height - radius:
            self.location.y = height - radius
            self.velocity.y *= -1

    def boundaries(self, width, height):
        DISTANCE_FROM_BORDER = 100
        desired = None

        if self.location.x < DISTANCE_FROM_BORDER:
            desired = PVector(self.max_speed, self.velocity.y)
        elif self.location.x > width - DISTANCE_FROM_BORDER:
            desired = PVector(-self.max_speed, self.velocity.y)

        if self.location.y < DISTANCE_FROM_BORDER:
            desired = PVector(self.velocity.x, self.max_speed)
        elif self.location.y > height - DISTANCE_FROM_BORDER:
            desired = PVector(self.velocity.x, -self.max_speed)

        if desired is not None:
            desired.Normalize()
            desired.Mult(self.max_speed)
            steer = desired.Sub(self.velocity)
            steer.Limit(self.max_force * 2)
            self.apply_force(steer)

    def seek(self, target, direction):
        CLOSE_ENOUGH = 50
        desired = target.Sub(self.location)
        distance = desired.get_Magnitude()

        if distance < CLOSE_ENOUGH:
            target_speed = self.max_speed * (distance / CLOSE_ENOUGH)
        else:
            target_speed = self.max_speed

        desired.set_Magnitude(target_speed)

        if direction == 'avoid':
            desired.Mult(-1)

        steer = desired.Sub(self.velocity)
        steer.Limit(self.max_force)
        self.apply_force(steer)

    def wander(self):
        wanderR = 30
        wanderD = 50
        change = 0.3
        self.wander_theta += rand.uniform(-change, change)

        # Calculate wander target
        wander_pos = PVector(self.velocity.x, self.velocity.y)
        if wander_pos.get_Magnitude() == 0: # Handle case where butterfly is stationary
            wander_pos = PVector(1, 0)
            
        wander_pos.Normalize()
        wander_pos.Mult(wanderD)
        wander_pos.Add(self.location)

        heading = self.velocity.heading2D()
        wander_offset = PVector(wanderR * cos(self.wander_theta + heading), wanderR * sin(self.wander_theta + heading))

        target = PVector(wander_pos.x + wander_offset.x, wander_pos.y + wander_offset.y)
        self.seek(target, 'attract')

    def separate(self, butterflies):
        separation_distance = self.size * 2
        sum_vec = PVector(0, 0)
        count = 0
        for other in butterflies:
            if other is not self:
                distance = self.location.Distance(other.location)
                if 0 < distance < separation_distance:
                    diff = self.location.Sub(other.location)
                    diff.Normalize()
                    diff.Div(distance)  # Weight by distance
                    sum_vec.Add(diff)
                    count += 1
        if count > 0:
            sum_vec.Div(count)
            sum_vec.Normalize()
            sum_vec.Mult(self.max_speed)
            steer = sum_vec.Sub(self.velocity)
            steer.Limit(self.max_force)
            self.apply_force(steer)

    def apply_force(self, force):
        f = force.Div(self.mass)
        self.acceleration.Add(f)

    def apply_perceptron(self, target):
        brain_result = self.brain.feed_forward(self.forces)
        self.apply_force(brain_result)
        error = target.Sub(self.location)
        self.brain.train(self.forces, error)
