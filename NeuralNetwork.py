import numpy as np

# the three-layer fully connected Neural Network class:
# ------------------------------------------------------------------
class NeuralNetwork:
    # hidden layer matrix: H = σ(W_ih * I + B_h), output matrix: O = σ(W_ho * H + B_o)
    # B is the bias matrix, all elements are 1.
    def __init__(self, nr_inputs, nr_hidden, nr_outputs, learning_rate):
        # number of elements in each of the layers:
        self.nr_inputs = nr_inputs
        self.nr_hidden = nr_hidden
        self.nr_outputs = nr_outputs
        self.learning_rate = learning_rate

        # create the input-hidden and hidden-output weight matrices. Initialize as random values
        # in the uniform interval [-1, 1]. In () is the matrix shape
        # nr of columns in the weight matrix = nr of input nodes
        self.weights_IH = np.random.random((self.nr_hidden, self.nr_inputs)) * 2 - 1
        # nr or rows in the weight matrix = nr of hidden nodes
        self.weights_HO = np.random.random((self.nr_outputs, self.nr_hidden)) * 2 - 1

        # create the bias matrices for the hidden and output layers with random values [-1, 1]:
        self.bias_H = np.random.random(self.nr_hidden) * 2 - 1
        self.bias_H = self.bias_H.reshape(self.nr_hidden, 1)  # reshape as a nr_hidden x 1 matrix
        self.bias_O = np.random.random(self.nr_outputs) * 2 - 1
        self.bias_O = self.bias_O.reshape(self.nr_outputs, 1)  # reshape as a nr_outputs x 1 matrix


    # create the sigmoid function and its derivative:
    # ------------------------------------------------------------------
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))


    def d_sigmoid(self, y):
        # return self.sigmoid(x) * (1 - self.sigmoid(x))
        return y * (1 - y)


    # ------------------------------------------------------------------
    # feed-forward process (assuming that we have normalized the inputs to the 0-1 space)
    # calculate the hidden layer nodes: H = σ(W_ih * I + B_h)
    def predict(self, inputs):
        # convert inputs to vector np array:
        inputs = np.array(inputs).reshape(self.nr_inputs, 1)

        # compute hidden nodes as W_ih * I:
        hidden = np.matmul(self.weights_IH, inputs)

        # now add the bias of the hidden layer (+ B_h):
        hidden = np.add(hidden, self.bias_H)
        # now we pass it from the sigmoid activation function:
        hidden = self.sigmoid(hidden)

        # now the hidden nodes are multiplied with the HO weights to create the output nodes: O = σ(W_ho * H + B_o)
        output_nodes = np.matmul(self.weights_HO, hidden)

        # now add the bias of the output layer (+ B_o):
        output_b = np.add(output_nodes, self.bias_O)

        # finally we pass it from the sigmoid activation function:
        output = self.sigmoid(output_b)

        # return the output:
        return output

    # ------------------------------------------------------------------
    # back-propagation algorithm to train the NN weights: we need to propagate the error between the NN output and the
    # target output to adjust all the weights for both hidden and input layers.
    #
    def train(self, inputs, targets):
        # convert inputs and targets to np vector arrays:
        inputs = np.array(inputs).reshape(self.nr_inputs, 1)
        targets = np.array(targets).reshape(self.nr_outputs, 1)

        # feed forward the specific input and calculate the output:
        outputs = self.predict(inputs)

        # calculate the output layer error: target - output
        output_errors = np.subtract(targets, outputs)

        # now we need to calculate the hidden layer error: they are the proportions of the weights for each
        # output error from each hidden node. We calculate by transposing the W_ho and multiplying with the
        # output errors we just calculated:
        weights_HO_transposed = np.transpose(self.weights_HO)
        hidden_errors = np.matmul(weights_HO_transposed, output_errors)

        # now we apply gradient descent in order to update the weights and bias for every input sample:
        # total cost function = Sum(guess - y)^2, to minimize this we set the partial derivative for m equal to 0:
        # guess = mx + b, partial derivative for m = 2 * error * d(error)/dm = 2 * error * input. This means that
        # a small change in m (Δm) will cause a change in the cost function in the direction of zero. So we need to
        # update m by the amount of error * input * learning rate (LR is used to make the changes more robust).
        # Equivalent for b: Δb = error * lr
        # the equivalent for matrix is: ΔW_ho = lr * E_o * O*(1-O) (*) H_trans , and ΔW_ih = lr * E_h  H*(1-H) (*) I_trans
        # Δbias_O = lr * E_o * O*(1-O), Δbias_I = lr * E_h  H*(1-H)

        # output layer:
        # calculate the derivative of the sigmoid: the output is already passed through the sigmoid:
        grad = self.d_sigmoid(outputs)
        # now multiply element-wise with the output errors:
        grad = np.multiply(grad, output_errors)
        # now multiply with the learning rate:
        grad *= self.learning_rate

        # Calculate output weight deltas: first compute (again) and transpose the hidden layer outputs:
        # compute hidden nodes as W_ih * I:
        hidden_nodes = np.matmul(self.weights_IH, inputs)
        # now add the bias of the hidden layer (+ B_h):
        hidden_b = np.add(hidden_nodes, self.bias_H)

        # now we pass it from the sigmoid activation function:
        hidden = self.sigmoid(hidden_b)

        # compute the transposed matrix:
        hidden_T = np.transpose(hidden)
        # now compute the delta weights:
        weights_HO_delta = np.matmul(grad, hidden_T)
        # finally update the H->O weights:
        self.weights_HO = np.add(self.weights_HO, weights_HO_delta)

        # hidden layer:
        # calculate gradient of the hidden layer as the hidden vector passed through the sigmoid derivative:
        grad_h = self.d_sigmoid(hidden)
        # now multiply element-wise with the hidden errors:
        grad_h = np.multiply(grad_h, hidden_errors)
        # now multiply with the learning rate:
        grad_h = grad_h * self.learning_rate

        # calculate hidden weight deltas: transpose input layer inputs:
        input_T = np.transpose(inputs)
        # now compute the input delta weights:
        weights_IH_delta = np.matmul(grad_h, input_T)
        # finally update the I->H weights:
        self.weights_IH = np.add(self.weights_IH, weights_IH_delta)

        # adjust the output and hidden bias by the deltas (grad3 and grad3_h:
        self.bias_O = np.add(self.bias_O, grad)
        self.bias_H = np.add(self.bias_H, grad_h)
