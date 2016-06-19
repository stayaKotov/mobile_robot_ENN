# -*- coding: utf-8 -*-

import math
import random
import numpy as np
import multiprocessing as mp
import pareto_domination as pareto


# функция позволяет получить вещественное числов заданном диапазоне
def fract_rand(num):
    return round(2*num*random.random()-num, 7)


# функция позволяет получить целое числов от нуля до num
def rand(num):
    return math.trunc(random.random()*num)


# функция принимает параменты каждого элемента множеста
# строит пространство на основе критериев
# устанавливает коэффициент эффективности каждому элементу из переданного множества
def set_pareto_functionals(elems, population):
    return set_fitness(elems, population)


# функция назначает ранг каждому элементу на основе парето оптимизации
def set_fitness(functionals, population):
    pop = population[:]
    ranks = pareto.assign_ranks(functionals)
    fitness = pareto.set_fitness_from_ranks(ranks, len(functionals))
    for i in range(len(population)):
        pop[i].fitness = fitness[i]
    return pop


# сливаем данные из нескольких потоков в один список
def queue_to_list(count, queue):
    res = []
    for i in range(count):
        for elem in queue.get(i):
            res.append(elem)
    return res


# параллелим функцию с заданными аргументами на максимально возможное число процессов
def create_and_do_processes(func, args):
    count = mp.cpu_count()
    processes = [None for _ in range(count)]
    qu = mp.JoinableQueue()
    for i in range(count):
        qu.put(i)
    res = mp.Queue()
    hh = int(len(args['pop'])/count)
    for i in range(count):
        arg1 = args['pop'][i*hh:i*hh+hh]
        processes[i] = mp.Process(target=func, args=(arg1, res, qu), daemon=True)
        processes[i].start()
    qu.join()
    return count, res

########################################################################################
########################################################################################
########################################################################################


# численное решение дифференциальных уравнений на основе улучшенного метода Эйлера
def ode45(network, system, t, NU, step):

    def u(x):
        uu, uu1 = network.feed_forward(np.array([[e] for e in x]))
        return check_u(uu[0]), check_u1(uu1[0])

    dim = len(NU)
    time = t[0]+step
    res = [[NU[i]] for i in range(dim)]
    prev_y = [NU[i] for i in range(dim)]
    while time < t[-1]-step:
        a, b = u(prev_y)
        f = system(a, b)
        y_tilda = [prev_y[i]+step*f[i](time-step, prev_y) for i in range(dim)]
        for r in range(dim):
            tmp = prev_y[r] + step * (f[r](time-step, prev_y) + f[r](time, y_tilda))/2
            res[r].append(tmp)
            prev_y[r] = res[r][-1]

        time += step
    return res

########################################################################################
########################################################################################
########################################################################################


# система дифференциальных уравнений, задающая мат. модель движения робота
def system(u, u1):
    return [
        lambda t, x: u * math.cos(x[2]),
        lambda t, x: u * math.sin(x[2]),
        lambda t, x: u/Lb * math.tan(u1)
    ]



Lb = 2
x_a_1 = -20
y_a_1 = -2
x_b_1 = -5
y_b_1 = 2

x_a_2 = 5
y_a_2 = -2
x_b_2 = 20
y_b_2 = 2

barrier1_x = [x_a_1, x_a_1, x_b_1, x_b_1, x_a_1]
barrier1_y = [y_a_1, y_b_1, y_b_1, y_a_1, y_a_1]

barrier2_x = [x_a_2, x_a_2, x_b_2, x_b_2, x_a_2]
barrier2_y = [y_a_2, y_b_2, y_b_2, y_a_2, y_a_2]


# назначение штрафа за наезд на препятствие
def set_penalty(point):
    x = point[0]
    y = point[1]
    pen = 0
    x_begin = [x_a_1, x_b_1]
    x_end = [x_a_2, x_b_2]
    y_begin = [y_a_1, y_b_1]
    y_end = [y_a_2, y_b_2]
    l = len(x_begin)

    if (x < -5 and -2 < y < 2) or (x > 5 and -2 < y < 2):

        delta_x = 100
        delta_y = 100
        for i in range(l):
            delta_x = min(math.fabs(x_begin[i] - x), math.fabs(x_end[i] - x), delta_x)
            delta_y = min(math.fabs(y_begin[i] - x), math.fabs(y_end[i] - y), delta_y)

        pen += (delta_x ** 2 + delta_y ** 2) ** (1 / 2)
    return pen


# функция вычисления двух критериев эффективности
def evaluate(network):
    counter = 0
    results = [0, 0]
    NU = [[-8, -4, 0], [8, -4, 0], [-8, 4, 0], [8, 4, 0]]
    c = 4
    epsi = 0.08
    for q_q in NU[:]:
        penalty = [0 for _ in range(c)]
        y0 = q_q

        time = 10
        t = np.arange(0, time, 0.1)
        res = ode45(network, system, t, y0, 0.1)
        xs = [y0[0]]+res[0]
        ys = [y0[1]]+res[1]
        tetas = [y0[2]]+res[2]

        for el in [xs, ys, tetas]:
            for i in el:
                if math.isnan(i):
                    results[0] = 1e5
                    results[1] = 1e5
                    return results

        qwe = len(xs) - 1
        # узнаем максимальный индекс по трем параметрам.
        # индекс будет показывать на время полной остановки робота в точке
        for ii in range(len(xs) - 2, 0, -1):
            if math.fabs(xs[ii]) < 0.05 and math.fabs(ys[ii]) < 0.05 and math.fabs(tetas[ii]) < 0.05:
                qwe = ii
            else:
                break

        tt = xs[qwe] ** 2 + ys[qwe] ** 2 + tetas[qwe] ** 2
        if tt > epsi:
            qwe = len(xs) - 1
            tt = xs[qwe] ** 2 + ys[qwe] ** 2 + tetas[qwe] ** 2

        # на всем пути движения робота до полной остановки или до окончания время интегрирования
        for i in range(qwe + 1):
            x = xs[i]
            y = ys[i]
            teta = tetas[i]
            x_ = []
            y_ = []

            # промежуточные слагаемые
            for j in range(c):
                sign_x = 1
                sign_y = 1
                if j == 1 or j == 2:
                    sign_x = -1
                if j == 2 or j == 3:
                    sign_y = -1

                x_.append(x * math.cos(teta) + y * math.sin(teta) + sign_x * Lb)
                y_.append(-x * math.sin(teta) + y * math.cos(teta) + sign_y * Lb / 2)

            # расчет позиций 4 углов робота
            p = [
                    [
                        x_[r] * math.cos(teta) - y_[r] * math.sin(teta),
                        x_[r] * math.sin(teta) + y_[r] * math.cos(teta)
                    ] for r in range(c)
                ]
            # назначения штрафа за весь путь

            for j in range(c):
                penalty[j] += set_penalty(p[j])

        s = sum(penalty)
        timetime = t[qwe]

        if tt <= epsi and t[qwe] < 9.9 and s == 0:
            # print('xs = {0} and ys = {1} and tetas = {2} and time = {3}'.format(xs[qwe], ys[qwe], tetas[qwe], t[qwe]))
            # print('dist = {0} and penalty = {1}'.format(tt, s))
            counter += 1
            # print('check and {0}'.format(counter))

        # узнаем время, когда все три параметра перестали изменяться
        results[0] += timetime
        results[1] += tt

        # назначаем времени штраф за каждый угол робота на все пути движения
        results[0] += s
        results[1] += s

    if counter == 4:
        print('win')

    return results

########################################################################################
########################################################################################
########################################################################################


# функция проверки ограничений на функцию управления скоростью
def check_u(func):
    bound = 5
    u = func
    if u > bound:
        return bound
    if u < -bound:
        return -bound
    return u


# функция проверки ограничений на функцию управления углом поворота
def check_u1(func):
    bound = 1
    u = func
    if u > bound:
        return bound
    if u < -bound:
        return -bound
    return u