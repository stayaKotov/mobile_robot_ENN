
# -*- coding:utf-8 -*-


import json
import Net


# создать представление структуры сети в json файле
def create_json_from_net(elem):
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
            'value': str(elem.accuracy),
            'genotype': str(elem.genotype),
            'phenotype': elem.phenotype,
            'weights': w
        }, sort_keys=True, indent=4, separators=(',', ': ')
    )


# считать json файл и построить сеть, исходя из данных в файле
def create_net_from_json(json_file):
    dict_ = json.loads(json_file)
    js_w = dict_['weights']
    js_matrixes = js_w.split('\n')
    net = Net.Network(layers[:])
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
        action = action.replace('self.network', 'net')
        eval("{0}".format(action))
    net.set_weights_from_file(js_matrixes)
    return net


if __name__ == "__main__":
    from main import layers
    from ga_weights import begin_teaching

    f = open('best_structure.json', 'r')
    network = create_net_from_json(f.read())
    best_params = begin_teaching(network=network, pop_len=10, cycles=2)
    network.set_weights(best_params.genotype)
    network.plot()