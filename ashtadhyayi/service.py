#!/usr/bin/python
# -*- coding: utf-8 -*-

import locale
import sys
import json
import re
import os.path
from .utils import *
from .config import *
from .subanta import *
from .rule import *
from pprint import pprint
from indic_transliteration import sanscript

AND = None
OR = None
NOT = None
SAMJNA = None
PRATYAYA = None
IT_ENDING = None
UPADESHA = None

class Ashtadhyayi:
    def __init__(self, sutras_json_file):
    	self.sutra_ids = []
        self.sutra_id_idx = {}
        self.terms_db = {}

        global AND
        AND = self._and
        global OR
        OR = self._or
        global NOT
        NOT = self._not
        global SAMJNA
        SAMJNA = self.is_samjna
        global PRATYAYA
        PRATYAYA = self.is_pratyaya
        global IT_ENDING
        IT_ENDING = self.it_ending
        global UPADESHA
        UPADESHA = self.is_upadesha

        # Key should be in SLP1 format
        self.predefined_funcs = {
            'antya' : lambda x: Subanta.praatipadikam(x)[-1],
            'Adi' : lambda x: Subanta.praatipadikam(x)[0],
            'upadeSa' : UPADESHA,
            'hal' : lambda x: x if x['pada'] == 'hal' else None
        }

        print "Loading Ashtadhyayi sutras .."
        with open(sutras_json_file) as data_file:
            try:
                self.ashtadhyayi = json.load(data_file)
                self.sutra_ids = sorted(self.ashtadhyayi['sutras'].keys())
                for i in range(len(self.sutra_ids)):
                    self.sutra_id_idx[self.sutra_ids[i]] = i
            except ValueError as err: # catch *all* exceptions
                print("Error: Format error in JSON file: ", err, ": aborting.", sutras_json_file)
                exit(1)

        print "Loading upadesha data .."
        self.load_upadeshas()
        print "Inferring Praatipadikas for all padas .."
        self.infer_praatipadikas()
        print "Building mahavakyas for all sutras .."
        self.build_mahavakyas()
        print "Pre-processing Samjna definitions .."
        self.extract_termdefs()

    def _and(self, pada_desc, conds):
        return reduce((lambda x, y: x and y), 
            [self._propmatch(pada_desc, c) for c in conds])

    def _or(self, pada_desc, conds):
        return reduce((lambda x, y: x or y), 
            [self._propmatch(pada_desc, c) for c in conds])


    def _not(self, pada_desc, cond):
        #print_dict(pada_desc)
        #print_dict(cond)
        return not self._propmatch(pada_desc, cond)

    def load_upadeshas(self):
        self.upadesha = { 'sutras' : [], 'dhaatu' : [], 
            'pratyaya' : [], 'nipAta' : [] }
        with open(datapath("maheshvara-sutras.txt")) as f:
            self.upadesha['sutras'] = [l.strip() for l in f.readlines()]
            pprint(self.upadesha['sutras'])

        it = { 'l' : True }
        varnas = reduce(lambda x,y : x + y,
            [s for s in self.upadesha['sutras']])
            
        def pratyahara(string):
            if len(string) > 3:
                return ""
            if string[-1] not in it:
                return ""
            starti = -1
            endi = 0
            for i in range(len(varnas)):
                if starti < 0 and varnas[i] == string[0]:
                    starti = i
                if endi < 0 and varnas[i] == string[1]:
                    endi = i
            if starti < 0 or endi < 0:
                return ""
            if starti >= endi:
                return ""
            return varnas[starti:endi]

        for c in pratyahara("hl"):
            it[c] = True

    def is_samjna(self, pada_desc):
        praatipadikam = Subanta.praatipadikam(pada_desc)
        match = praatipadikam in self.terms_db
        if match:
#            print "Found ", pada_desc['pada'].encode('utf-8')
            pass
        return match

    def is_pratyaya(self, pada_desc):
        match = pada_desc['pada'] in self.pratyayas
        if match:
#            print "Found ", pada_desc['pada'].encode('utf-8')
            pass
        return match

    def is_upadesha(self, pada_desc):
        praatipadikam = Subanta.praatipadikam(pada_desc)
        for gana in self.upadesha.keys():
            if praatipadikam in self.upadesha[gana]:
                print praatipadikam + " in upadesha: " + gana
                pada_desc['upadeSa'] = gana
                return pada_desc
        return None

    def it_ending(self, pada_desc, parms):
        subanta = "सुबन्त"
        if not (pada_desc['type'] == subanta.decode('utf-8') and 
                pada_desc['vibhakti'] == 1):
            return False
        pada = pada_desc['pada'].encode('utf-8')
            
        match = pada.endswith(parms["varna"])
        if match:
    #        print "Matched", pada, "with ", parms["varna"]
            pass
        return match

    def sutra(self, sutra_id):
        try:
            sutra = self.ashtadhyayi["sutras"][str(sutra_id)]
            return sutra
        except ValueError as err: # catch *all* exceptions
            print("Error: " + str(sutra_id) + " not found.")
            return None

    def split_sutra(self, sutra_id):
        s = self.sutra(sutra_id)
        return " ".join([p['pada'] for p in s['PadacCheda']])

    def _propmatch(self, myobj, cond = None):
        if not cond:
            return True

        #print "matching "
        #pprint(myobj)
        #print "against "
        #pprint(cond)
        ismatch = False
        if isinstance(cond, list):
            if callable(cond[0]):
                # If matching with list, condition must apply to any item
                if isinstance(myobj, list):
                    return reduce((lambda x, y: x or y), 
                        [cond[0](o, cond[1]) for o in myobj])
                # If dict, condition must apply to it
                if isinstance(myobj, dict):
                    return cond[0](myobj, cond[1])
            # If cond is a list and myobj is scalar, match any list item
            ismatch = reduce((lambda x, y: x or y), 
                [self._propmatch(myobj,  v) for v in cond])
        elif callable(cond):
            return cond(myobj)
        elif isinstance(cond, dict):
            if isinstance(myobj, list):
                # cond must match any list item
                ismatch = reduce((lambda x, y: x or y), 
                    [self._propmatch(o, cond) for o in myobj])
                return ismatch
            if not isinstance(myobj, dict):
                return False

            # Both query and object are dictionaries
            # Hence match the values for each of the keys.
            ismatch = True
            for k in cond.keys():
                if k not in myobj:
                    return False

                if not self._propmatch(myobj[k], cond[k]):
                    return False
        else:
            if isinstance(cond, str):
                cond = cond.decode('utf-8')
            if isinstance(myobj, list):
                ismatch = reduce((lambda x, y: x or y), 
                    [(o == cond) for o in myobj])
            else:
                ismatch = (myobj == cond)

        if not ismatch:
            return False
        return True

    def equal_dvng(self, w1, w2):
        ma = "म्"
        ma = ma.decode('utf-8')
        if not (w1.endswith(ma) or w2.endswith(ma)):
            return w1 == w2
        w1 = sanscript.transliterate(w1, sanscript.DEVANAGARI, sanscript.SLP1)
        w2 = sanscript.transliterate(w2, sanscript.DEVANAGARI, sanscript.SLP1)
        w1 = re.sub(r'[mM]$', 'm', w1)
        w2 = re.sub(r'[mM]$', 'm', w2)
        return w1 == w2

    def sutras(self, match_props = None):
    	return (snum for snum in self.sutra_ids \
            if self._propmatch(self.sutra(snum), match_props))

    def infer_praatipadikas(self):
        for s_id in self.sutras():
            sutra = self.sutra(s_id)
            for p in sutra['PadacCheda']:
                if 'analysis' in p:
                    continue
                if 'vibhakti' not in p:
                    continue

                p['analysis'] = Subanta.analyze(p)

    def find_listable_terms(self):
        not_terms = {}
        with open(datapath("pratyaya-notlist.txt")) as f:
            lines = f.readlines()
            for l in lines:
                l = l.rstrip()
                not_terms[l.decode('utf-8')] = True

        #rule = { 'kutra' : [], 'kasmAt': [], 'kim' : [] }
        for t,term_desc in self.terms_db.items():
            for defn in term_desc['defns']:
                s = self.sutra(defn['sutra_id'])
                if utf8_decode("अधिकारः") in s['Sutra_type']:
                    sfirst, slast = s['Influence'].split('-')
                    starti = self.sutra_id_idx[sfirst] + 1
                    stopi = self.sutra_id_idx[slast] + 1
                    members = {}
                    for i in range(starti, stopi):
                        as_id = self.sutra_ids[i]
                        a_s = self.sutra(str(as_id))
                        if 'Anuvrtti' not in a_s:
                            continue
                        if t == 'tadDita':
                            print_dict(a_s['Anuvrtti'])
                        t_exists = reduce(lambda x, y: x or y,
                                        [(t in a['praatipadikas']) for a in a_s['Anuvrtti']])
                        if not t_exists:
                            continue

                        if utf8_decode("संज्ञा") in a_s['Sutra_type']:
                            myterm = a_s['Term']
                            if myterm not in members:
                                members[myterm] = []
                            members[myterm].append(as_id)
                            continue

                        # Pick words in prathama-vibhakti as candidates
                        for p in a_s['PadacCheda']:
                            if p['type'] == utf8_decode("सुबन्त") and p['vibhakti'] == 1:
                                pada = p['pada']
                                if pada in not_terms:
                                    continue
                                #print snum, pada.encode('utf-8')
                                #if pada.endswith(u"\u200C"):
                                #    continue
                                if pada not in members:
                                    members[pada] = []
                                members[pada].append(as_id)
                    term_desc['members'] = members
                    self.upadesha[t] = members.keys()
            
    def compile_term_rules(self):
        for t,term_desc in self.terms_db.items():
            if 'members' in term_desc:
                continue
            for defn in term_desc['defns']:
                s = self.sutra(defn['sutra_id'])
                if utf8_decode("संज्ञा") not in s['Sutra_type']:
                    continue
                vibhakti_ordered = sorted(defn['defn'], key=lambda k: k['vibhakti'] if ('vibhakti' in k) else 0, reverse=True)
                #print_dict(vibhakti_ordered)
                defn['rule'] = Rule(self, t).compile(vibhakti_ordered)
                #print(defn['rule'])

    def check_samjna(self, term_slp1, pada_desc):
        pada_desc['analysis'] = Subanta.analyze(pada_desc)
        term_desc = self.terms_db[term_slp1]
            
        if 'members' in term_desc:
            if Subanta.praatipadikam(pada_desc) in term_desc['members']:
                return True
        for d in term_desc['defns']:
            print "Checking rule .."
            print_dict(d['rule'])
            Rule(self, term_slp1, d['rule']).apply(pada_desc)
        return pada_desc[term_slp1]

    def compute_pratyaharas(self):
        res = self.check_samjna('it', 
            { 'pada' : 'hal', 'vibhakti' : 1, 'vachana' : 1 })
        print "Result: ", res
        

    def extract_termdefs(self):
        samjna_file = outpath("terms.json")
        if os.path.isfile(samjna_file):
            with open(samjna_file) as f:
                try:
                    self.terms_db = json.load(f)
                    return
                except ValueError as err: # catch *all* exceptions
                    print("Error: Format error in JSON file: ", err, ": aborting.", samjna_file)
                
        print "Extracting samjna definitions from samjna sutras .."
        self.terms_db = {}
        term_defs_str = ""
        for snum in self.sutras({ 'Sutra_type' : "संज्ञा" }):
            s = self.sutra(snum)
            for t in s['Term'].split():
                # Search for samjna in sutra's padacCheda
                pdesc = Subanta.analyze({'pada' : t,
                    'vibhakti' : 1, 'vachana' : 1})
                print_dict(pdesc)
                if pdesc:
                    praatipadikam = pdesc[0]['praatipadikam']
                if not praatipadikam:
                    print "Error: Couldn't find praatipadika for ", t
                    exit(1)
                if praatipadikam not in self.terms_db:
                    self.terms_db[praatipadikam] = { 'pada' : t, 'defns' : [] }

                defn = []
                def_padas = []
                for p in s['mahavakya_padacCheda']:
                    if p['pada'] == t:
                        continue
                    #print_dict(p)
                    if 'analysis' in p:
                        found = False
                        for pada_a in p['analysis']:
                            for term_a in pdesc:
                                #print pada_a['praatipadikam'] + " == " + term_a['praatipadikam']
                                if pada_a['praatipadikam'] == term_a['praatipadikam']:
                                    found = True
                                    break
                            if found:
                                break
                        if found:
                            continue

                    if 'pada_split' in p:
                        #pada_split_slp1 = sanscript.transliterate(p['pada_split'], 
                        #    sanscript.DEVANAGARI, sanscript.SLP1)

                        split_desc = { 'pada' : p['pada_split'],
                            'vibhakti' : p['vibhakti'],
                            'vachana' : p['vachana'] }
                        plist = Subanta.analyze(split_desc)
                        if plist is None:   
                            print "Error getting praatipadika of ", p['pada_split'].encode('utf-8')
                            exit(1)
                        found = False
                        for w_p in plist:
                            w = w_p['praatipadikam']
                            found = reduce(lambda x, y: x or y,
                                [(pada == praatipadikam) 
                                    for pada in w.split('-')])
                            if found:
                                break
                        if found:
                            continue
                    #print_dict(p)
                    v_desc = p['vibhakti'] if 'vibhakti' in p else -1
                    def_padas.append("{}({})".format(p['pada'].encode('utf-8'), v_desc))
                    defn.append(p)
                self.terms_db[praatipadikam]['defns'].append({'sutra_id' : snum, 'defn' : defn})
                term_defs_str += "{}: {} = {}\n".format(snum, praatipadikam, ' '.join(def_padas))

        print "Listing members of some samjnas .."
        self.find_listable_terms()
        print "Converting Samjna sutras into processing rules .."
        self.compile_term_rules()

        with open(outpath("terms.json"), "w") as f:
            stext = json.dumps(self.terms_db, indent=4, ensure_ascii=False, separators=(',', ': '))
            f.write(stext.encode('utf-8') + "\n")

        with open(outpath("term_defs_slp1.txt"), "w") as f:
            term_defs_slp1 = xliterate(term_defs_str)
            f.write(term_defs_slp1)

        print "Computing definitions of Pratyaharas .."
        #self.compute_pratyaharas()

    def build_mahavakyas(self):
        for snum in self.sutras():
            sutra = self.sutra(snum)
            if 'mahavakya_padacCheda' not in sutra:
                sutra['mahavakya_padacCheda'] = self.mahavakya_padacCheda(snum)
       
    def mahavakya_padacCheda(self, sutra_id):
        sutra = self.sutra(sutra_id)
        if not sutra:
            return None

        new_vaakya = []
        if 'Anuvrtti' in sutra:
            for vrttam in sutra['Anuvrtti']:
                prev_id = str(vrttam['sutra'])
                prev_sutra = self.sutra(prev_id)
                prev_padaccheda = prev_sutra['PadacCheda']

                praatipadikas = []
                for p in vrttam['padas']:
                    for prevp in prev_padaccheda:
                        if self.equal_dvng(p, prevp['pada']):
                            new_vaakya.append(prevp)
                            praatipadikas.append(Subanta.praatipadikam(prevp))
                            break
                vrttam['praatipadikas'] = praatipadikas
                #print "{}: {}".format(sutra_id, praatipadikas)

        new_vaakya.extend(sutra['PadacCheda'])
        return new_vaakya

_ashtadhyayi = None
def ashtadhyayi():
    global _ashtadhyayi
    if not _ashtadhyayi:
        config_init()
        _ashtadhyayi = Ashtadhyayi(datapath(My_config.sutras_json_file))
    return _ashtadhyayi

class Paribhasha:
    def __init__(self, sutra_id, defs):
        self.defs = defs
        self.sutra_id = sutra_id
        self.a = ashtadhyayi()
        self.sutra = self.a.sutra(sutra_id)

    def applies(self, sutra):
        found = False
        modifications = []
        for m in self.defs:
            cond = m['cond']
            action = m['action']
            if isinstance(m['cond'], dict) and self.a._propmatch(sutra, cond):
                modifications.append({ 'cond' : cond, 'action' : action })
        return modifications

    def matching_sutras(self):
    	return (snum for snum in self.a.sutra_ids \
            if len(self.applies(self.a.sutra(snum))) > 0)

    def action(self, sutra):
        return sutra

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Usage: " + sys.argv[0] + " <sutranum>")
        print("    For sutra 1.1.1, give 11001")
        exit(1)

    sutra_id = sys.argv[1];

    a = ashtadhyayi()

    sutra = a.sutra(sutra_id)
    stext = json.dumps(sutra, indent=4, ensure_ascii=False, separators=(',', ': '))
    #print type(sutra)
    #print(byteify(sutra))
    print stext.encode('utf-8')
