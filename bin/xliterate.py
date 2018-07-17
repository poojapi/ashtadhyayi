#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import fileinput
import locale
from vedavaapi.utils import *
from indic_transliteration import sanscript

rmchars = [ u"\uFEFF", u"\u200c", u"\u200d", u"\u201c", u"\u201d" ]
word_dict = {}

#if len(sys.argv) < 3:
#    print "Usage: xliterate.py <from_script> <to_script>\
#    Where from_script and to_script can DEVANAGARI, HK, ITRANS, SLP1 or WX"
#    exit(1)
#    
#from_script = sys.argv[1]
#to_script = sys.argv[2]
from_script = sanscript.DEVANAGARI
to_script = sanscript.ITRANS

linenum = 0
for line in fileinput.input():
    linenum = linenum + 1
    l = line.rstrip()
    try:
        l = l.encode('utf-8')
    except Exception as e:
        print "Skipping invalid line ", linenum
        continue
    for c in rmchars:
        l = l.replace(c, '')
    #l = sanscript.transliterate(l, from_script, to_script)
    print l
