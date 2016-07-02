# -*- coding: utf-8 -*-

import HelpFuncs as hf
import random
from Topology_Weights import Topology_Weights as Topo_W
import ga_ann
bound = 6

net = None


def get_phenotype(count):
    return [hf.fract_rand(bound) for _ in range(count)]


# Популяцию получаем случайным генерированием первичных параметров у индивидуума.
def get_population(network, pop_len):
    l_1 = network.get_params_count()
    return [Topo_W(network, get_phenotype(l_1)) for _ in range(pop_len)]


def mutation_and_get_children(population, res, qu):
    qu.get()
    children_dict = ga_ann.get_children_chromo(population)
    childs_dict = mutation(children_dict, 0.8)
    res.put(get_children(childs_dict))
    qu.task_done()


def mutation(childs_dict, p):
    for j in range(len(childs_dict)):
        if p > random.random():
            i = random.randint(0, len(childs_dict[j])-1)
            childs_dict[j][i] = hf.fract_rand(bound)
    return childs_dict


def get_children(children_chromos):
    return [Topo_W(net, elem) for elem in children_chromos]


def begin_teaching(network, pop_len, cycles):
    global net
    net = network
    population = get_population(network, pop_len)
    population = hf.get_population_with_fitness(population)
    l = len(population)

    while cycles > 0:
        random.shuffle(population)
        count, res = hf.create_and_do_processes(mutation_and_get_children, {'pop': population})
        children = hf.queue_to_list(count, res)
        pop = hf.get_population_with_fitness(population+children)
        population = ga_ann.get_new_population(pop[:l], pop[l:])
        cycles -= 1
        # print(cycles)
        # print(population[0])
    return population[0]
