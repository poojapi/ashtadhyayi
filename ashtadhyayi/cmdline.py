#!/usr/bin/python
# -*- coding: utf-8 -*-

from ashtadhyayi import *

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
