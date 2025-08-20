import pygame
from PVector import PVector
import random as rand
from butterfly import Butterfly
from wasp import Wasp
from obstacle import Obstacle

# Set the characteristics of the world
WIDTH, HEIGHT = 1200, 800
FPS = 70
BUTTERFLIES = 5
WASPS = 0

# --- Constants for creating creatures ---
MAX_SPEED = 6
MAX_FORCE = 0.4
MEAN_MASS = 4
# ------------------------------------

# --- Global variables for food source ---
food_exists = False
food = PVector(0, 0)
# ------------------------------------

# Colors
LIGHT_BLUE = (173, 216, 230)

def main():
    global food_exists, food

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ecosystem")
    clock = pygame.time.Clock()

    # Create butterflies
    butterflies = [
        Butterfly(
            rand.randrange(0, WIDTH),
            rand.randrange(0, HEIGHT),
            max(0.5, rand.gauss(MAX_SPEED, 0.5)),
            max(0.1, rand.gauss(MAX_FORCE, 0.1)),
            max(1, rand.gauss(MEAN_MASS, 0.5))
        )
        for _ in range(BUTTERFLIES)
    ]

    # Create wasps
    wasps = [
        Wasp(
            rand.randrange(0, WIDTH),
            rand.randrange(0, HEIGHT),
            max(0.5, rand.gauss(MAX_SPEED * 1.2, 0.5)),
            max(0.1, rand.gauss(MAX_FORCE * 1.2, 0.1)),
            max(1, rand.gauss(MEAN_MASS * 0.8, 0.5))
        )
        for _ in range(WASPS)
    ]

    # Create obstacles
    obstacles = [
        Obstacle(300, 200, 100, 50, (100, 100, 100)), # Grey rectangle
        Obstacle(700, 400, 50, 150, (100, 100, 100))  # Another grey rectangle
    ]

    running = True
    while running:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    food_exists = True
                    mouse_x, mouse_y = event.pos
                    food.set(mouse_x, mouse_y)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    food_exists = False

        # Drawing (fill background once per frame)
        screen.fill(LIGHT_BLUE)

        # Draw obstacles (before creatures, so creatures are on top)
        for obs in obstacles:
            obs.draw(screen)

        # Update and draw all butterflies
        # Filter out dead butterflies
        butterflies = [b for b in butterflies if getattr(b, 'is_alive', True)]
        
        for b in butterflies:
            if food_exists:
                b.navigate_to_food(food, obstacles) # Use new navigation method
            else:
                b.wander()
            
            b.boundaries(WIDTH, HEIGHT)
            b.separate(butterflies) # Butterflies separate from each other
            b.avoid_obstacles(obstacles) # Add obstacle avoidance
            
            # Add bounce from obstacles
            for obs in obstacles:
                b.bounce_from_obstacle(obs)

            b.move() # Move after all forces and bounces are applied
            b.bounce(WIDTH, HEIGHT) # Bounce from screen edges

            b.draw(screen)

        # Update and draw all wasps
        for w in wasps:
            # If there are butterflies to chase, chase them.
            # Otherwise, wander.
            if butterflies: # Check if the list of butterflies is not empty
                w.chase_butterflies(butterflies)
            else:
                w.wander()

            w.boundaries(WIDTH, HEIGHT)
            w.avoid_obstacles(obstacles) # Add obstacle avoidance for wasps
            for obs in obstacles:
                w.bounce_from_obstacle(obs) # Add bounce from obstacles for wasps

            w.move()
            w.bounce(WIDTH, HEIGHT) # Wasp's bounce reduces speed

            w.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()