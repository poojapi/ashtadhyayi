#!/usr/bin/python
# -*- coding: utf-8 -*-

from .utils import *
from . import *

def a():
    return ashtadhyayi()

def mahavakya(sutra_id):
    s = a().sutra(sutra_id)

    return s['mahavakya_padacCheda']

def paribhasha(sutra_id):
    p = get_paribhasha(sutra_id)
    if not p:
        print "Error: Paribhasha description not found for ", sutra_id
        return []

    matches = []
    for s_id in p.matching_sutras():
        s = a().sutra(s_id)
        out = dict((k, s[k]) for k in ('Sutra_krama', 'Sutra_text', 'Sutra_type'))
        matches.append(out)
    return matches

def praatipadika(pada, vibhakti=1, vachana=1):
    pada = sanscript.transliterate(pada, sanscript.SLP1, sanscript.DEVANAGARI)
    return Subanta().analyze({'pada': pada, 'vibhakti' : vibhakti, 
        'vachana' : vachana})

def annotate(pada_descs):
    # Each pada_desc in the list pada_descs has the following keys:
    #   Required keys:
    #       'pada' : the word to be annotated
    #       'upadesha' : Bool
    #   Optional keys:
    #       'type' : 'subanta|tinanta'
    #       'subtype' : 'avyaya'
    #       'vibhakti' : [1-8]
    #       'vachana' : [1-3]
    #       'lakara' : '..'
    #       'purusha' : '..'
    pass

def init_interpreter():
    annotate({'pada': 'hal', 'it' : [2], 'upadesha': True})
    for pada_desc in a().upadeshas['sutras']:
        annotate(pada_desc)
