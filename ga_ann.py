# -*- coding: utf-8 -*-

import math
import HelpFuncs as hf
import random
import time
from Topology import Topology as Topo

# Так как генотип кодируется строкой из десятичных чисел, то нужен генератор.
# Мы задаем длину генотипа и случайным образом заполняем его.
def get_genotypes(gen_length):
    return [random.randint(0, 200) for _ in range(gen_length)]


# Популяцию получаем случайным генерированием первичных параметров у индивидуума.
def get_population(pop_len, geno_len):
    res = [0 for _ in range(pop_len)]
    for i in range(pop_len):
        b = time.time()
        res[i] = Topo(get_genotypes(geno_len))
        print('i = {0} and time = {1}'.format(i, time.time()-b))
    return res


def mutation(chlds_gen, p):
    for j in range(len(chlds_gen)):
        if p > random.random():
            i = random.randint(0, len(chlds_gen[j])-1)
            chlds_gen[j][i] = math.fabs(chlds_gen[j][i]-random.randint(0, 200))
    return chlds_gen


def get_children(children_genotype):
    res = [0 for _ in children_genotype]
    for i in range(len(children_genotype)):
        b = time.time()
        res[i] = Topo(children_genotype[i])
        print('i = {0} and time = {1}'.format(i, time.time()-b))
    return res


# Для получения детей используем турнирный метод селекции. Выбираем 7  родителей из популяции с малой фитнес-функцией.
# Далее из этих 7 отбираем двоих лучших и скрещиваем. Так получаются 2 ребенка от двух родителей.
def get_children_chromo(parents):
    def tournament():
        return [min([parents[random.randint(0, len(parents)-1)] for _1 in range(7)]) for _2 in range(2)]
    children_chromo = []
    for i in range(int(len(parents)/2)):
        pair = tournament()
        children_chromo += crossover(pair[0].genotype, pair[1].genotype)
    return children_chromo


# В качестве кроссовера выбрал двуточечный кроссовер.
# Делим каждый генотип на 3 части, а не на две как в классике
def crossover(p1, p2):
    c = random.randint(1, len(p1) - 2)
    d = random.randint(1, len(p1) - 2)

    if c > d:
        c, d = d, c

    return [p1[:c]+p2[c:d]+p1[d:], p2[:c]+p1[c:d]+p2[d:]]


# Популяция фиксированная, поэтому для следующего витка эволюци надо отобрать точное число родителей и детей.
# Объединим в один массив детей и родителей. Возьмем первых трех как самых лучших. Они должны выжить.
# А дальше снова дело случая.
def get_new_population(population, children):
    l = len(population)
    buf = population+children
    buf.sort()
    c = int(0.2*l)
    new_population = buf[:c]
    tmp = buf[c:]
    ll = len(tmp)
    new_population += [tmp[random.randint(0, ll-1)] for _ in range(c, l)]
    return new_population


# Главная функция генетического алгоритма. Изначально создана одна популяция(число особей будет фиксированным)
# Дальше нужно создавать потомство и эволюционировать
def run_ga_ann(geno_len, pop_len, cycles):
    population = get_population(pop_len,  geno_len)
    population = hf.get_population_with_fitness(population)
    l = len(population)

    buf = population[:]
    buf.sort()

    print("topology search")
    print("count = {0}".format(cycles))
    print(buf[0])

    while cycles > 0:
        genotypes = get_children_chromo(population)
        childs = mutation(genotypes, 0.8)
        children = get_children(childs)
        pop = hf.get_population_with_fitness(population+children)
        population = get_new_population(pop[:l], pop[l:])
        cycles -= 1

        print("topology search")
        print("cycles = {0}".format(cycles))
        print(population[0])

    return population
