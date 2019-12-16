from butterfly import *
import numpy as np
from sklearn.cluster import KMeans

# Wasp inherits all Butterfly methods
class Wasp(Butterfly):
    # Initialize and draw the wasp. max speed is the maximum speed the wasp can move:
    def __init__(self, canvas, max_speed, max_force, mass, w_radius, w_distance):
        self.canvas = canvas
        # get the canvas dimensions:
        self.canvas_width = int(self.canvas.cget("width"))
        self.canvas_height = int(self.canvas.cget("height"))

        # define the initial random location, velocity = 0 and acceleration = 0 of the wasp:
        self.location = PVector(randrange(0, self.canvas_width), randrange(0, self.canvas_height))
        self.velocity = PVector(0, 0)
        self.acceleration = PVector(0, 0)
        self.max_speed = max_speed  # object's maximum speed
        self.max_force = max_force  # object's maximum force
        self.mass = mass
        self.w_radius = w_radius
        self.w_distance = w_distance

        # open wasp png file, resize it and draw it on the canvas using Pillow (ImageTk):
        image = Image.open('wasp.png')
        RESIZE = 30
        im = image.resize((RESIZE, RESIZE))
        self.image = ImageTk.PhotoImage(im)
        self.id = self.canvas.create_image(self.location.x, self.location.y, image=self.image)

    # ------------------------------------------------------------------
    # the move method updates the location based on the velocity by adding the two vectors, and moves the vehicle
    def move(self):
        # add acceleration to velocity:
        self.velocity.Add(self.acceleration)
        # limit top speed:
        self.velocity.Limit(self.max_speed)
        # add velocity to position:
        self.location.Add(self.velocity)
        # reset the acceleration at the end of each frame:
        self.acceleration.Mult(0)
        # move the image with the specific id by the pixels specified by the velocity:
        self.canvas.move(self.id, self.velocity.x, self.velocity.y)

    # ------------------------------------------------------------------
    # Method to calculate and apply a steering force towards a target. It receives a target point and calculates
    # a steering force towards that target point. SOS: this is different than the seek of the butterfly, because
    # wasp should not have arriving behaviour when closing in to a butterfly!
    def seek(self, target):
        # subtract the current location from the target location vector to find the desired direction vector:
        desired = target.Sub(self.location)  # desired vector = target position - current position

        distance = desired.get_Magnitude()  # this is how far the target is
        desired.Normalize()  # get the unit vector in the direction of the desired direction vector

        desired.Mult(self.max_speed)

        # Subtract the desired from the current velocity to create the steering force vector:
        steer = desired.Sub(self.velocity)  # steer = desired - current velocity

        # Limit the steering force depending on the vehicle max force and mass:
        steer.Limit(self.max_force)

        # finally we apply the steering force:
        self.apply_force(steer)

    # ------------------------------------------------------------------
    def chase_butterflies(self, butterflies):
        distance_list = []  # create a list of distances from wasp to all butterflies
        if len(butterflies) > 0:
            for butterfly in butterflies:
                distance = self.location.distance(butterfly.location)
                distance_list.append(distance)
                # find the nearest butterfly: sort the distance list. sorted gives a new sorted list, enumerate gives
                # a tuple with first item the index and second the value, we sort by the value, and create a new list
                # with the first, ie the index. Then we chose the first item, i.e. the minimum:
                min_index = [i[0] for i in sorted(enumerate(distance_list), key=lambda x: x[1])][0]
                self.seek(butterflies[min_index].location)

                # if butterfly reached, kill it and remove from list:
                if self.location.distance(butterfly.location) < 5:
                    butterfly.killed = True
                    butterflies.pop(butterflies.index(butterfly))
                    butterfly.canvas.delete(butterfly.id)

    # ------------------------------------------------------------------
    # method to classify butterfly groups in two and go towards the closest
    def cluster_butterflies(self, butterflies):
        # I will classify the butterflies to two groups, and chase the closest.
        # slow if I do in every frame, but every ten frames perhaps? I can make another routine in main
        # with a different timer (100 ms) that runs a different set of routines.
        x_dimension = []
        y_dimension = []
        for butterfly in butterflies:
            x_dimension.append(butterfly.location.x)
            y_dimension.append(butterfly.location.y)
        data = np.column_stack((x_dimension, y_dimension))
        #
        k_means = KMeans(n_clusters=2, max_iter=50)
        k_means.fit(data)
        distance11 = self.location.distance(PVector(k_means.cluster_centers_[0][0], k_means.cluster_centers_[0][1]))
        distance12 = self.location.distance(PVector(k_means.cluster_centers_[1][0], k_means.cluster_centers_[1][1]))
        if distance11 < distance12:
            self.seek(PVector(k_means.cluster_centers_[0][0], k_means.cluster_centers_[0][1]))
        else:
            self.seek(PVector(k_means.cluster_centers_[1][0], k_means.cluster_centers_[1][1]))



