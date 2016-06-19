# -*- coding: utf-8 -*-
__author__ = 'anton'


# берем два элемента. они представлены двумерным массивом. идем по второй строке.
# если какой - либо из параметров во втором элементе болльше, чем в первом, то
# первый элемент не доминирует над вторым
def dominate(F1, F2):
    d = False
    for i in range(len(F1[1])):
        if F1[1][i] < F2[1][i]:
            d = True
        elif F2[1][i] < F1[1][i]:
            return False
    return d



def non_dominated_front(Group):
    # изанчально недоминирующий фронт пустой
    Front = []
    # проходим по каждому элементу в выборке, которую передаем в функцию
    for G in Group:
        # добавляем элемент в НЕдоминирующий фронт
        Front.append(G)
        # копируем полученный фронт во временный массив
        tmpFront = Front[:]
        # проходим по начальному фронту
        for C in Front:
            if G != C:
                # если элемент, который добавили во фронт доминирует над другим элементом, то удаляем доминанта из временного массива
                # и обрываем цикл.
                if dominate(G, C):
                    tmpFront.remove(G)
                    break

                elif dominate(C, G):
                    tmpFront.remove(C)
        Front = tmpFront[:]
    return Front



# создаем список кортежей: номер элемента и список его параметров.
def assign_ranks(functionals):
    tmp_functionals = [(i, functionals[i]) for i in range(len(functionals))]
    ranks = []
    i = 0
    while tmp_functionals != []:
        ranks.append(non_dominated_front(tmp_functionals))
        for R in ranks[i]:
            tmp_functionals.remove(R)
        i += 1
    return ranks



def set_fitness_from_ranks(ranks, pop_size):
    Fitness = [0.0 for i in range(pop_size)]
    cr = 0.0
    for R in ranks:
        for e in R:
            Fitness[e[0]] = 1.0 / (1.0 + cr)
        cr += 1
    return Fitness

