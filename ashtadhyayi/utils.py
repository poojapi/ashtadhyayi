# -*- coding: utf-8 -*-

import locale
import sys
import json

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

