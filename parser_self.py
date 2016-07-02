# -*- coding: utf-8 -*-

import re
from random import randint


def parse_depth(genotype):
    grammar = {
        "<expr>": [
            "<expr><more_expr><expr>",
            "<more_expr>",
        ],
        "<more_expr>": [
            "self.network.add_layer(<layer_count>,<layer_count>) ",
            "self.network.add_neurons(<layer_count>,<layer_count>) ",
            "self.network.change_active_func(<layer_count>,<Activation_func_number>) ",
        ],
        "<layer_count>": [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
        ],
        '<Activation_func_number>': [
            '0', '1', '2', '3', '4', '5',
        ]
    }

    length = len(genotype)
    j = 0
    h = "<expr>"

    s = r"<+[" + ('|'.join(list(map(lambda x: x[1:-1], grammar.keys())))) + "]+>"
    pattern = re.compile(s)

    # построение выражения вглубину
    while j < length:
        elems = pattern.findall(h)
        if not elems and j < length:
            break
        el = elems[0]
        new_el = grammar[el][int(genotype[j] % len(grammar[el]))]
        h = h.replace(el, new_el, 1)
        j += 1

    # убираем все оставишиеся нетерминальные символы
    while True:
        elements = pattern.findall(h)
        if elements:
            for el in elements:
                n = '' if el == "<expr>" else grammar[el][randint(0, len(grammar[el])-1)]
                h = h.replace(el, n, 1)
        else:
            break

    return h
