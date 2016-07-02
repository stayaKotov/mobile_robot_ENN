# -*- coding : utf-8 -*-

from parser_self import parse_depth
import Net
from ga_weights import begin_teaching


class Topology:
    # genotyoe представлен списком из цифр в десятичном представлении
    # phenotype является список функций, которые нужно применить к базисной топологии
    # network является полноценной сетью
    # time, value - критерии задачи
    def __init__(self, genotype):
        self.genotype = genotype
        self.phenotype = self.get_phenotype()
        from main import layers
        self.network = Net.Network(layers[:])
        self.network = self.update_network()
        self.time, self.accuracy = self.get_mistake()
        self.fitness = None

    # преобразуем базисное решение. Выполняем функции из фенотипа
    def update_network(self):
        for action in self.descendre_change_func():
            eval("{0}".format(action))
        return self.network

    # спускаем все апдейты функции активации вниз списка действий.
    # сначала ж надо поставить нейроны на нужные места
    def descendre_change_func(self):
        pheno_list_prev = self.phenotype
        pheno_list_prev.append('self.network.prepare_weights()')
        new_list = []
        another_list = []

        for elem in pheno_list_prev:
            if not elem.startswith('self.network.change_active_func'):
                new_list.append(elem)
            else:
                another_list.append(elem)

        return new_list + another_list

    # применяем грамматику к генотипу и получаем правила для преобразования сети
    def get_phenotype(self):
        # p1 = parse_depth(self.genotype)
        # pheno1 = parse_depth(self.genotype).strip()
        return parse_depth(self.genotype).strip().split(' ')

    # настраиваем веса сети. возвращаем значения двух критериев
    def get_mistake(self):
        best_params = begin_teaching(network=self.network, pop_len=8, cycles=1)
        self.network.set_weights(best_params.genotype)
        return best_params.time, best_params.accuracy

    # перегруженные функции

    def __str__(self):
        s = "time = {0} \naccuracy = {1} \nfitness = {2}\n".format(self.time, self.accuracy, self.fitness)
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
