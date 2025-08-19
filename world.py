from tkinter import *

# ------------------------------------------------------------------
# Create the main world window. Inputs: width, height and gravity. Outputs: top window, canvas and gravity vector
class World:
    def __init__(self, title, width, height):
        # create the main window using Tk:
        self.top_window = Tk()
        self.top_window.title(title)
        self.top_window.resizable(False, False)  # turn off resizing of the top window
        self.width = width
        self.height = height

        # create canvas to draw inside with the dimensions defined above:
        self.canvas = Canvas(self.top_window, width=self.width, height=self.height, bg="light blue")
        # packs the elements in the window:
        self.canvas.pack()

    # ------------------------------------------------------------------
    def create(self):
        # return both the top window and the canvas:
        return self.top_window, self.canvas


class Obstacle:
    def __init__(self, canvas, x, y, size_x, size_y, color):
        # x, y are the upper left corner of the rectangle, size_x, size_y are the side lengths
        self.id = id(self)  # object id
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.canvas = canvas
        self.ref = canvas.create_rectangle(self.x, self.y, self.x + self.size_x, self.y + self.size_y, fill=color, width=0)
