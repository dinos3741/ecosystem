from pygame.math import Vector2
from random import *

# ------------------------------------------------------------------
# The perceptron class (one neuron to classify butterfly behaviour)
class Perceptron:
    def __init__(self, nr_inputs, learning_rate):
        self.weights = []  # weights belong to the perceptron instance
        self.c = learning_rate
        # initialize the weights with random values from 0 to 1: 
        for i in range(nr_inputs):
            self.weights.append(random())


    def feed_forward(self, forces):
        sum_vec = Vector2(0, 0)  # initialize sum of all forces
        # for all forces, multiply with weight and add:
        for i in range(len(forces)):
            sum_vec += forces[i] * self.weights[i]  # Use operator overloading

        # return the total vector force without activation function
        return sum_vec


    # update the weights according to the error noticed (back-propagation):
    def train(self, forces, error):
        for i in range(len(self.weights)):  # Dw = input * error, weight update: weight = weight + Dw
            self.weights[i] += self.c * error.x * forces[i].x
            self.weights[i] += self.c * error.y * forces[i].y
            # force the weights to be in the [0..1] range:
            if self.weights[i] > 1:
                self.weights[i] = 1
            elif self.weights[i] < 0:
                self.weights[i] = 0