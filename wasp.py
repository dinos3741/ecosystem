import pygame
from pygame.math import Vector2
import random as rand
from butterfly import Butterfly
from math import pi, cos, sin, degrees, radians
from Perceptron import Perceptron

class Wasp(Butterfly):
    def __init__(self, x, y, max_speed, max_force, max_mass):
        # Call parent constructor for common initialization (location, velocity, acceleration, etc.)
        # We pass dummy values for image loading as Wasp will override it immediately
        super().__init__(x, y, max_speed, max_force, max_mass)

        # Wasp-specific initialization
        self.is_alive = True
        self.obstacle_hits = 0

        # Override image loading for wasp.png
        try:
            self.base_image = pygame.image.load('wasp.png').convert_alpha()
        except pygame.error:
            print("Warning: wasp.png not found. Using a placeholder square.")
            self.base_image = pygame.Surface((10, 10))
            self.base_image.fill((255, 255, 0)) # Yellow for wasp placeholder

        self.size = int(self.mass * 10)
        self.image = pygame.transform.scale(self.base_image, (self.size, self.size))
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))

        # Wasp's brain (if different from butterfly's) - keeping original logic
        nr_forces = 8
        self.brain = Perceptron(nr_forces, 0.01)
        self.forces = []
        for i in range(nr_forces):
            force = Vector2(self.max_force, 0)
            force = force.rotate(degrees(2 * pi * i / nr_forces)) # Use Vector2.rotate
            self.forces.append(force)

    # Wasps have a different seek method, with slowing down later before reaching the butterflies
    # This overrides Butterfly.seek, so it must match its signature (target, direction)
    def seek(self, target, direction):
        CLOSE_ENOUGH = 10  # Wasps get much closer than butterflies (Butterfly has 50)
        desired = target - self.location # Use operator overloading
        distance = desired.length() # Use Vector2.length

        if distance < CLOSE_ENOUGH:
            target_speed = self.max_speed * (distance / CLOSE_ENOUGH)
        else:
            target_speed = self.max_speed

        if desired.length() > 0:
            desired = desired.normalize() * target_speed # Use Vector2.normalize and multiply
        else:
            desired = Vector2(0,0)

        if direction == 'avoid':
            desired *= -1 # Use operator overloading

        steer = desired - self.velocity # Use operator overloading
        
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        self.apply_force(steer)

    # Different bounce method from the butterflies: here for each hit on wall, force is reduced by 2%
    # This overrides Butterfly.bounce, so it must match its signature (width, height)
    def bounce(self, width, height):
        # Call parent bounce for basic wall collision and position correction
        super().bounce(width, height)
        
        # Apply wasp-specific speed reduction if it hit a boundary
        radius = self.size / 2
        # Check if it's at or beyond any boundary after super().bounce adjusted its position
        if (self.location.x <= radius + 1 or self.location.x >= width - radius - 1 or
            self.location.y <= radius + 1 or self.location.y >= height - radius - 1):
            self.max_speed *= 0.98

    def chase_butterflies(self, butterflies):
        distance_list = []
        # Filter out dead butterflies and self
        alive_butterflies = [b for b in butterflies if getattr(b, 'is_alive', True) and b is not self]

        if not alive_butterflies: # No alive butterflies to chase
            return

        # Find the nearest alive butterfly
        min_distance = float('inf')
        nearest_butterfly = None
        for b in alive_butterflies:
            distance = self.location.distance_to(b.location) # Use Vector2.distance_to
            if distance < min_distance:
                min_distance = distance
                nearest_butterfly = b

        if nearest_butterfly:
            self.seek(nearest_butterfly.location, "attract") # Call wasp's seek method

            # If butterfly reached, mark it as not alive:
            if self.location.distance_to(nearest_butterfly.location) < 10: # Wasp's CLOSE_ENOUGH
                nearest_butterfly.is_alive = False

    def update_behaviors(self, food_target, obstacles, all_creatures, width, height):
        # Filter out only the actual butterflies from all_creatures that are alive
        actual_butterflies = [c for c in all_creatures if isinstance(c, Butterfly) and not isinstance(c, Wasp) and getattr(c, 'is_alive', True)]

        # Decision: Chase butterflies or wander
        if actual_butterflies: # Check if there are actual butterflies to chase
            self.chase_butterflies(actual_butterflies) # Pass only actual butterflies
        else:
            self.wander()
        
        # Apply other behaviors
        self.boundaries(width, height)
        self.avoid_obstacles(obstacles) # Add obstacle avoidance for wasps
        for obs in obstacles:
            self.bounce_from_obstacle(obs) # Add bounce from obstacles for wasps

        # Update motion
        self.move()
        self.bounce(width, height) # Wasp's bounce reduces speed