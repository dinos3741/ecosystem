import pygame
import random as rand
from math import pi, cos, sin, degrees, radians

from pygame.math import Vector2
from Perceptron import Perceptron

class Butterfly:
    def __init__(self, x, y, max_speed, max_force, max_mass):
        # Motion variables
        self.location = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
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
            force = Vector2(self.max_force, 0) # Use Vector2
            force = force.rotate(degrees(2 * pi * i / nr_forces)) # Use Vector2.rotate
            self.forces.append(force)

    def move(self):
        self.velocity += self.acceleration # Use operator overloading
        
        # Limit speed using Vector2.scale_to_length or normalize and multiply
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        self.location += self.velocity # Use operator overloading
        self.acceleration *= 0 # Use operator overloading

    def draw(self, screen):
        self.rect.center = (int(self.location.x), int(self.location.y)) # Cast to int for rect
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

    def bounce_from_obstacle(self, obstacle):
        # Update rect's center to current location before collision check
        self.rect.center = (int(self.location.x), int(self.location.y)) # Cast to int

        if self.rect.colliderect(obstacle.rect):
            # Calculate previous position to determine which side was hit
            prev_location = self.location - self.velocity # Use operator overloading
            prev_rect = self.image.get_rect(center=(int(prev_location.x), int(prev_location.y))) # Cast to int

            # Check for collision on X axis
            if prev_rect.right <= obstacle.rect.left and self.rect.right > obstacle.rect.left: # Hit left side of obstacle
                self.velocity.x *= -1
                self.location.x = obstacle.rect.left - self.size / 2 # Adjust to outside obstacle
            elif prev_rect.left >= obstacle.rect.right and self.rect.left < obstacle.rect.right: # Hit right side of obstacle
                self.velocity.x *= -1
                self.location.x = obstacle.rect.right + self.size / 2 # Adjust to outside obstacle

            # Check for collision on Y axis
            if prev_rect.bottom <= obstacle.rect.top and self.rect.bottom > obstacle.rect.top: # Hit top side of obstacle
                self.velocity.y *= -1
                self.location.y = obstacle.rect.top - self.size / 2 # Adjust to outside obstacle
            elif prev_rect.top >= obstacle.rect.bottom and self.rect.top < obstacle.rect.bottom: # Hit bottom side of obstacle
                self.velocity.y *= -1
                self.location.y = obstacle.rect.bottom + self.size / 2 # Adjust to outside obstacle

            # Update rect after location change
            self.rect.center = (int(self.location.x), int(self.location.y)) # Cast to int

    def is_path_blocked(self, target, obstacles):
        line_start = (int(self.location.x), int(self.location.y))
        line_end = (int(target.x), int(target.y))

        for obs in obstacles:
            if obs.rect.clipline(line_start, line_end):
                return True # Path is blocked by this obstacle
        return False # Path is clear

    def navigate_to_food(self, food_target, obstacles):
        # If no food, just wander
        if food_target is None:
            self.wander()
            return

        # Check if direct path to food is blocked
        path_blocked = False
        closest_blocking_obstacle = None
        min_dist_to_blocking_obs = float('inf')
        
        line_start = (int(self.location.x), int(self.location.y))
        line_end = (int(food_target.x), int(food_target.y))

        for obs in obstacles:
            if obs.rect.clipline(line_start, line_end):
                path_blocked = True
                dist_to_obs = self.location.distance_to(Vector2(obs.rect.centerx, obs.rect.centery))
                if dist_to_obs < min_dist_to_blocking_obs:
                    min_dist_to_blocking_obs = dist_to_obs
                    closest_blocking_obstacle = obs

        if path_blocked and closest_blocking_obstacle:
            # Path is blocked, calculate a waypoint to go around
            obs_center = Vector2(closest_blocking_obstacle.rect.centerx, closest_blocking_obstacle.rect.centery)
            vec_to_obstacle = obs_center - self.location
            
            offset_distance = max(closest_blocking_obstacle.rect.width, closest_blocking_obstacle.rect.height) / 2 + self.size / 2 + 120 # Increased Buffer (even more)

            waypoint1_vec = Vector2(vec_to_obstacle.x, vec_to_obstacle.y)
            waypoint1_vec = waypoint1_vec.rotate(degrees(pi / 2))
            waypoint1_vec = waypoint1_vec.normalize() * offset_distance
            waypoint1 = Vector2(obs_center.x, obs_center.y)
            waypoint1 += waypoint1_vec # Use operator overloading
            
            waypoint2_vec = Vector2(vec_to_obstacle.x, vec_to_obstacle.y)
            waypoint2_vec = waypoint2_vec.rotate(degrees(-pi / 2))
            waypoint2_vec = waypoint2_vec.normalize() * offset_distance
            waypoint2 = Vector2(obs_center.x, obs_center.y)
            waypoint2 += waypoint2_vec # Use operator overloading
            
            # Choose the waypoint that is closer to the food target
            if waypoint1.distance_to(food_target) < waypoint2.distance_to(food_target):
                waypoint = waypoint1
            else:
                waypoint = waypoint2
            
            # Seek the chosen waypoint
            self.seek(waypoint, "attract")
            
        else:
            # Path is clear, seek food directly
            self.seek(food_target, "attract")

    def update_behaviors(self, food_target, obstacles, all_creatures, width, height):
        # Decision: Seek food or wander
        if food_target is not None:
            self.navigate_to_food(food_target, obstacles)
        else:
            self.wander()
        
        # Apply other behaviors
        self.boundaries(width, height)
        self.separate(all_creatures) # Pass all creatures for separation
        self.avoid_obstacles(obstacles)
        
        # Handle bounces
        for obs in obstacles:
            self.bounce_from_obstacle(obs)

        # Update motion
        self.move()
        self.bounce(width, height) # Bounce from screen edges

    def boundaries(self, width, height):
        DISTANCE_FROM_BORDER = 100
        desired = None

        if self.location.x < DISTANCE_FROM_BORDER:
            desired = Vector2(self.max_speed, self.velocity.y)
        elif self.location.x > width - DISTANCE_FROM_BORDER:
            desired = Vector2(-self.max_speed, self.velocity.y)

        if self.location.y < DISTANCE_FROM_BORDER:
            desired = Vector2(self.velocity.x, self.max_speed)
        elif self.location.y > height - DISTANCE_FROM_BORDER:
            desired = Vector2(self.velocity.x, -self.max_speed)

        if desired is not None:
            desired = desired.normalize() * self.max_speed
            steer = desired - self.velocity
            
            if steer.length() > self.max_force * 2:
                steer.scale_to_length(self.max_force * 2)
            self.apply_force(steer)

    def flee(self, target):
        desired = (self.location - target).normalize() * self.max_speed
        steer = desired - self.velocity
        # Apply a stronger force for avoidance
        if steer.length() > self.max_force * 2.0:
            steer.scale_to_length(self.max_force * 2.0)
        self.apply_force(steer)

    def avoid_obstacles(self, obstacles):
        SAFE_DISTANCE = 100  # minimum distance before activating fleeing
        for obstacle in obstacles:
            # Check if butterfly is within the horizontal span of the obstacle
            if obstacle.rect.left < self.location.x < obstacle.rect.right:
                # Check vertical distance to top and bottom edges
                distance_to_top = abs(self.location.y - obstacle.rect.top)
                distance_to_bottom = abs(self.location.y - obstacle.rect.bottom)
                
                if distance_to_top < SAFE_DISTANCE:
                    self.flee(Vector2(self.location.x, obstacle.rect.top))
                if distance_to_bottom < SAFE_DISTANCE:
                    self.flee(Vector2(self.location.x, obstacle.rect.bottom))

            # Check if butterfly is within the vertical span of the obstacle
            if obstacle.rect.top < self.location.y < obstacle.rect.bottom:
                # Check horizontal distance to left and right edges
                distance_to_left = abs(self.location.x - obstacle.rect.left)
                distance_to_right = abs(self.location.x - obstacle.rect.right)

                if distance_to_left < SAFE_DISTANCE:
                    self.flee(Vector2(obstacle.rect.left, self.location.y))
                if distance_to_right < SAFE_DISTANCE:
                    self.flee(Vector2(obstacle.rect.right, self.location.y))

    def seek(self, target, direction):
        CLOSE_ENOUGH = 50
        desired = target - self.location
        distance = desired.length()

        if distance < CLOSE_ENOUGH:
            target_speed = self.max_speed * (distance / CLOSE_ENOUGH)
        else:
            target_speed = self.max_speed

        if desired.length() > 0:
            desired = desired.normalize() * target_speed
        else:
            desired = Vector2(0,0)

        if direction == 'avoid':
            desired *= -1

        steer = desired - self.velocity
        
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        self.apply_force(steer)

    def wander(self):
        wanderR = 30
        wanderD = 50
        change = 0.3
        self.wander_theta += rand.uniform(-change, change)

        # Calculate wander target
        wander_pos = Vector2(self.velocity.x, self.velocity.y)
        if wander_pos.length() == 0: # Handle case where butterfly is stationary
            wander_pos = Vector2(1, 0)
            
        wander_pos = wander_pos.normalize() * wanderD
        wander_pos += self.location

        heading = self.velocity.angle_to(Vector2(1,0))
        wander_offset = Vector2(wanderR, 0).rotate(degrees(self.wander_theta + radians(heading)))

        target = wander_pos + wander_offset
        self.seek(target, 'attract')

    def separate(self, all_creatures):
        separation_distance = self.size * 2
        sum_vec = Vector2(0, 0)
        count = 0
        for other in all_creatures:
            if other is not self:
                distance = self.location.distance_to(other.location)
                if 0 < distance < separation_distance:
                    diff = self.location - other.location
                    diff = diff.normalize() / distance
                    sum_vec += diff
                    count += 1
        if count > 0:
            sum_vec /= count
            sum_vec = sum_vec.normalize() * self.max_speed
            steer = sum_vec - self.velocity
            
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
            self.apply_force(steer)

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    # Removed apply_perceptron as it's not used by Butterfly or Wasp anymore.
    # def apply_perceptron(self, target):
    #     brain_result = self.brain.feed_forward(self.forces)
    #     self.apply_force(brain_result)
    #     error = target - self.location
    #     self.brain.train(self.forces, error)
