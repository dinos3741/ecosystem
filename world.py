import random
from random import randrange
from tkinter import *
from PVector import *

# Create the main world window. Inputs: width, height and gravity. Outputs: top window, canvas and gravity vector
class World:
    def __init__(self, title, width, height, gravity, obstacles):
        # create the main window using Tk:
        self.top_window = Tk()
        self.top_window.title(title)
        self.top_window.resizable(False, False)  # turn off resizing of the top window
        self.width = width
        self.height = height

        # create canvas to draw inside with the dimensions defined above:
        self.canvas = Canvas(self.top_window, width=width, height=height, bg="light blue")
        # packs the elements in the window:
        self.canvas.pack()

        # create gravity vector:
        self.gravity = PVector(0, gravity)

        # create some random obstacles:
        self.obstacles = self.create_obstacles(obstacles)

    def create(self):
        # return both the top window and the canvas:
        return self.top_window, self.canvas, self.gravity, self.obstacles

    # create a number of random obstacles that do not overlap:
    def create_obstacles(self, number):
        # create an empty list of obstacles:
        obstacles = []
        # while list length less than desired:
        while len(obstacles) < number:
            overlapped = False
            # create temporary obstacle:
            new = Obstacle(self.canvas, randrange(0, self.width), randrange(0, self.height), randrange(10, 200),
                           randrange(10, 200), random.choice(['blue', 'red', 'green', 'grey', 'purple', 'beige']))
            # if list is empty, add new object as first:
            if len(obstacles) == 0:
                obstacles.append(new)
            # otherwise, if list has at least one item, check the new against all existing ones for overlap:
            else:
                for obstacle in obstacles:
                    if obstacle.overlap(new) or new.overlap(obstacle):
                        # if at least one overlap found, raise flag:
                        overlapped = True

                # after all iterations, if no flag raised, this means we are OK and I add item to the list:
                if not overlapped:
                    obstacles.append(new)
                    print("created obstacle")
                else:
                    # delete temporary object and remove from canvas so does not display:
                    new.delete(self.canvas)
                    del new

        # returns the list of obstacles:
        return obstacles

#------------------------------------------------------------------
# This is a template class to make various rectangles.
class Obstacle:
    def __init__(self, canvas, x, y, size_x, size_y, color):
        # a, b are the dimensions of the rectangle center, SIZE is the side length
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.canvas = canvas
        self.ref = canvas.create_rectangle(self.x, self.y, self.x + self.size_x, self.y + self.size_y, fill=color, width=0)

    # method to check if an object (butterfly, wasp etc) hits any border of the obstacle. Very important point: when
    # the object hits an edge, I first move it back with the amount of the distance it overshooted. Then I set its current
    # position to the one set. This way the simulation is realistic and the objects "stick" to the walls.
    def bounce(self, object):
        OFFSET = 5 # offset from touching the obstacle
        # left vertical side:
        if abs(object.location.x - self.x) < OFFSET and self.y < object.location.y < self.y + self.size_y:
            # calculate difference of offset:
            diff = object.location.x - self.x
            # reverse velocity of x:
            object.velocity.x *= -1
            # set location right on the side:
            object.location.x = self.x
            # move the object on the side:
            self.canvas.move(object.id, -diff, 0)

        # right vertical side:
        if abs(object.location.x - (self.x + self.size_x)) < OFFSET and self.y < object.location.y < self.y + self.size_y:
            # calculate difference of offset:
            diff = self.x + self.size_x - object.location.x
            # reverse velocity of x:
            object.velocity.x *= -1
            # set location right on the side:
            object.location.x = self.x + self.size_x
            # move the object on the side:
            self.canvas.move(object.id, -diff, 0)

        # top horizontal side:
        if abs(object.location.y - self.y) < OFFSET and self.x < object.location.x < self.x + self.size_x:
            # calculate difference of offset:
            diff = object.location.y - self.y
            # reverse velocity of y:
            object.velocity.y *= -1
            # set location right on the side:
            object.location.y = self.y
            # move the object on the side:
            self.canvas.move(object.id, 0, -diff)

        # bottom horizontal side:
        if abs(object.location.y - (self.y + self.size_y)) < OFFSET and self.x < object.location.x < self.x + self.size_x:
            # calculate difference of offset:
            diff = self.y + self.size_y - object.location.y
            # reverse velocity of y:
            object.velocity.y *= -1
            # set location right on the side:
            object.location.y = self.y + self.size_y
            # move the object on the side:
            self.canvas.move(object.id, 0, -diff)

    # method to check if this obstacle overlaps with another:
    def overlap(self, obstacle):
        horizontal_overlap = False
        vertical_overlap = False
        # horizontal overlap:
        if self.x + self.size_x > obstacle.x:
            horizontal_overlap = True
        # vertical overlap:
        if self.y + self.size_y > obstacle.y:
            vertical_overlap = True
        if horizontal_overlap and vertical_overlap:
            return True
        else:
            return False

    def delete(self, canvas):
        canvas.delete(self.ref)




