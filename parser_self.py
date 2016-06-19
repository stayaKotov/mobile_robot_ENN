# -*- coding: utf-8 -*-

import re
import HelpFuncs as hf


def parse_depth(genotype):
    grammar = {
        "<expr>": [
            "<expr><more_expr><expr>",
            "<more_expr>",
        ],
        "<more_expr>": [
            # "self.network.remove_layer(<layer_count>) ",
            "self.network.add_layer(<layer_count>,<bigConst>) ",
            "self.network.add_neurons(<layer_count>,<bigConst>) ",
            "self.network.change_active_func(<layer_count>,<Activation_func_number>) ",
            # "self.network.remove_neurons(<layer_count>,<bigConst>) ",
        ],
        "<layer_count>": [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
        ],
        '<bigConst>': [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
        ],
        '<Activation_func_number>': [
            '0', '1', '2', '3', '4', '5'
        ]
    }

    length = len(genotype)
    j = 0
    h = "<expr>"

    s = r"\<[expr|more_expr|bigConst|Activation_func_number|layer_count]+\>"
    pattern = re.compile(s)

    while j < length:
        elem = pattern.findall(h)
        if not elem and j < length:
            break
        el = elem[0]
        i = int(genotype[j] % len(grammar[el]))
        new_el = grammar[el][i]
        h = h.replace(el, new_el, 1)
        j += 1

    # теперь нужно обработать все нетерминальный символы
    while True:
        elements = pattern.findall(h)
        if elements:
            for el in elements:
                n = '' if el == "<expr>" else grammar[el][hf.rand(len(grammar[el]))]
                h = h.replace(el, n, 1)
        else:
            break

    s = r"\<[bigConst|smallConst|Activation_func_number|layer_number]+\>"
    pattern = re.compile(s)
    elems = pattern.findall(h)
    if elems:
        for el in elems:
            string = hf.rand(len(grammar[el]))
            h = h.replace(el, string, 1)

    return h

