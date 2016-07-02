# -*- encoding:utf-8-*-

import ga_ann
import ann_js

layers = [3, 1, 2]

if __name__ == "__main__":

    solution = ga_ann.run_ga_ann(
       geno_len=10,
       pop_len=6,
       cycles=2)[0]

    f = open('best_structure.json', 'w')
    f.write(ann_js.create_json_from_net(solution))
    f.close()

    solution.network.plot()
