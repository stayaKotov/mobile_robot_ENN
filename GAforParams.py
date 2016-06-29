# -*- coding: utf-8 -*-

import HelpFuncs as hf
import random

bound = 3
mute = 300

nets = None


class Individ:

    def __init__(self, networks=nets, phenotype_1=[], phenotype_2=[]):
        self.networks = networks
        self.phenotypes = [phenotype_1, phenotype_2]
        self.time, self.value = self.get_mistake()
        self.fitness = None

    def __str__(self):
        return "time = {0}\nvalue = {1}\nfitness = {2}\nphenotype_u1 = {3}\nphenotype_u2 = {4}\n".format(
            self.time, self.value, self.fitness, self.phenotypes[0], self.phenotypes[1])

    def __eq__(self, other):
        return self.fitness == other.fitness

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __ge__(self, other):
        return not self.__lt__(other)

    def get_mistake(self):
        self.networks[0].set_weights(self.phenotypes[0])
        self.networks[1].set_weights(self.phenotypes[1])
        return hf.evaluate(self.networks)

##############################################################################
##############################################################################
##############################################################################


def get_phenotype(count):
    return [hf.fract_rand(bound) for _ in range(count)]


def begin_teaching(networks, pop_len, cycles):
    global nets
    nets = networks[:]
    population = get_population(networks, pop_len)
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
def get_population(networks, pop_len):
    l_1 = networks[0].get_params_count()
    l_2 = networks[1].get_params_count()
    return [Individ(networks, get_phenotype(l_1), get_phenotype(l_2)) for _ in range(pop_len)]


def get_children_data(parents):

    def tournament():
        ret = []
        for _1 in range(2):
            random_parents = []
            r = [random.randint(1, len(parents) - 1) for _ in range(7)]
            for j in range(7):
                random_parents.append(parents[r[j]])
            sorted(random_parents)
            ret.append(random_parents[0])
        return ret

    l = int(len(parents)/2)
    children_chromo = [[], []]
    for i in range(l):
        pair = tournament()
        children_chromo[0] += crossover(pair[0].phenotypes[0], pair[1].phenotypes[0])
        children_chromo[1] += crossover(pair[0].phenotypes[1], pair[1].phenotypes[1])
    return [[el[0], el[1]] for el in zip(children_chromo[0], children_chromo[1])]


def crossover(p1, p2):
    c = random.randint(1, len(p1) - 2)
    d = random.randint(1, len(p1) - 2)

    if c > d:
        c, d = d, c

    return [p1[:c]+p2[c:d]+p1[d:], p2[:c]+p1[c:d]+p2[d:]]


def mutation_and_get_children(population, res, qu):
    qu.get()
    global mute
    if mute > 5:
        p = 0.8
    else:
        print('gg')
        p = 0.2
    children_dict = get_children_data(population)
    childs_dict = mutation_wrapper(children_dict, p)
    res.put(get_children(childs_dict))
    qu.task_done()


def mutation_wrapper(chromosomes, p):
    return [[el[0], el[1]] for el in
            zip(mutation([elem[0] for elem in chromosomes], p), mutation([elem[1] for elem in chromosomes], p))]


def mutation(childs_dict, p):
    for j in range(len(childs_dict)):
        if p > random.random():
            i = hf.rand(len(childs_dict[j]))
            childs_dict[j][i] = hf.fract_rand(bound)
    return childs_dict


def get_children(children_chromos):
    return [Individ(networks=nets, phenotype_1=elem[0], phenotype_2=elem[1]) for elem in children_chromos]


def get_new_population(population, children):
    l = len(population)
    buf = population+children
    buf.sort()
    c = int(0.2*l)
    new_population = buf[:c]
    tmp = buf[c:]
    ll = len(tmp)
    new_population += [tmp[hf.rand(ll)] for _ in range(c, l)]
    return new_population
