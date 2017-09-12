#!/usr/bin/python

from ashtadhyayi.cmdline import *

myfilter = {'PadacCheda' : {'vibhakti' : 1 } }
result = {}
for v in [0, 1, 2, 3, 4, 5, 6, 7]:
    myfilter['PadacCheda']['vibhakti'] = v
    v_padas = []
    for s_id in a().sutras(myfilter):
        s = a().sutra(s_id)
        for p in s['PadacCheda']:
            if 'vibhakti' not in p:
                continue
            if p['vibhakti'] != v:
                continue
            v_padas.append(p['pada'])
    result[v] = sorted(set(v_padas))

print_dict(result)
