from world import *
from butterfly import *
import concurrent.futures

# Set the characteristics of the world: window dimensions and gravity (indicative value 4):
WIDTH, HEIGHT = 1200, 800
BUTTERFLIES = 10  # number of butterflies in the ecosystem
WASPS = 0  # number of wasps in the ecosystem

REFRESH_TIME = 6  # time in milliseconds for refresh the tkinter frame

# mean parameters for the creatures:
MAX_SPEED = 3
MAX_FORCE = 0.2
MEAN_MASS = 4

# global variables for food (left mouse click):
food_exists = False
food = PVector(0, 0)  # initialize food position

# ----------------------------------------------
# create the main window as a world object:
world = World("Ecosystem", WIDTH, HEIGHT)
# It returns the top window object, the canvas and the gravity vector:
top_window, canvas = world.create()

# create an array of butterflies with random gaussian distribution characteristics around the mean values and
# deviations appropriate for each type:
butterflies = [Butterfly(canvas, max(0.5, rand.gauss(MAX_SPEED, 0.5)), max(0.1, rand.gauss(MAX_FORCE, 0.1)), max(1, rand.gauss(MEAN_MASS, 0.5)))
               for i in range(BUTTERFLIES)]

# mean test butterfly
# butterflies = [Butterfly(canvas, MAX_SPEED, MAX_FORCE, MEAN_MASS)]


# create an obstacle
#obstacle1 = Obstacle(canvas, 500, 300, 10, 250, 'blue')
#obstacle2 = Obstacle(canvas, 800, 300, 150, 10, 'blue')


# ------------------------------------------------------------------
# define butterfly behaviours: using the after method it re-runs inside the tkinter mainloop
def butterfly_behaviours():
    global food_exists  # flag to indicate existence of food
    global food  # PVector of the food position

    # Update each butterfly's state sequentially.
    for butterfly in butterflies:
        # First, determine the primary goal: seek food or wander.
        if food_exists:
            # butterfly.apply_perceptron(food)
            butterfly.seek(food, direction="none")
        else:
            butterfly.wander()

        # Apply other behaviors like avoiding borders and other butterflies.
        # These behaviors accumulate forces in the butterfly's acceleration vector.
        butterfly.boundaries()
        butterfly.separate(butterflies)

        # The obstacle logic is commented out in the original file.
        # butterfly.bounce_from_obstacle(obstacle1)
        # butterfly.avoid_obstacle(obstacle1)

        # Then, update the butterfly's position based on all accumulated forces.
        butterfly.move()

        # Finally, enforce hard boundaries.
        butterfly.bounce()

    # re-runs the method each REFRESH_TIME millisecond:
    canvas.after(REFRESH_TIME, butterfly_behaviours)


# ----------------------------------------------
# define left mouse button press callback - food offering for butterflies:
def left_button_press(event):
    # raise the flag that food exists:
    global food_exists
    global food

    food_exists = True
    # define food position:
    food.x = event.x
    food.y = event.y

# bind mouse left button press with callback routine:
canvas.bind('<ButtonPress-1>', left_button_press)

# ----------------------------------------------
# define left mouse button release callback: food stops
def left_button_release(event):
    # when left button released, butterfly stops seeking food location:
    global food_exists
    food_exists = False  # flag is down

# bind mouse left button release with callback routine:
canvas.bind('<ButtonRelease-1>', left_button_release)

# ----------------------------------------------
# main event loop of tkinter:
butterfly_behaviours()
top_window.mainloop()
