#!/usr/bin/python
# -*- coding: utf-8 -*-

from .subanta import *

class Rule:
    def __init__(self, ashtadhyayi, term_slp1, rule = None):
        self.a = ashtadhyayi
        self.samjna = term_slp1
        self.rule = rule

        global IF
        IF = self._if
        global INTERPRET
        INTERPRET = self._interpret
        global UNION
        UNION = self._union
        global PIPE
        PIPE = self._pipe
        global GEN_SAMJNA
        GEN_SAMJNA = self._gen_samjna
        global GEN_SEQ
        GEN_SEQ = self._gen_sequence

        # Key should be in SLP1 format
        self.predefined_funcs = {
            'antya' : lambda x: Subanta.praatipadikam(x)[-1],
            'Adi' : lambda x: Subanta.praatipadikam(x)[0],
            'upadeSa' : self.a.is_upadesha,
            'hal' : lambda x: x if x['pada'] == 'hal' else None,
            'Sabda' : lambda x: list(x)
        }

    def _apply_func(self, pada_desc, func_desc):
        if isinstance(func_desc[0], str):
            f = eval(func_desc[0])
        else:
            f = INTERPRET
        parms = func_desc[1:]
        return f(pada_desc, parms)

    # Return pada_desc if cond applies to it, None otherwise
    def _if(self, pada_desc, cond):
        if isinstance(cond, list):
            res = reduce((lambda x, y: x and y), 
                (self._interpret(pada_desc, c) for c in cond))
        else:
            res = self._interpret(pada_desc, cond)

        return pada_desc if res else None

    def _ifnot(self, pada_desc, cond):
        return None if self._if(pada_desc, cond) else pada_desc

    def _gen_samjna(self, pada_desc, defn):
        res = self.apply(defn['samjna'])

    def _gen_sequence(self, pada_desc, seq):
        startc, endc = seq[0], seq[1]
        print startc, endc
        return startc
        

    def _interpret(self, pada_desc, parms):
        sutra_pada = parms[0]
        praatipadikam = Subanta.praatipadikam(sutra_pada)
        print "Sutra padam ", praatipadikam
        res = None
        if praatipadikam is 'na':
            pada_desc[self.samjna].pop(self.samjna, None)
            return res
        elif praatipadikam in self.predefined_funcs:
            res = self.predefined_funcs[praatipadikam](pada_desc)
        elif self.a.is_samjna(sutra_pada): 
            samjna_desc = self.a.terms_db[praatipadikam]
            if 'members' in samjna_desc:
                for t in samjna_desc['members']:
                    if Subanta.praatipadikam(pada_desc) == t:
                        return pada_desc
                return None
            for defn in samjna_desc['defns']:
                if 'rule' not in defn:
                    continue
                res = Rule(self.a, praatipadikam, defn['rule']).apply(pada_desc)
                if res:
                    break
        elif praatipadikam.startswith('a'):
            pada = sutra_pada.copy()
            pada['pada'] = pada['pada'][1:]
            pada['analysis'][0]['praatipadikam'] = pada['analysis'][0]['praatipadikam'][1:]
            if self.a.is_samjna(pada):
                res = self._interpret(pada_desc, [pada])
                return not res
        print "Interpreted result: ", res
        return res

    def _union(self, pada_desc, func_descs):
        return reduce((lambda x, y: x + y), 
            [self._apply_func(pada_desc, f) for f in func_descs])

    def _pipe(self, pada_desc, func_descs):
        res = pada_desc
        for f in func_descs:
            res = self._apply_func(res, f)
            if not res:
                break
        print "Pipe result: ", res
        return res

    def bifurcate(self, plist, cond):
        matches = []
        rest = []
        for p in plist:
            if self.a._propmatch(p, cond):
                matches.append(p)
            else:
                rest.append(p)
        return (matches, rest)

    def _compile(self, plist):
        func_descs = []
        p7, rest = self.bifurcate(plist, {'vibhakti' : 7})
        if p7:
            func_descs = ["PIPE", ["IF"] + p7]

        # Handle generated Samjna names
        match, rest = self.bifurcate(rest, {'analysis' : {'praatipadika' : 'sva'} })
        if match:
            match, rest = self.bifurcate(rest, {'analysis' : {'praatipadika' : 'rUpa'} })
            if match:
                p6, rest = self.bifurcate(rest, {'vibhakti' : 6})
                samjna = self._compile(rest) if rest else None
                if p6:
                    func_descs.append(["GEN_SAMJNA", 
                        { 'samjni' : ["PIPE"] + p6, 'samjna' : samjna }])
                else:
                    func_descs.append(["GEN_SAMJNA", 
                        { 'samjni' : None, 'samjna' : samjna }])
                    
                return func_descs

        p6, rest = self.bifurcate(rest, {'vibhakti' : 6})
        if p6:
            func_descs.append(["PIPE"] + p6)

        p1, rest = self.bifurcate(rest, {'vibhakti' : 1})
        match, rest = self.bifurcate(rest, {'pada' : 'saha', 'vibhakti' : 0})
        if match:
            p3, rest = self.bifurcate(rest, {'vibhakti' : 3})
            return ["GEN_SEQ", ["PIPE"] + p1, ["PIPE"] + p3]
        
        func_descs.append(["PIPE"] + p1)
        return func_descs

        #plist = sorted(plist, key=lambda k: k['vibhakti'] if ('vibhakti' in k) else 0, reverse=True)
        #for i in range(8):
        #    padas.append([p for p in plist if 'vibhakti' in p and p['vibhakti'] == i])

#        for i in range(plist):
#            p = plist[i]
#            if p['pada'] == 'saha':
#                p1 = filter(lambda p: 'vibhakti' in p and p['vibhakti'] == 1, plist)
#                p3 = filter(lambda p: 'vibhakti' in p and p['vibhakti'] == 3, plist)
#                func = ['SAHA', ["PIPE", p1], ["PIPE", p3]]
#                    
#        if padas[7]:
#            func_descs.append(["PIPE"] + [["IF", p] for p in padas[7]])
#        if padas[6]:
#            func_descs.append(["PIPE"] + [["IF", p] for p in padas[6]])
#        if padas[5]:
#            #func_descs.append(["PIPE"] + [["PARAM", p] for p in padas[5]])
#            pass
#        if padas[3]:
#            func_descs.append(["PIPE"] + [["WITH", p] for p in padas[3]])
#        if padas[1]:
#            func_descs.append(["PIPE"] + [["INTERPRET", p] for p in padas[1]])
#        if padas[0]:
#            func_descs.append(["PIPE"] + [["INTERPRET", p] for p in padas[0]])
#
#        self.rule = ["PIPE"] + func_descs
#        #print_dict(self.rule)
#        return self.rule

    def compile(self, plist):
        self.rule = self._compile(plist)
        return self.rule

    def __repr__(self):
        return self.rule

    def apply(self, pada_desc):
        res = self._apply_func(pada_desc, self.rule)
        if res:
            if self.samjna not in pada_desc:
                pada_desc[self.samjna] = []
            pada_desc[self.samjna].append(res)
        return res
