#!/usr/bin/python
# -*- coding: utf-8 -*-

import locale
import sys
import json
import re
import os.path
from ashtadhyayi.utils import *
from ashtadhyayi import *
from pprint import pprint
from indic_transliteration import sanscript

pada_spec = [
    {
        'pada': 'At',
        'attrs': {
            'it' : [1],
            'seq' : ['A']
            'upadesa' : { 'source' : 'ashtadhyayi' }
            'samjnas' : {'it' : [1], 'upaDA' : [0], 
        }
        'result' : ['A']
    }
    {
        'pada': 'Ec',
        'attrs': {
            'it' : ['c'],
            'upadesa' : True
            'samjna' : True
            'dhatu' : False
            'pratyaya' : False
        }
        'result' : ['E', 'O']
    }
]

def ashtadhyayi_xform(pada_spec, transforms = ['CLASSIFY', 'JOIN', 'SPLIT']):
    if not transforms:
        return pada_spec
    
    if 'CLASSIFY' in transform:
        pass

def create_term_rules():
    for t,defn in a().terms_db.items():
        rule = { 'kutra' : [], 'kasmAt': [], 'kim' : [] }
        s = a().sutra(defn['sutra_id'])
        if "अधिक]रः" in s['Sutra_type']:
            sstart, sstop = map(lambda x: int(x)+1, s['Influence'].split('-'))
            members = {}
            for as_id in range(sstart, sstop):
                a_s = a().sutra(str(as_id))
                t_exists = reduce(lambda x, y, x or y,
                                 [(t in a['padas']) for a in a_s['Anuvrtti']])
                if not t_exists:
                    continue

                if "संज्ञा"  in a_s['Sutra_type']:
                    members[a_s['Term']] = [as_id]
                    continue

                # Pick words in prathama-vibhakti as candidates
                for p in a_s['PadacCheda']:
                    if p['type'] == subanta and p['vibhakti'] == 1:
                        pada = p['pada']
                        #print snum, pada.encode('utf-8')
                        #if pada.endswith(u"\u200C"):
                        #    continue
                        if pada not in members:
                            members[pada] = []
                        members[pada].append(snum)
                self.terms_db[t]['members'] = members


        samjna_desc = Subanta.analyze({'pada' : t, 
            'vibhakti' : 1, 'vachana' : 1})
        for p in defn['defn']:
            if not 'vibhakti' in p:
                continue

            pdesc = Subanta.analyze(p['pada'])
            if p['vibhakti'] == 1:
                if is_samjna(pdesc['pada']):
            elif p['vibhakti'] == 5:
            elif p['vibhakti'] == 6:
            elif p['vibhakti'] == 7:
                
