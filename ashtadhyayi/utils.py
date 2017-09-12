# -*- coding: utf-8 -*-

import locale
import sys
import json
from indic_transliteration import sanscript

def utf8_decode(string):
    return string.decode('utf-8')

def print_dict(mydict):
    stext = json.dumps(mydict, indent=4, ensure_ascii=False, separators=(',', ': '))
    print stext.encode('utf-8')

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

class DotDict(dict):
    def __getattr__(self, name):
        return self[name]

_rmchars = [ u"\uFEFF", u"\u200c", u"\u200d", u"\u201c", u"\u201d" ]
def xliterate(mystr, from_script = "DEVANAGARI", to_script = "SLP1"):
    from_script = eval("sanscript." + from_script)
    to_script = eval("sanscript." + to_script)
    l = mystr.decode('utf-8')
    if isinstance(l, unicode):
        for c in _rmchars:
            l = l.replace(c, '')
        l = sanscript.transliterate(l, from_script, to_script)
    return l
