# -*- coding: utf-8 -*-

from HelpFuncs import evaluate

class Topology_Weights:

    def __init__(self, network, genotype=[]):
        self.network = network
        self.genotype = genotype
        self.time, self.accuracy = self.get_mistake()
        self.fitness = None

    def __str__(self):
        return "time = {0}\naccuracy = {1}\nfitness = {2}\ngenotype = {3}\n".format(
            self.time, self.accuracy, self.fitness, self.genotype)

    def __eq__(self, other):
        return self.fitness == other.fitness

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __ge__(self, other):
        return not self.__lt__(other)

    def get_mistake(self):
        self.network.set_weights(self.genotype)
        return evaluate(self.network)
