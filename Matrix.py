# a library class to perform basic matrix operations to use in the NN class

class Matrix:
    # create new matrix of rows x columns and initialize to 0:
    def __init__(self, rows, columns, fill):
        self.rows = rows
        self.columns = columns
        self.matrix = [[fill] * self.columns for i in range(self.rows)]


    # scalar addition
    def scale(self, a):
        for i in range(self.rows):
            for j in range(self.columns):
                self.matrix[i][j] += a

    # scalar multiplication
    def multiply(self, a):
        for i in range(self.rows):
            for j in range(self.columns):
                self.matrix[i][j] *= a
