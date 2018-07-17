import sys
sys.path.append("..")
from vedavaapi.ashtadhyayi.cmdline import *

input_list = [
    { 'word' : '' },
    { 'word' : '' },
    { 'word' : '' },
    { 'word' : '' },
    { 'word' : '' },
    { 'word' : '' },
]

pratyaharas = [
    { 'word' : 'aiuN', 'it' : [3], 'anunAsika' : [3] },
    { 'word' : 'RLk' , 'it' : [2]},
    { 'word' : '' },
    { 'word' : '' },
    { 'word' : '' },
    { 'word' : 'hal', 'it' : [2], },
]

{ 'samjna' : 'ac', 
  'samjni' : {
        'word' : "aiuNRLkeo~nai au ch", 'it' : [3,6,9,12],
        'effective_word' : "a i u R L e o ai au" }
}


input_list = [
    { 'word' : 'ramu' },
    { 'word' : 'gha~N' },
    { 'word' : 'jas' }
]

input_list = [
    { 'word' : 'ramu', 'it' : [3], 'effective_word' : 'ram' },
    { 'word' : 'gha~N', 'it' : [0,2], 'effective_word' : 'a' },
    { 'word' : 'jas', 'it' : [0], 'effective_word' : 'as'  }
]

def annotate(pada_descs):
    for p in pada_descs:
        a().check_samjna(p)

a()
#annotate([{'pada' : 'ac', 'upadesha' : True}])
