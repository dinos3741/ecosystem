import numpy as np
from PIL import Image, ImageTk
import random as rand
from Perceptron import *
from NeuralNetwork import *


class Butterfly:
    # Initialize and draw the butterfly. max speed is the maximum speed the butterfly can move:
    def __init__(self, canvas, max_speed, max_force, max_mass):
        self.canvas = canvas
        # get the canvas dimensions:
        self.canvas_width = int(self.canvas.cget("width"))
        self.canvas_height = int(self.canvas.cget("height"))

        # define the initial random location. Also velocity = 0 and acceleration = 0 of the butterfly:
        self.location = PVector(randrange(0, self.canvas_width), randrange(0, self.canvas_height))
        #self.location = PVector(self.canvas_width/2, self.canvas_height/2)
        self.velocity = PVector(0, 0)
        self.acceleration = PVector(0, 0)
        self.max_speed = max_speed
        self.max_force = max_force
        self.mass = max_mass
        self.wander_theta = 0  # initial angle for wander method

        # open butterfly png file, resize it and draw it on the canvas using Pillow (ImageTk):
        # Note: I must save the image to a class variable, because if not, it will collect garbage after the class is
        # instantiated:
        # (https://stackoverflow.com/questions/16424091/why-does-tkinter-image-not-show-up-if-created-in-a-function)
        image = Image.open('butterfly.png')
        SIZE = int(self.mass * 10)  # size equivalent to mass
        im = image.resize((SIZE, SIZE))
        self.image = ImageTk.PhotoImage(im)
        self.id = self.canvas.create_image(self.location.x, self.location.y, image=self.image)

        #---- perceptron engine data -----
        nr_forces = 8  # 3 is the minimum nr of forces to be equally spaced around the circle. More forces: smaller radius
        # learning rate 0.2-0.3 is a nice balance between speed of convergence and accuracy
        self.brain = Perceptron(nr_forces, 0.01)
        # list of all forces applied to the butterfly
        self.forces = []
        # equally space them around the butterfly to steer:
        for i in range(nr_forces):
            force = PVector(self.max_force, 0)  # the larger the force, the smaller the orbit rotation they create
            force.Rotate(2 * pi * i / nr_forces)
            self.forces.append(force)


        


    # ------------------------------------------------------------------
    # boundaries method is used to avoid ecosystem boundaries and turn
    def boundaries(self):
        DISTANCE_FROM_BORDER = 100  # the distance from the borders where it starts to change direction
        # desired velocity is a vector from current location until target: target - location, but in this case
        # it's a vector opposite to the x-coordinate
        if self.location.x < DISTANCE_FROM_BORDER:  # close to left wall
            desired = PVector(self.max_speed, self.velocity.y)
        elif self.location.x > self.canvas_width - DISTANCE_FROM_BORDER:  # close to right wall
            desired = PVector(-self.max_speed, self.velocity.y)
        elif self.location.y < DISTANCE_FROM_BORDER:  # close to ceiling
            desired = PVector(self.velocity.x, self.max_speed)
        elif self.location.y > self.canvas_height - DISTANCE_FROM_BORDER:  # close to floor
            desired = PVector(self.velocity.x, -self.max_speed)
        else:
            desired = PVector(0, 0)

        if desired.get_Magnitude() != 0:  # if desired has an assigned value from above:
            # Subtract the desired from the current velocity to create the steering force vector:
            steer = desired.Sub(self.velocity)  # steer = desired - current velocity
            # Limit the steering force depending on the vehicle max force and mass:
            steer.Limit(self.max_force*2)  # 100% more force when bouncing
        else:
            steer = PVector(0, 0)

        # finally apply the steering force:
        self.apply_force(steer)

    # ------------------------------------------------------------------
    # a simple bounce off the edges method: set velocity to reverse in all cases
    def bounce(self):
        radius = int(self.mass * 10) / 2  # The radius is half the image size
        if self.location.x < radius:
            self.velocity.x *= -1
            self.location.set(radius, int(self.location.y))

        if self.location.x > self.canvas_width - radius:
            self.velocity.x *= -1
            self.location.set(self.canvas_width - radius, int(self.location.y))

        if self.location.y < radius:
            self.velocity.y *= -1
            self.location.set(int(self.location.x), radius)

        if self.location.y > self.canvas_height - radius:
            self.velocity.y *= -1
            self.location.set(int(self.location.x), self.canvas_height - radius)

    # ------------------------------------------------------------------
    # avoid obstacles by turning
    def avoid_obstacle(self, obstacle):
        d_max = 100

        # if approaching left side:
        if abs(self.location.x - obstacle.x) < d_max and obstacle.y < self.location.y < obstacle.y + obstacle.size_y:
            desired = PVector(-self.max_speed, self.velocity.y)

        # if approaching right side:
        elif abs(self.location.x - (obstacle.x + obstacle.size_x)) < d_max and obstacle.y < self.location.y < obstacle.y + obstacle.size_y:
            desired = PVector(self.max_speed, self.velocity.y)

        # if approaching top side:
        elif abs(self.location.y - obstacle.y) < d_max and obstacle.x < self.location.x < obstacle.x + obstacle.size_x:
            desired = PVector(self.velocity.x, -self.max_speed)

        # if approaching bottom side:
        elif abs(self.location.y - (obstacle.y + obstacle.size_y)) < d_max and obstacle.x < self.location.x < obstacle.x + obstacle.size_x:
            desired = PVector(self.velocity.x, self.max_speed)

        else:
            desired = PVector(0, 0)

        if desired.get_Magnitude() != 0:
            steer = desired.Sub(self.velocity)  # steer = desired - current velocity
            steer.Normalize()
            steer.Mult(self.max_force*1.5)
        else:
            steer = PVector(0, 0)

        self.apply_force(steer)


    # ------------------------------------------------------------------
    # bounce from obstacle: calculate the absolute value as distance from the x and y of the obstacle
    def bounce_from_obstacle(self, obstacle):
        space = 5  # nr of pixels from borders so they don't get inside the obstacle
        if abs(self.location.x - obstacle.x) <= space and obstacle.y <= self.location.y <= obstacle.y + obstacle.size_y:
            self.velocity.x *= -1

        if abs(self.location.x - (obstacle.x + obstacle.size_x)) <= space and obstacle.y <= self.location.y <= obstacle.y + obstacle.size_y:
            self.velocity.x *= -1

        if abs(self.location.y - obstacle.y) <= space and obstacle.x <= self.location.x <= obstacle.x + obstacle.size_x:
            self.velocity.y *= -1

        if abs(self.location.y - (obstacle.y + obstacle.size_y)) <= space and obstacle.x <= self.location.x <= obstacle.x + obstacle.size_x:
            self.velocity.y *= -1

# ------------------------------------------------------------------
    # the move method updates the location based on the velocity by adding the two vectors, and moves the object
    def move(self):
        # add acceleration to velocity:
        self.velocity.Add(self.acceleration)
        # limit maximum velocity
        self.velocity.Limit(self.max_speed)
        # add velocity to position:
        self.location.Add(self.velocity)
        # reset the acceleration at the end of each frame:
        self.acceleration.Mult(0)
        # update the position of the image with the specific id by the pixels specified by the velocity:
        self.canvas.move(self.id, self.velocity.x, self.velocity.y)


    # ------------------------------------------------------------------
    # apply a force to the butterfly object:
    def apply_force(self, force):
        f = PVector(0, 0)
        force.Copy(f)  # copy force to temporary f
        f = force.Div(self.mass)
        self.acceleration.Add(f)  # update the acceleration vector

    # ------------------------------------------------------------------
    # Method to calculate and apply a steering force towards a target. It receives a target point and calculates
    # a steering force towards that target point
    def seek(self, target, direction):
        CLOSE_ENOUGH = 50  # distance from target in order to detect arriving and stop - more than 30 looks unnatural

        # subtract the current location from the target location vector to find the desired direction vector:
        desired = target.Sub(self.location)  # desired velocity = target position - current position

        distance = desired.get_Magnitude()  # this is how far the target is
        desired.Normalize()  # get the unit vector in the direction of the desired vector

        # to use also to avoid a point - reverse:
        if direction == 'avoid':
            self.max_speed *= -1

        if distance < CLOSE_ENOUGH:  # if we arrive close to the target
            # limit with the max speed of the vehicle (if instead -max_speed, we have fleeing behaviour)
            desired.Mult(self.max_speed * distance / CLOSE_ENOUGH)
        else:
            desired.Mult(self.max_speed)

        # Subtract the desired from the current velocity to create the steering force vector:
        steer = desired.Sub(self.velocity)  # steering force = desired vector - current velocity

        # Limit the steering force depending on the vehicle max force:
        steer.Limit(self.max_force)

        # finally apply the steering force:
        self.apply_force(steer)


# ------------------------------------------------------------------
    # method to create a wandering path for the vehicle. Result is to calculate a target vector
    def wander(self):
        # values of diameter and radius should be almost equal for natural motion
        wanderR = 30  # Radius of wander circle: smaller = more straight movement. Natural movement: (~30)
        wanderD = 50  # Distance from current location to center of the wander circle: bigger = less jitter (~50)
        change = 0.3  # random angle in radians: increase results in more jittery movement (~0.3)
        self.wander_theta += rand.uniform(-change, change)   # Add new random wander theta from -change to change rads

        # Now we have to calculate the new location to steer towards on the wander circle:
        circle_location = PVector(self.velocity.x, self.velocity.y)  # copy velocity to circle location (center of circle)
        circle_location.Normalize()  # create unit vector in direction of current velocity
        circle_location.Mult(wanderD)  # Multiply by distance: move wanderD pixels at the direction of current velocity
        circle_location.Add(self.location)  # now circleloc is the center of the circle, in the perimeter of which we move next
        heading = self.velocity.heading2D()  # We need to know the heading to offset wander_theta
        circleOffSet = PVector(wanderR * cos(self.wander_theta + heading), wanderR * sin(self.wander_theta + heading))
        circle_location.Add(circleOffSet)  # this is the target to feed the seek method

        # I can either use Reynold's method to seek the target, or use the perceptron. Perceptron is slower
        # but I think gives more realistic result:
        #self.apply_perceptron(circle_location)

        # Raynold's seek method to reach the target:
        self.seek(circle_location, 'search')

    # ------------------------------------------------------------------
    # avoid falling into other butterflies:
    def separate(self, butterflies):
        separation_distance = 80  # the desired separation distance before activating
        sum = PVector(0, 0)  # the sum of all vectors of butterflies closer than desired distance
        count = 0  # counter of all vectors of butterflies closer than desired distance
        for butterfly in butterflies:
            # calculate the distance between this vehicle and all other vehicles:
            distance = self.location.Distance(butterfly.location)
            # if distance from specific butterfly is less than desired and more than 0 (so not itself):
            if 0 < distance < separation_distance:
                # calculate difference vector
                diff = self.location.Sub(butterfly.location)
                sum.Add(diff)  # add to the sum
                count += 1  # increase counter by one
        # after the loop, in case at least one is closer than desired distance, calculate average vector:
        if count > 0:
            sum.set_Magnitude(self.max_speed)  # set it to max speed
            steer = sum.Sub(self.velocity)  # steer is now the desired (sum) minus the current velocity
            steer.Limit(self.max_force)
            self.apply_force(steer)

    # ------------------------------------------------------------------
    # control position based on an array of forces weighted by a perceptron NN
    def apply_perceptron(self, target):
        # predict the output force from the perceptron:
        brain_result = self.brain.feed_forward(self.forces)
        # apply the resulting force from the perceptron and move the vehicle:
        self.apply_force(brain_result)
        # calculate error from current location to target:
        error = target.Sub(self.location)
        # re-adjust the weights according to the error:
        self.brain.train(self.forces, error)


    # ------------------------------------------------------------------
    # control position based on an array of forces weighted by the fully connected NN
    def apply_NN(self, target):
        # predict the output force from the NN:
        training_data = []
        training_data.append(self.location.x)
        training_data.append(self.location.y)  # append x and y location coordinates in simple array
        result = self.nn.predict(training_data)
        result = result.reshape(2,)  # convert into 1-dimensional array
        # apply the resulting force from the perceptron and move the vehicle:
        self.apply_force(PVector(result[0], result[1]))
        # calculate error from current location to target:
        #error = target.Sub(self.location)
        #error_array = [error.x/self.canvas_width, error.y/self.canvas_height]
        target_array = [target.x/self.canvas_width, target.y/self.canvas_height]
        # re-adjust the weights according to the error:
        self.nn.train(training_data, target_array)

        # I want the NN to make a decision based on the training dataset: input is location x & y,
        # make a method "train_NN" that gets called in the move method, and for each frame it collects
        # data from the butterfly position vector, and it outputs a "go/avoid" flag
        # the boundaries method will not run, and instead it will run around bouncing on walls and everytime it hits
        # a wall it will learn that position with a avoid flag. When the food source is behind an obstacle,
        # it will avoid it
        # inputs are distances from any object around it (5 directions). Output should be a point to seek
        # in a specific angle from the current velocity vector.
        # Error should be calculated if it hits a wall: