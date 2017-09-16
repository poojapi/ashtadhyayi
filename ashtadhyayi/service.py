#!/usr/bin/python
# -*- coding: utf-8 -*-

import locale
import sys
import json
import re
import os.path
from .utils import *
from .config import *
from pprint import pprint
from indic_transliteration import sanscript

AND = None
OR = None
NOT = None
SAMJNA = None
PRATYAYA = None
IT_ENDING = None
UPADESHA = None

# Key should be in SLP1 format
predefined_funcs = {
    'antyam' : lambda x: Subanta().praatipadikam(x)[-1],
    'AdiH' : lambda x: Subanta().praatipadikam(x)[0],
    'upadeSe' : UPADESHA,
    'hal_shabda' : lambda x: x if x == 'hal' else ''

}

class Subanta:
    vibhakti_suffixes = []
    def __init__(self):
        try:
            with open(datapath("vibhakti_templates_slp1.json")) as f:
                vibhakti_dict = json.load(f)
                self.vibhakti_suffixes = vibhakti_dict['suffixes']
        except Exception as e:
            print "Error loading vibhaktidictslp.json: ", e
            exit(1)

    def analyze(self, pada_desc):
        if 'vibhakti' not in pada_desc:
            return None

        pada = sanscript.transliterate(pada_desc['pada'],
                    sanscript.DEVANAGARI, sanscript.SLP1)
        if pada_desc['vibhakti'] == 0:
            # Avyayam
            return [{'praatipadikam' : pada, 'stem' : pada, 'anta' : ''}]
        vibhakti = pada_desc['vibhakti']
        vachana = pada_desc['vachana']

        matches = []
        max_len = -1
        #print s_id
        # Find vibhaktis with a maximal match of suffix
        #pprint(self.vibhakti_suffixes)
        for v_entry in self.vibhakti_suffixes:
            v = v_entry["vibhaktis"]
            suffix_str = v[vibhakti-1][vachana-1]
            for suffix in suffix_str.split('/'):
                pada = re.sub(r'[mM]$', 'm', pada)
                suffix = re.sub(r'[mM]$', 'm', suffix)
                if pada.endswith(suffix):
                    l = len(suffix)
                    if l < max_len:
                        continue
                    elif l > max_len:
                        matches = []
                    max_len = l

                    stem = pada if l <= 0 else pada[:- l]
                    praatipadikam = stem + v_entry['anta']
                    prathamaa_rupam = stem + v[0][0]
                    #print str(vibhakti) + ", " + str(vachana) + ": " + v_entry['anta'] + " " + v_entry['linga'] + " " + pada + " -> " + praatipadikam + " -> " + prathamaa_rupam
                    matches.append({'anta' : v_entry['anta'], 
                        'linga' : v_entry['linga'], 
                        'praatipadikam' : praatipadikam, 'stem' : stem})

        return matches

    def praatipadikam(self, pada_desc):
        if 'analysis' not in pada_desc or \
            len(pada_desc['analysis']) == 0:
            return None
        praatipadikam = pada_desc['analysis'][0]['praatipadikam']
        return praatipadikam if praatipadikam else None

class Ashtadhyayi:
    def __init__(self, sutras_json_file):
    	self.sutra_ids = []
        self.sutra_id_idx = {}
        self.terms_db = {}
        with open(sutras_json_file) as data_file:
            try:
                self.ashtadhyayi = json.load(data_file)
                self.sutra_ids = sorted(self.ashtadhyayi['sutras'].keys())
                for i in range(len(self.sutra_ids)):
                    self.sutra_id_idx[self.sutra_ids[i]] = i
            except ValueError as err: # catch *all* exceptions
                print("Error: Format error in JSON file: ", err, ": aborting.", sutras_json_file)
                exit(1)

        self.load_upadeshas()
        self.infer_praatipadikas()
        self.build_mahavakyas()
        self.extract_termdefs()
        self.extract_pratyayas()

#        self.funcs = ["AND", "OR", "NOT", "SAMJNA", "PRATYAYA", "IT_ENDING",
#            "UPADESHA", "INTERPRET", "IF"]
#        for f in self.funcs:
#            func = eval(f)
#            global func
#            func = self.
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
        global IF
        IF = self._if
        global INTERPRET
        INTERPRET = self._interpret
        global APPLY
        APPLY = self._apply_func

    def _and(self, pada_desc, conds):
        return reduce((lambda x, y: x and y), 
            [self._propmatch(pada_desc, c) for c in conds])

    def _or(self, pada_desc, conds):
        return reduce((lambda x, y: x or y), 
            [self._propmatch(pada_desc, c) for c in conds])

    def _apply_func(self, pada_desc, func_desc):
        f = eval(func_desc[0])
        parms = func_desc[1:]
        return f(pada_desc, parms)

    def _union(self, pada_desc, func_descs):
        return reduce((lambda x, y: x + y), 
            [self._apply_func(pada_desc, f) for f in func_descs])

    def _pipe(self, pada_desc, func_descs):
        res = pada_desc
        for f in func_descs:
            res = self._apply_func(res, f)
            if not res:
                break
        return res

    def _not(self, pada_desc, cond):
        #print_dict(pada_desc)
        #print_dict(cond)
        return not self._propmatch(pada_desc, cond)

    def _if(self, pada_desc, cond):
        if self._interpret(pada_desc, cond):
            return pada_desc
        else:
            return None

    def _interpret(self, pada_desc, sutra_pada):
        praatipadikam = Subanta().praatipadikam(sutra_pada)
        res = None
        if praatipadikam in predefined_funcs:
            res = predefined_funcs[praatipadikam](pada_desc)
        elif self.is_samjna(sutra_pada): 
            samjna_desc = self.terms_db[praatipadikam]['defns']
            for defn in samjna_desc:
                res = defn['rule'].apply(pada_desc)
                if res:
                    break
        return res

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
        praatipadikam = Subanta().praatipadikam(pada_desc)
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
        praatipadikam = Subanta().praatipadikam(pada_desc)
        for gana in self.upadesha.keys():
            if praatipadikam in self.upadesha[gana]:
                return gana
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

                p['analysis'] = Subanta().analyze(p)

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
                defn['rule'] = Rule(vibhakti_ordered).rule
                #print(defn['rule'])

    def extract_termdefs(self):
        samjna_file = outpath("terms.json")
        if os.path.isfile(samjna_file):
            with open(samjna_file) as f:
                try:
                    self.terms_db = json.load(f)
                    return
                except ValueError as err: # catch *all* exceptions
                    print("Error: Format error in JSON file: ", err, ": aborting.", samjna_file)
                
        self.terms_db = {}
        term_defs_str = ""
        for snum in self.sutras({ 'Sutra_type' : "संज्ञा" }):
            s = self.sutra(snum)
            for t in s['Term'].split():
                #print t.encode('utf-8')
                pdesc = Subanta().analyze({'pada' : t,
                    'vibhakti' : 1, 'vachana' : 1})
                #print_dict(pdesc)
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
                        plist = Subanta().analyze(split_desc)
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

        self.find_listable_terms()
        self.compile_term_rules()

        with open(outpath("terms.json"), "w") as f:
            stext = json.dumps(self.terms_db, indent=4, ensure_ascii=False, separators=(',', ': '))
            f.write(stext.encode('utf-8') + "\n")

        with open(outpath("term_defs_slp1.txt"), "w") as f:
            term_defs_slp1 = xliterate(term_defs_str)
            f.write(term_defs_slp1)

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
                            praatipadikas.append(Subanta().praatipadikam(prevp))
                            break
                vrttam['praatipadikas'] = praatipadikas
                #print "{}: {}".format(sutra_id, praatipadikas)

        new_vaakya.extend(sutra['PadacCheda'])
        return new_vaakya
       
    def extract_pratyayas(self):
        pratyaya_file = outpath("pratyayas.json")
        if os.path.isfile(pratyaya_file):
            with open(pratyaya_file) as f:
                try:
                    self.pratyayas = json.load(f)
                    return
                except ValueError as err: # catch *all* exceptions
                    print("Error: Format error in JSON file: ", err, ": aborting.", pratyaya_file)

        self.not_pratyayas = {}
        with open(datapath("pratyaya-notlist.txt")) as f:
            lines = f.readlines()
            for l in lines:
                l = l.rstrip()
                self.not_pratyayas[l.decode('utf-8')] = True
                #print l
        #stext = json.dumps(self.not_pratyayas, indent=4, ensure_ascii=False, separators=(',', ': '))
        #print(stext.encode('utf-8') + "\n")

        self.pratyayas = {}

        pratyaya = "प्रत्ययः"
        pratyaya = pratyaya.decode('utf-8')
        subanta = "सुबन्त"
        subanta = subanta.decode('utf-8')
        for snum in self.sutras({ 'Sutra_type' : "विधिः"}):
            s = self.sutra(snum)

            if 'Anuvrtti' not in s:
                continue

            # The word 'pratyayaH' should be listed as an Anuvrtti pada
            is_pratyaya = reduce(lambda x, y: x or y,
                [(pratyaya in v['padas']) for v in s['Anuvrtti']])
            if not is_pratyaya:
                continue

#            has_vibhakti5 = reduce(lambda x, y: x or y,
#                [(p['type'] == subanta and p['vibhakti'] == 5) for p in s['PadacCheda']])

            # Pick words in prathama-vibhakti as candidates
            for p in s['PadacCheda']:
                if p['type'] == subanta and p['vibhakti'] == 1:
                    pada = p['pada']
                    #print snum, pada.encode('utf-8')
                    #if pada.endswith(u"\u200C"):
                    #    continue
                    if pada not in self.pratyayas:
                        self.pratyayas[pada] = []
                    self.pratyayas[pada].append(snum)

        with open(outpath("pratyayas.json"), "w") as f:
            stext = json.dumps(self.pratyayas, indent=4, ensure_ascii=False, separators=(',', ': '))
            f.write(stext.encode('utf-8') + "\n")

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

class Rule:
    def __init__(self, plist):
        self.plist = plist
        self.rule = []
        self.compile()

    def compile(self):
        padas = []
        for i in range(8):
            padas.append([p for p in self.plist if 'vibhakti' in p and p['vibhakti'] == i])
        

        func_descs = []
        if padas[7]:
            func_descs.append(["PIPE", [["IF", p] for p in padas[7]]])
        if padas[6]:
            func_descs.append(["PIPE", [["IF", p] for p in padas[6]]])
        if padas[5]:
            func_descs.append(["PIPE", [["PARAM", p] for p in padas[5]]])
        if padas[1]:
            func_descs.append(["PIPE", [["INTERPRET", p] for p in padas[1]]])

        self.rule = ["PIPE", func_descs]
        #print_dict(self.rule)

    def __repr__(self):
        return self.rule

    def apply(self, pada_desc):
        return APPLY(pada_desc, self.rule)

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
