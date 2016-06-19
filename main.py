# -*- encoding:utf-8-*-

import GAforANN as GA_ANN
import ANNtoJSON as ann_js

layers = [3, 1, 2]
if __name__ == "__main__":

    the_best = GA_ANN.run_ga_for_ann(
       geno_len=10,
       pop_len=10,
       cycles=10)[0]

    f = open('best_structure.json', 'w')
    f.write(ann_js.newJSON(the_best))
    f.close()

    the_best.network.plot()
