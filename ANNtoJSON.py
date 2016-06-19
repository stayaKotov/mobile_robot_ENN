
# -*- coding:utf-8 -*-

__author__ = 'anton'

import json
import Net
import GAforParams as GA


# создать представление структуры сети в json файле
def newJSON(elem):
    w = ''
    for matrix in elem.network.weights:
        w += "("
        for row in matrix:
            num_row = list(map(lambda el: float(el), row))
            tmp_str = list(map(lambda el: str(el), num_row))
            w += ','.join(tmp_str)
            w += ';'
        w = w[:-1]
        w += ")\n"
    w = w[:-1]

    return json.dumps(
        {
            'time': str(elem.time),
            'value': str(elem.value),
            'genotype': str(elem.genotype),
            'phenotype': elem.phenotype,
            'weights': w
        }, sort_keys=True, indent=4, separators=(',', ': ')
    )


# считать json файл и построить сеть, исходя из данных в файле
def parseJSON(json_file):

    dict_ = json.loads(json_file)

    js_w = dict_['weights']
    js_matrixes = js_w.split('\n')

    import main
    network = Net.Network(main.layers)

    phenotype = dict_['phenotype']

    pheno_list = phenotype[:]
    pheno_list.append('self.network.prepare_weights()')
    new_list = []
    another_list = []
    for elem in pheno_list:
        if not elem.startswith('self.network.change_active_func'):
            new_list.append(elem)
        else:
            another_list.append(elem)
    res = new_list + another_list

    for action in res:
        action = action.replace('self.', '')
        eval("{0}".format(action))
    network.set_weights_from_file(js_matrixes)
    return network


if __name__ == "__main__":
    f = open('best_structure.json', 'r')
    network = parseJSON(f.read())
    best_params = GA.begin_teaching(network=network,
                                    pop_len=12000,
                                    cycles=50)
    network.set_weights(best_params.phenotype)
    network.plot()