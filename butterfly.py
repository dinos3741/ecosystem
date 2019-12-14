from PVector import *
from random import *
from PIL import Image, ImageTk

class Butterfly:
    # Initialize and draw the butterfly. max speed is the maximum speed the butterfly can move:
    def __init__(self, canvas, max_speed, max_force, mass, w_radius, w_distance):
        self.canvas = canvas
        # get the canvas dimensions:
        self.canvas_width = int(self.canvas.cget("width"))
        self.canvas_height = int(self.canvas.cget("height"))

        # define the initial random location, velocity = 0 and acceleration = 0 of the butterfly:
        self.location = PVector(randrange(0, self.canvas_width), randrange(0, self.canvas_height))
        self.velocity = PVector(0, 0)
        self.acceleration = PVector(0, 0)
        self.max_speed = max_speed  # object's maximum speed
        self.max_force = max_force  # object's maximum force
        self.mass = mass
        self.w_radius = w_radius
        self.w_distance = w_distance

        self.hunted = False
        self.killed = False

        # open butterfly png file, resize it and draw it on the canvas using Pillow (ImageTk):
        image = Image.open('butterfly.png')
        RESIZE = 25
        im = image.resize((RESIZE, RESIZE))
        self.image = ImageTk.PhotoImage(im)
        # SOS: must save the image to a class variable because if not, it will collect garbage after the class is instantiated
        # (https://stackoverflow.com/questions/16424091/why-does-tkinter-image-not-show-up-if-created-in-a-function)
        self.id = self.canvas.create_image(self.location.x, self.location.y, image=self.image)

    # ------------------------------------------------------------------
    # methods to avoid the window boundaries: boundaries() and bounce()
    # boundaries is to avoid boundaries and turn
    def boundaries(self):
        DISTANCE_FROM_BORDER = 100  # the distance from the borders where it starts to change direction
        hits_boundary = False  # use a flag to avoid repeating the code for the steer force

        if self.location.x < DISTANCE_FROM_BORDER:  # close to left wall
            desired = PVector(self.max_speed, self.velocity.y)
            hits_boundary = True

        if self.location.x > self.canvas_width - DISTANCE_FROM_BORDER:  # close to right wall
            desired = PVector(-self.max_speed, self.velocity.y)
            hits_boundary = True

        if self.location.y < DISTANCE_FROM_BORDER:  # close to ceiling
            desired = PVector(self.velocity.x, self.max_speed)
            hits_boundary = True

        if self.location.y > self.canvas_height - DISTANCE_FROM_BORDER:  # close to floor
            desired = PVector(self.velocity.x, -self.max_speed)
            hits_boundary = True

        if hits_boundary == True:
            # Subtract the desired from the current velocity to create the steering force vector:
            steer = desired.Sub(self.velocity)  # steer = desired - current velocity
            # Limit the steering force depending on the vehicle max force and mass:
            steer.Limit(self.max_force)
            # finally apply the steering force:
            self.apply_force(steer)

    # ------------------------------------------------------------------
    # a simple bounce off the edges method: set velocity to reverse. Very important point: when the object hits
    # an edge, I first move it back with the amount of the distance it overshooted. Then I set its current position
    # to the one set. This way the simulation is realistic and the objects "stick" to the walls.
    def bounce(self):
        if self.location.x < 0:
            self.canvas.move(self.id, -self.location.x, 0)
            self.location.x = 0
            self.velocity.x *= 1

        if self.location.x > self.canvas_width:
            diff = self.location.x - self.canvas_width
            self.canvas.move(self.id, -diff, 0)
            self.location.x = self.canvas_width
            self.velocity.x *= -1

        if self.location.y < 0:
            self.canvas.move(self.id, 0, -self.location.y)
            self.location.y = 0
            self.velocity.y *= 1

        if self.location.y > self.canvas_height:
            diff = self.location.y - self.canvas_height
            self.canvas.move(self.id, 0, -diff)
            self.location.y = self.canvas_height
            self.velocity.y *= -1

    # ------------------------------------------------------------------
    # bounce off the obstacle after hitting:
    def bounce_obstacle(self, obstacles):
        for obstacle in obstacles:
            if obstacle.y < self.location.y < obstacle.y + obstacle.size_y:
                if obstacle.x < self.location.x < obstacle.x + obstacle.size_x:
                    self.velocity.x *= -1

            if obstacle.x < self.location.x < obstacle.x + obstacle.size_x:
                if obstacle.y < self.location.y < obstacle.y + obstacle.size_y:
                    self.velocity.y *= -1

    # new version of the bounce method implemented in the Obstacle class:
    # ------------------------------------------------------------------
    def bounce_obstacle1(self, obstacles):
        for obstacle in obstacles:
            obstacle.bounce(self)

    # ------------------------------------------------------------------
    # this is to try and avoid the obstacle by turning:
    def avoid_obstacle(self, obstacles):
        SAFE_DISTANCE = 100  # minimum distance before activating fleeing
        for obstacle in obstacles:
            if obstacle.x < self.location.x < obstacle.x + obstacle.size_x:
                distance1 = abs(self.location.y - obstacle.y)
                distance2 = abs(self.location.y - (obstacle.y + obstacle.size_y))
                if distance1 < SAFE_DISTANCE:
                    self.avoid_point(PVector(self.location.x, obstacle.y))
                if distance2 < SAFE_DISTANCE:
                    self.avoid_point(PVector(self.location.x, obstacle.y + obstacle.size_y))

            if obstacle.y < self.location.y < obstacle.y + obstacle.size_y:
                distance3 = abs(self.location.x - obstacle.x)
                distance4 = abs(self.location.x - (obstacle.x + obstacle.size_x))
                if distance3 < SAFE_DISTANCE:
                    self.avoid_point(PVector(obstacle.x, self.location.y))
                if distance4 < SAFE_DISTANCE:
                    self.avoid_point(PVector(obstacle.x + obstacle.size_x, self.location.y))

    # ------------------------------------------------------------------
    # avoid a PVector point
    def avoid_point(self, point):
        # create a vector to point away from the point:
        diff = self.location.Sub(point)
        diff.Normalize()
        diff.Mult(self.max_speed)

        # Subtract the desired from the current vectors to create the steering force vector:
        steer = diff.Sub(self.velocity)

        # Limit the steering force depending on the vehicle max force and mass:
        steer.Limit(self.max_force)
        # Finally apply the steering force:
        self.apply_force(steer)

    # ------------------------------------------------------------------
    # the move method updates the location based on the velocity by adding the two vectors, and moves the vehicle
    def move(self):
        # add acceleration to velocity:
        self.velocity.Add(self.acceleration)
        # limit top speed according to hunted or not:
        if self.hunted:
            self.velocity.Limit(self.max_speed * 1.2)
        else:
            self.velocity.Limit(self.max_speed)

        # add velocity to position:
        self.location.Add(self.velocity)
        # reset the acceleration at the end of each frame:
        self.acceleration.Mult(0)
        # move the image with the specific id by the pixels specified by the velocity:
        self.canvas.move(self.id, self.velocity.x, self.velocity.y)

    # ------------------------------------------------------------------
    # apply a force to the butterfly object:
    def apply_force(self, force):
        f = PVector(0, 0)
        force.Copy(f)  # copy force to temporary f
        f = force.Div(self.mass)
        self.acceleration.Add(f)

    # ------------------------------------------------------------------
    # Method to calculate and apply a steering force towards a target. It receives a target point and calculates
    # a steering force towards that target point
    def seek(self, target):
        CLOSE_ENOUGH = 100  # distance from target in order to detect arriving and stop

        # subtract the current location from the target location vector to find the desired direction vector:
        desired = target.Sub(self.location)  # desired vector = target position - current position

        distance = desired.get_Magnitude()  # this is how far the target is
        desired.Normalize()  # get the unit vector in the direction of the desired direction vector

        if distance < CLOSE_ENOUGH:  # if we arrive close to the target
            # limit with the max speed of the vehicle (if instead -max_speed, we have fleeing behaviour)
            desired.Mult(self.max_speed * distance / CLOSE_ENOUGH)
        else:
            desired.Mult(self.max_speed)

        # Subtract the desired from the current velocity to create the steering force vector:
        steer = desired.Sub(self.velocity)  # steer = desired - current velocity

        # Limit the steering force depending on the vehicle max force and mass:
        steer.Limit(self.max_force)

        # finally we apply the steering force:
        self.apply_force(steer)

    # ------------------------------------------------------------------
    # method to create a wandering path for the vehicle. Result is to calculate a target vector
    def wandering(self, radius, distance):
        wanderR = radius  # Radius for our "wander circle"
        wanderD = distance  # Distance from current location to the center of the "wander circle"
        change = 1  # we randomly chose an angle in radians: increasing this results in a more "jittery" movement
        wander_theta = random() * 2.0 * change - change   # Randomly change wander theta from -change to change

        # Now we have to calculate the new location to steer towards on the wander circle:
        circle_location = PVector(0, 0)  # initialize circleloc: this is the center of the circle
        self.velocity.Copy(circle_location)  # copy velocity to circleloc
        circle_location.Normalize()  # unit vector in direction of current velocity
        circle_location.Mult(wanderD)  # Multiply by distance
        circle_location.Add(self.location)  # now circleloc is the center of the circle, in the perimeter of which we move next
        heading = self.velocity.heading2D()  # We need to know the heading to offset wander_theta
        circleOffSet = PVector(wanderR * cos(wander_theta + heading), wanderR * sin(wander_theta + heading))
        circle_location.Add(circleOffSet)  # this is the target to feed the seek method
        # and now seek the new target:
        self.seek(circle_location)

    # ------------------------------------------------------------------
    # avoid falling into other butterflies:
    def separate(self, butterflies):
        SAFE_DISTANCE = 100  # minimum distance before activating fleeing
        for butterfly in butterflies:
            # calculate the distance between this vehicle and all other vehicles:
            distance = self.location.distance(butterfly.location)
            # if distance from specific butterfly is less than safe:
            if 0 < distance < SAFE_DISTANCE:
                self.avoid_point(butterfly.location)  # avoid this butterfly

    # ------------------------------------------------------------------
    #  avoid every wasp:
    def avoid_wasps(self, wasps):
        SAFE_DISTANCE = 100
        if len(wasps) > 0:
            for wasp in wasps:
                if self.location.distance(wasp.location) < SAFE_DISTANCE:
                    # butterfly raises the hunted flag:
                    self.hunted = True
                    self.avoid_point(wasp.location)
                else:
                    self.hunted = False
