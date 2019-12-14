from world import *
from wasp import *

# Set the characteristics of the world: window dimensions and gravity (indicative value 4):
WIDTH = 1200; HEIGHT = 800; GRAVITY = 10
BUTTERFLIES = 9  # number of butterflies in the world
OBSTACLES = 0  # number of obstacles
WASPS = 1  # number of wasps in the world
REFRESH_TIME = 15  # time in msec

# general parameters of the butterflies and wasps:
MAX_SPEED = 10
MAX_FORCE = 5
MASS = 5
# parameters for the wandering
RADIUS = 200
DISTANCE = 100

# global variables for food (left mouse click):
food_exists = False
food = PVector(0, 0)

#----------------------------------------------
# create the main window as a world object.
world = World("New World", WIDTH, HEIGHT, GRAVITY, OBSTACLES)
# It returns the top window object, the canvas, the gravity vector and the obstacles list:
top_window, canvas, gravity, obstacles = world.create()

# create an array of butterflies with random characteristics:
butterflies = [Butterfly(canvas, randrange(2, MAX_SPEED), randrange(1, MAX_FORCE), MASS, RADIUS, DISTANCE) for i in range(BUTTERFLIES)]

# create an array of wasps with random characteristics (slightly more speed and force than the butterflies):
wasps = [Wasp(canvas, randrange(3, MAX_SPEED), randrange(2, MAX_FORCE), MASS, RADIUS, DISTANCE) for i in range(WASPS)]

#------------------------------------------------------------------
# butterfly behaviours: using the after method it re-runs inside the tkinter mainloop
def butterfly_behaviours(gravity):
    global food_exists, hunted
    global food

    # butterfly behaviours:
    for butterfly in butterflies:
        # update its location (move):
        butterfly.move()

        butterfly.avoid_wasps(wasps)

        # start wandering only if not hunted by a wasp:
        if not butterfly.hunted:
            butterfly.wandering(butterfly.w_radius, butterfly.w_distance)

        # avoid and bounce in borders:
        butterfly.boundaries()
        butterfly.bounce()
        # avoid obstacles:
        butterfly.bounce_obstacle1(obstacles)
        butterfly.avoid_obstacle(obstacles)

        # apply gravity (or other force):
        #if butterfly.killed:
        #    butterfly.apply_force(gravity)
        #    if butterfly.location.y == HEIGHT:
        #        # when butterfly falls down, disappear from canvas:
        #        butterflies.pop(butterflies.index(butterfly))
        #        butterfly.canvas.delete(butterfly.id)

        # butterflies avoid each other:
        butterfly.separate(butterflies)

        # if food exists go eat:
        if food_exists:
            butterfly.seek(food)

    # re-runs the method each REFRESH_TIME msec:
    canvas.after(REFRESH_TIME, butterfly_behaviours, gravity)

#------------------------------------------------------------------
# apply wasp behaviours/forces callback: using the after method it re-runs inside the tkinter mainloop
def wasp_behaviours(gravity):
    for wasp in wasps:
        # update location:
        wasp.move()
        # start wandering:
        wasp.wandering(wasp.w_radius, wasp.w_distance)
        # avoid and bounce in borders:
        wasp.boundaries()
        wasp.bounce()
        # avoid obstacles:
        wasp.bounce_obstacle1(obstacles)
        wasp.avoid_obstacle(obstacles)
        # wasps avoid each other:
        wasp.separate(wasps)
        # wasps chase butterflies:
        wasp.chase_butterflies(butterflies)

    # re-runs the method each REFRESH_TIME msec:
    canvas.after(REFRESH_TIME, wasp_behaviours, gravity)

#----------------------------------------------
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

#----------------------------------------------
# define left mouse button release callback: food stops
def left_button_release(event):
    # when left button released, butterfly stops seeking food location:
    global food_exists
    food_exists = False  # flag is down

# bind mouse left button release with callback routine:
canvas.bind('<ButtonRelease-1>', left_button_release)

#----------------------------------------------
# main event loop of tkinter:

butterfly_behaviours(gravity)
wasp_behaviours(gravity)

top_window.mainloop()