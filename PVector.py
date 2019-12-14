# definition of PVector class
from math import *

class PVector:
    def __init__(self, x, y):  # initiation of vector class
        self.x = x
        self.y = y

    def get_Magnitude(self):
        mag = sqrt(self.x*self.x + self.y*self.y)
        return mag

    def set_Magnitude(self, a):
        if a!=0:
            self.x = self.x*a/self.get_Magnitude()
            self.y = self.y * a / self.get_Magnitude()
        else:
            pass

    # adds vector v to self and replace:
    def Add(self, v):
        self.x = self.x + v.x
        self.y = self.y + v.y

    # subtracts vector v from self and puts the result in new vector
    def Sub(self, v):
        w = PVector(0, 0)  # create temporary vector
        w.x = self.x - v.x
        w.y = self.y - v.y
        return w

    # adds constant c to vector:
    def AddC(self, c):
        self.x = self.x + c
        self.y = self.y + c

    # multiplies vector by scalar a:
    def Mult(self, a):
        self.x = self.x * a
        self.y = self.y * a

    # vector divide returns a new vector as the result of the division by number a:
    def Div(self, a):
        v = PVector(0, 0)  # create temporary vector
        if a!=0:
            v.x = self.x/a
            v.y = self.y/a
        elif a==0:
            v.x = 999999
            v.y = 999999
        return v

    # copies vector to a new vector v:
    def Copy(self, v):
        v.x = self.x
        v.y = self.y

    # divides by the magnitude of the vector
    def Normalize(self):
        mag = self.get_Magnitude()
        if mag != 0:
            self.x = self.x/mag
            self.y = self.y/mag
        elif mag == 0:
            return

    def Limit(self, lim):
        if self.get_Magnitude() > lim:
            self.set_Magnitude(lim)

    def InnerProduct(self, v):
        a = self.x*v.x + self.y*v.y
        return a

    def heading2D(self):
        angle = atan2(-self.y, self.x)
        return -angle

    # finds the angle of two vectors:
    def angle_between(self, v):
        a = self.InnerProduct(v)
        mag_self = self.get_Magnitude()
        mag_v = v.get_Magnitude()
        if mag_self != 0 and mag_v != 0:
            cosangle = a/(mag_self * mag_v)
            return acos(cosangle)
        else:
            print("at least one vector length is 0")
            return 0

    # the distance between two vectors
    def distance(self, v):
        dist = sqrt(pow(abs(self.x - v.x), 2) + pow(abs(self.y - v.y), 2))
        return dist