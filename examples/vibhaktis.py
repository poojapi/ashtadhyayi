import sys
sys.path.append("..")
from vedavaapi.ashtadhyayi.cmdline import *

myfilter = {'PadacCheda' : {'vibhakti' : 1 } }
result = {}
nunique = 0
for v in [0, 1, 2, 3, 4, 5, 6, 7]:
    myfilter['PadacCheda']['vibhakti'] = v
    v_padas = []
    for s_id in a().sutras(myfilter):
        s = a().sutra(s_id)
        for p in s['PadacCheda']:
            if 'vibhakti' not in p:
                continue
            elif p['vibhakti'] != v:
                continue
            v_padas.append(p['pada'])
    result[v] = sorted(set(v_padas))
    nunique += len(result[v])
    print "{}: {}".format(v, len(result[v]))

#print "Total subanta words in Ashtadhyayi:", nwords
#print "Total unique subanta words in Ashtadhyayi:", nunique
#print_dict(result)

nwords = 0
subantas = []
tinantas = {}
for s_id in a().sutras():
    s = a().sutra(s_id)
    for p in s['PadacCheda']:
        nwords = nwords + 1
        if 'vibhakti' not in p:
            if p['pada'] not in tinantas:
                tinantas[p['pada']] = []
            tinantas[p['pada']].append(s_id)
        else:
            subantas.append(p['pada'])

nsubantas = len(set(subantas))
ntinantas = len(tinantas.keys())
for t in tinantas.keys():
    print "{} - {}".format(t.encode('utf-8'), ", ".join(tinantas[t]))
print "Subantas: {}, tinantas: {}, total unique: {}, total: {}".\
    format(nsubantas, ntinantas, nsubantas+ntinantas, nwords)
