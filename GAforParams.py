# -*- coding: utf-8 -*-

import HelpFuncs as hf
import math
import random

bound = 30

mute = 300

class Individ:
    network = None

    def __init__(self, pheno):
        self.phenotype = pheno
        self.time, self.value = self.get_mistake()
        self.fitness = None

    def __str__(self):
        return "time = {0}\nvalue = {1}\nfitness = {2}\nphenotype = {3}\n".format(
            self.time, self.value, self.fitness, self.phenotype)

    def __eq__(self, other):
        return self.fitness == other.fitness

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __ge__(self, other):
        return not self.__lt__(other)

    def get_mistake(self):
        self.network.set_weights(self.phenotype)
        return hf.evaluate(self.network)

##############################################################################
##############################################################################
##############################################################################


def get_phenotype(count):
    return [hf.fract_rand(bound) for _ in range(count)]


def begin_teaching(network, pop_len, cycles):
    Individ.network = network
    population = get_population(network, pop_len)
    population = hf.set_pareto_functionals([[elem.time, elem.value] for elem in population], population)
    l = len(population)

    while cycles > 0:
        random.shuffle(population)
        count, res = hf.create_and_do_processes(mutation_and_get_children, {'pop': population})
        children = hf.queue_to_list(count, res)
        pop = hf.set_pareto_functionals([[elem.time, elem.value] for elem in population+children], population+children)
        population = get_new_population(pop[:l], pop[l:])
        cycles -= 1
        # print(cycles)
        # print(population[0])
    return population[0]


# Популяцию получаем случайным генерированием первичных параметров у индивидуума.
def get_population(network, pop_len):
    return [Individ(get_phenotype(network.get_params_count())) for _ in range(pop_len)]


def get_children_data(parents):

    def tournament():
        tmp = [min([parents[hf.rand(len(parents)-1)] for _1 in range(7)]) for _2 in range(2)]
        return tmp

    children_dict_net_and_genotype = []
    for i in range(int(len(parents)/2)):
        children_dict_net_and_genotype += crossover(tournament())
    return children_dict_net_and_genotype


def crossover(pair):
    p1 = pair[0]
    p2 = pair[1]
    c = random.randint(1, len(p1.phenotype) - 2)
    d = random.randint(1, len(p1.phenotype) - 2)

    if c > d:
        c, d = d, c

    return [
        p1.phenotype[:c]+p2.phenotype[c:d]+p1.phenotype[d:],
        p2.phenotype[:c]+p1.phenotype[c:d]+p2.phenotype[d:]
    ]


def mutation_and_get_children(population, res, qu):
    qu.get()
    global mute
    if mute > 5:
        mutations = 0.8
    else:
        print('gg')
        mutations = 0.2
    children_dict = get_children_data(population)
    childs_dict = mutation(children_dict, mutations)
    res.put(get_children(childs_dict))
    qu.task_done()


def mutation(childs_dict, p):
    for j in range(len(childs_dict)):
        if p > random.random():
            i = hf.rand(len(childs_dict[j]))
            childs_dict[j][i] = hf.fract_rand(bound)
    return childs_dict


def get_children(children_dict):
    return [Individ(elem) for elem in children_dict]


def get_new_population(population, children):
    l = len(population)
    buf = population+children
    buf.sort()
    c = math.trunc(0.2*l)
    new_population = buf[:c]
    tmp = buf[c:]
    ll = len(tmp)
    new_population += [tmp[hf.rand(ll)] for _ in range(c, l)]
    return new_population
