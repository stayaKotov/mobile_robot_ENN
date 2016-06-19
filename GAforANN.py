# -*- coding: utf-8 -*-

import math
from parser_self import parse_depth
import Net
import GAforParams as GA
import HelpFuncs as hf
import random
import time
import main


# Индивидуум описывается тремя полями
# 1) генотип - строка из десятичных чисел, кодирующая формулу
# 2) фитнес-функция - значение, которое стараемся минимизировать
# 3)фенотип - конечная формула. Ее используем для нахождения фитнеса у данного индивидуума

glob_pop = 8
glob_cycles = 4


class Individ:

    def __init__(self, genotype):
        self.network = Net.Network(main.layers[:])
        self.genotype = genotype
        self.phenotype = self.get_phenotype()
        self.network = self.update_network()
        self.time, self.value = self.get_mistake()
        self.fitness = None

    def __str__(self):
        s = "time = {0} \nvalue = {1} \nfitness = {2}\n".format(self.time, self.value, self.fitness)
        for action in self.phenotype:
            s += "{0}\n".format(action)
        return s

    def __eq__(self, other):
        if other.fitness:
            return self.fitness == other.fitness
        else:
            return type(self) == 'NoneType'

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __ge__(self, other):
        return not self.__lt__(other)

    def update_network(self):
        for action in self.descendre_change_func():
            eval("{0}".format(action))
        return self.network

    # спускаем все апдейты функции активации вниз списка действий.
    # сначала ж надо поставить нейроны, заполнить все весами, а потом уже менять функции
    def descendre_change_func(self):
        pheno_list = self.phenotype[:]
        pheno_list.append('self.network.prepare_weights()')
        new_list = []
        another_list = []
        for elem in pheno_list:
            if not elem.startswith('self.network.change_active_func'):
                new_list.append(elem)
            else:
                another_list.append(elem)
        return new_list + another_list

    # Для того, чтобы считать фитнес у индивидуума, нужен фенотип - конечная функция аппроксимации.
    # Ее можно получить след образом. Берем генотип индивиддума.
    # Проходим по нему и создаем функцию по заданной ранее грамматике
    def get_phenotype(self):
        pheno = parse_depth(self.genotype)
        phenotype = pheno.strip()
        return phenotype.split(' ')

    # получаем функцию. высчитываем интеграл по ошибке. используем нужные ограничения. делаем выводы
    def get_mistake(self):
        best_params = GA.begin_teaching(network=self.network,
                                        pop_len=glob_pop,
                                        cycles=glob_cycles)
        self.network.set_weights(best_params.phenotype)
        return best_params.time, best_params.value


##############################################################################
##############################################################################
##############################################################################

# Так как генотип кодируется строкой из десятичных чисел, то нужен генератор.
# Мы задаем длину генотипа и случайным образом заполняем его.
def get_genotype(gen_length):
    return [hf.rand(200) for _ in range(gen_length)]


# Популяцию получаем случайным генерированием первичных параметров у индивидуума.
def get_population(pop_len, geno_len):
    res = [0 for _ in range(pop_len)]
    for i in range(pop_len):
        b = time.time()
        res[i] = Individ(get_genotype(geno_len))
        print('i = {0} and time = {1}'.format(i, time.time()-b))
    return res


def mutation(chlds_gen, p):
    for j in range(len(chlds_gen)):
        if p > random.random():
            i = hf.rand(len(chlds_gen[j]))
            chlds_gen[j][i] = math.fabs(chlds_gen[j][i]-hf.rand(200))
    return chlds_gen


def get_children(children_genotype):
    res = [0 for _ in children_genotype]
    for i in range(len(children_genotype)):
        b = time.time()
        res[i] = Individ(genotype=children_genotype[i])
        print('i = {0} and time = {1}'.format(i, time.time()-b))
    return res


# Для получения детей используем турнирный метод селекции. Выбираем 7  родителей из популяции с малой фитнес-функцией.
# Далее из этих 7 отбираем двоих лучших и скрещиваем. Так получаются 2 ребенка от двух родителей.
def get_children_chromo(parents):

    def tournament():
        tmp = [min([parents[hf.rand(len(parents)-1)] for _1 in range(7)]) for _2 in range(2)]
        return tmp

    children_chromo = []
    for i in range(int(len(parents)/2)):
        children_chromo += crossover(tournament())
    return children_chromo


# В качестве кроссовера выбрал двуточечный кроссовер.
# Делим каждый генотип на 3 части, а не на две как в классике
def crossover(pair):
    p1 = pair[0]
    p2 = pair[1]
    c = random.randint(1, len(p1.genotype) - 2)

    return p1.genotype[:c]+p2.genotype[c:], p2.genotype[:c]+p1.genotype[c:]


# Популяция фиксированная, поэтому для следующего витка эволюци надо отобрать точное число родителей и детей.
# Объединим в один массив детей и родителей. Возьмем первых трех как самых лучших. Они должны выжить.
# А дальше снова дело случая.
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


def print_weights(elem):
    print(elem.network.sizes)
    print(len(elem.network.weights))


def print_all_sizes(pop):
    for elem in pop:
        print(elem.network.sizes)


# Главная функция генетического алгоритма. Изначально создана одна популяция(число особей будет фиксированным)
# Дальше нужно создавать потомство и эволюционировать
def run_ga_for_ann(geno_len, pop_len, cycles):
    population = get_population(pop_len,  geno_len)
    population = hf.set_pareto_functionals([[elem.time, elem.value] for elem in population], population)
    l = len(population)

    counter = cycles

    buf = population[:]
    buf.sort()
    print("count = {0}".format(counter))
    print(buf[0])

    while counter > 0:
        if counter % 1 == 0 and counter != cycles:
            print("runGAforANN")
            print("count = {0}".format(counter))
            print(population[0])

        genotypes = get_children_chromo(population)
        childs = mutation(genotypes, 0.8)
        children = get_children(childs)
        pop = hf.set_pareto_functionals([[elem.time, elem.value] for elem in population+children], population+children)
        population = get_new_population(pop[:l], pop[l:])

        counter -= 1
    print("count = 0")
    print(population[0])

    return population
