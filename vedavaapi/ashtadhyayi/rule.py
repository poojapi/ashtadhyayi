#!/usr/bin/python
# -*- coding: utf-8 -*-

from .subanta import *

class Rule:

    def __init__(self, ashtadhyayi, term_slp1, rule = None):
        self.a = ashtadhyayi
        self.samjna = term_slp1
        self.rule = rule

        self.IF = self._if
        self.IFNOT = self._ifnot
        self.INTERPRET = self._interpret
        self.UNION = self._union
        self.PIPE = self._pipe
        self.GEN_SAMJNA = self._gen_samjna
        self.GEN_SEQ = self._gen_sequence

        #global IF

        # Key should be in SLP1 format
        self.predefined_funcs = {
            'antya' : lambda x: Subanta.praatipadikam(x)[-1],
            'Adi' : lambda x: Subanta.praatipadikam(x)[0],
            'upadeSa' : self.a.is_upadesha,
            'hal' : lambda x: x if x['pada'] == 'hal' else None,
            'Sabda' : lambda x: list(x)
        }

    def _apply_func(self, pada_desc, func_desc):
        if isinstance(func_desc, list):
            f = self._apply_func(pada_desc, func_desc[0])
            return f(pada_desc, func_desc[1:]) if f else None
        elif isinstance(func_desc, dict):
            return self._interpret(pada_desc, func_desc)
        elif isinstance(func_desc, str):
            print func_desc
            f = eval("self."+func_desc)
            return f
        else:
            return None

    # Return pada_desc if cond applies to it, None otherwise
    def _if(self, pada_desc, cond):
        if isinstance(cond, list):
            res = reduce((lambda x, y: x and y), 
                (self._interpret(pada_desc, c) for c in cond))
        else:
            res = self._interpret(pada_desc, cond)

        return pada_desc if res else None

    def _ifnot(self, pada_desc, cond):
        if not self._if(pada_desc, cond):
            return pada_desc
        # Remove attribute from pada_desc named by the samjna
        pada_desc[self.samjna].pop(self.samjna, None)


    def _gen_sequence(self, pada_desc, seq_desc):
        first = self._apply_func(pada_desc, seq_desc[0])
        if not first:
            return None
        elif isinstance(first, list):
            first = first[0]
        last = self._apply_func(pada_desc, seq_desc[1])
        if not last:
            return None
        elif isinstance(last, list):
            last = last[0]
        seq = self.a.gen_sequence(first, last)
        print "gen_sequence({}, {}) = {}".format(first, last, seq)
        return seq

    def _gen_samjna(self, pada_desc, parms):
        defn = parms[0]
        res = self._apply_func(pada_desc, defn['samjna'])
        if not res:
            return None
        self.samjna = Subanta.praatipadikam(pada_desc)
        if defn['samjni']:
            res = self._apply_func(pada_desc, defn['samjni'])
        return res

    def _interpret(self, pada_desc, func_desc):
        sutra_pada = func_desc['pada']
        print "Sutra padam ", sutra_pada
        praatipadikam = Subanta.praatipadikam(func_desc)
        print "Sutra praatipadikam ", praatipadikam
        res = None
        if praatipadikam is 'na':
            # Remove attribute from pada_desc named by the samjna
            pada_desc[self.samjna].pop(self.samjna, None)
            return res
        elif praatipadikam in self.predefined_funcs:
            res = self.predefined_funcs[praatipadikam](pada_desc)
        elif praatipadikam in pada_desc['samjnas']:
            res = pada_desc['samjnas'][praatipadikam]
            res = [pada_desc['pada'][i] for i in res]
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
        intersect = set()
        for f in func_descs:
            res = self._apply_func(pada_desc, f)
            print "pipe component result", res
            if not res:
                return None
            intersect = intersect & set(res) if intersect else set(res)
            if not intersect:
                return None
        print "Pipe result: ", intersect
        return res

    # Split given property list into those matching or not matching the cond. 
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
        match, rest = self.bifurcate(rest, {'analysis' : {'praatipadikam' : 'sva'} })
        if match:
            #print "Entered sva"
            match, rest = self.bifurcate(rest, {'analysis' : {'praatipadikam' : 'rUpa'} })
            if match:
                #print "Entered rUpa"
                p6, rest = self.bifurcate(rest, {'vibhakti' : 6})
                samjna = self._compile(rest) if rest else None
                if p6:
                    func_descs.extend(["GEN_SAMJNA", 
                        { 'samjni' : ["PIPE"] + p6, 'samjna' : samjna }])
                else:
                    func_descs.extend(["GEN_SAMJNA", 
                        { 'samjni' : None, 'samjna' : samjna }])
                    
                return func_descs

        p6, rest = self.bifurcate(rest, {'vibhakti' : 6})
        if p6:
            func_descs.append(["PIPE"] + p6)

        match, rest = self.bifurcate(rest, {'pada' : 'na', 'vibhakti' : 0})
        if match:
            if rest:
                subrule = self._compile(rest)
                func_descs.append(["IFNOT", subrule])
                return func_descs

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
