from matplotlib import pyplot as plt
import numpy as np
import HelpFuncs as hf


def sigma(z):
    return 1.0 / (1.0 + np.exp(-z))


def radial_basis(z):
    return np.exp((-z) ** 2)


def tang(z):
    tmp = (np.exp(z)-np.exp(-z))/(np.exp(z)+np.exp(-z))
    return tmp


def linear(z):
    return z


def log(z):
    return np.log(z)


def sin(z):
    return np.sin(z)


def sign(z):
    return np.sign(z)


class Network(object):

    poss_active_func = [tang, linear, log, sigma, sign, sin]

    def check_valid(*args):
        for el in args:
            if el == -1:
                return False
        return True

    def __init__(self, sizes):
        self.weights = None
        self.active_layers_func = None
        # сам список слоев с кол-вом нейронов
        self.sizes = sizes

    def set_random_weights(self):
        # список с матрицами весов.
        # По строкам нейроны, в которые входят синапсы, а по столбцам нейроны, которые пускают сигнал
        # Каждая матрица расширена на один столбец для коэффициентов смещения.
        # Также веса настраиваются только для внутренних слоев.
        # Входной и выходной слой мы не трогаем пока
        if len(self.sizes) > 2:

            self.weights = [np.random.randn(y, x + 1) for x, y in zip(self.sizes[:-1], self.sizes[1:])]
        else:
            self.weights = [np.random.randn(self.sizes[1], self.sizes[0])]
        # каждому слою зададим дефолтное значение функции активации
        self.active_layers_func = [self.poss_active_func[0] for _ in self.sizes]

    def feed_forward(self, a):
        add = True if len(self.weights) >= 2 else False
        for i, w in enumerate(self.weights):
            if add:
                a = np.append(a, [[1]], axis=0)
            a = self.active_layers_func[i](np.dot(w, a))
        return a

    def set_layer_in_interval(self, value):
        tmp = value % len(self.sizes)
        if len(self.sizes) == 2 or tmp == 0 or tmp == len(self.sizes)-1:
            tmp = -1
        return tmp

    def add_layer(self, position, neurons):
        mod_position = self.set_layer_in_interval(position)
        if self.check_valid(mod_position):
            self.sizes.insert(mod_position, neurons)

    def remove_layer(self, position):
        mod_position = self.set_layer_in_interval(position)
        if self.check_valid(mod_position):
            self.sizes.pop(mod_position)

    def add_neurons(self, position, neurons):
        mod_position = self.set_layer_in_interval(position)
        if self.check_valid(mod_position):
            self.sizes[mod_position] += neurons

    def remove_neurons(self, position, neurons):
        mod_position = self.set_layer_in_interval(position)
        if self.check_valid(mod_position):
            self.sizes[mod_position] -= neurons
            if self.sizes[mod_position] <= 0:
                self.remove_layer(mod_position)

    # меняем функцию активации для слоя
    def change_active_func(self, position, func_num):
        mod_position = self.set_layer_in_interval(position)
        if self.check_valid(position):
            self.active_layers_func[mod_position] = self.poss_active_func[func_num]

    def get_params_count(self):
        return sum(map(lambda matrix: matrix.size, self.weights))

    def prepare_weights(self):
        self.set_random_weights()

    def set_weights(self, phenotype):
        j = 0
        for i in range(len(self.weights)):
            for row in range(len(self.weights[i])):
                for col in range(len(self.weights[i][row])):
                    self.weights[i][row][col] = phenotype[j]
                    j += 1
        return phenotype

    def get_weights(self):
        weights = []
        for i in range(len(self.weights)):
            for row in range(len(self.weights[i])):
                for col in range(len(self.weights[i][row])):
                    weights.append(self.weights[i][row][col])
        return weights

    def set_weights_from_file(self, matrix_w):
        for matrix_i in range(len(self.weights)):
            input_matrix = matrix_w[matrix_i][1:-1]
            input_matrix_rows_array = input_matrix.split(';')
            for row_i in range(len(self.weights[matrix_i])):
                input_row = [float(elem) for elem in input_matrix_rows_array[row_i].split(',')]
                for col_i in range(len(self.weights[matrix_i][row_i])):
                    self.weights[matrix_i][row_i][col_i] = input_row[col_i]

    def plot(self):
        time = 20
        t = np.arange(0, time, 0.1)
        nu = [
            [-8, -4, 0], [-10, -4, 0], [-8, -5, 0],
            [8, -4, 0], [10, -4, 0], [-8, -5, 0],
            [-8, 4, 0], [-10, 4, 0], [-8, 5, 0],
            [8, 4, 0], [10, 4, 0], [8, 5, 0],
        ]
        glob_x = []
        glob_y = []
        glob_tetas = []
        for y0 in nu:
            res = hf.ode45(self, hf.system, t, y0, 0.1)
            xs = [y0[0]] + res[0]
            ys = [y0[1]] + res[1]
            tetas = [y0[2]] + res[2]
            glob_x.append(xs)
            glob_y.append(ys)
            glob_tetas.append(tetas)

        plt.figure(1)
        plt.axis([-25, 25, -10, 10])
        # plt.hold()
        plt.plot(hf.barrier1_x, hf.barrier1_y, 'b')
        plt.plot(hf.barrier2_x, hf.barrier2_y, 'b')
        for j in range(len(nu)):
            plt.plot(glob_x[j], glob_y[j], 'r')
        plt.show()
