#!/usr/bin/python
# -*- coding: utf-8 -*-

#from .service import *
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
        global NOT
        NOT = self._not

    def _apply_func(self, pada_desc, func_desc):
        f = eval(func_desc[0])
        parms = func_desc[1:]
        return f(pada_desc, parms)

    def _if(self, pada_desc, cond):
        if self._interpret(pada_desc, cond):
            return pada_desc
        else:
            return None

    def _not(self, pada_desc, cond):
        if not pada_desc:
            return True
        else:
            return None

    def _interpret(self, pada_desc, parms):
        sutra_pada = parms[0]
        praatipadikam = Subanta.praatipadikam(sutra_pada)
        print "Sutra padam ", praatipadikam
        res = None
        if praatipadikam is 'na':
            pada_desc[self.samjna].pop(self.samjna, None)
            return res
        elif praatipadikam in self.a.predefined_funcs:
            res = self.a.predefined_funcs[praatipadikam](pada_desc)
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

    def compile(self, plist):
        padas = []
        for i in range(8):
            padas.append([p for p in plist if 'vibhakti' in p and p['vibhakti'] == i])
        

        func_descs = []
        if padas[7]:
            func_descs.append(["PIPE"] + [["IF", p] for p in padas[7]])
        if padas[6]:
            func_descs.append(["PIPE"] + [["IF", p] for p in padas[6]])
        if padas[5]:
            #func_descs.append(["PIPE"] + [["PARAM", p] for p in padas[5]])
            pass
        if padas[1]:
            func_descs.append(["PIPE"] + [["INTERPRET", p] for p in padas[1]])
        if padas[0]:
            func_descs.append(["PIPE"] + [["INTERPRET", p] for p in padas[0]])

        self.rule = ["PIPE"] + func_descs
        #print_dict(self.rule)
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
