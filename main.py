import pygame
from pygame.math import Vector2
import random as rand
from butterfly import Butterfly
from wasp import Wasp
from obstacle import Obstacle

class Game:
    # Constants
    WIDTH = 1200
    HEIGHT = 800
    FPS = 70
    BUTTERFLIES = 5
    WASPS = 0

    MAX_SPEED = 8
    MAX_FORCE = 0.3
    MEAN_MASS = 4

    LIGHT_BLUE = (173, 216, 230)

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        pygame.display.set_caption("Ecosystem")
        self.clock = pygame.time.Clock()

        # Game state variables
        self.food_exists = False
        self.food = Vector2(0, 0)

        # Create creatures and obstacles
        self.butterflies = self._create_butterflies()
        self.wasps = self._create_wasps()
        self.obstacles = self._create_obstacles()

    def _create_butterflies(self):
        return [
            Butterfly(
                rand.randrange(0, Game.WIDTH),
                rand.randrange(0, Game.HEIGHT),
                max(0.5, rand.gauss(Game.MAX_SPEED, 0.5)),
                max(0.1, rand.gauss(Game.MAX_FORCE, 0.2)),
                max(1, rand.gauss(Game.MEAN_MASS, 0.5))
            )
            for _ in range(Game.BUTTERFLIES)
        ]

    def _create_wasps(self):
        return [
            Wasp(
                rand.randrange(0, Game.WIDTH),
                rand.randrange(0, Game.HEIGHT),
                max(0.5, rand.gauss(Game.MAX_SPEED * 0.8, 0.5)),
                max(0.1, rand.gauss(Game.MAX_FORCE * 1.5, 0.2)),
                max(1, rand.gauss(Game.MEAN_MASS * 0.8, 0.5))
            )
            for _ in range(Game.WASPS)
        ]

    def _create_obstacles(self):
        return [
            Obstacle(300, 200, 100, 50, (100, 100, 100)),
            Obstacle(700, 400, 50, 150, (100, 100, 100))  # Another grey rectangle
        ]

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Signal to quit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.food_exists = True
                    self.food.x, self.food.y = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.food_exists = False
        return True # Continue running

    def _update_game_state(self):
        # Filter out dead butterflies
        self.butterflies = [b for b in self.butterflies if getattr(b, 'is_alive', True)]
        
        all_creatures = self.butterflies + self.wasps

        # Update all butterflies
        for b in self.butterflies:
            if self.food_exists:
                b.update_behaviors(self.food, self.obstacles, all_creatures, Game.WIDTH, Game.HEIGHT)
            else:
                b.update_behaviors(None, self.obstacles, all_creatures, Game.WIDTH, Game.HEIGHT)

        # Update all wasps
        for w in self.wasps:
            w.update_behaviors(self.food, self.obstacles, all_creatures, Game.WIDTH, Game.HEIGHT)

    def _draw_elements(self):
        self.screen.fill(Game.LIGHT_BLUE)

        # Draw obstacles
        for obs in self.obstacles:
            obs.draw(self.screen)

        # Draw butterflies
        for b in self.butterflies:
            b.draw(self.screen)

        # Draw wasps
        for w in self.wasps:
            w.draw(self.screen)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(Game.FPS)

            running = self._handle_events()

            if not running:
                break

            self._update_game_state()
            self._draw_elements()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()