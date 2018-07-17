#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from vedavaapi.ashtadhyayi.utils import *
from vedavaapi.ashtadhyayi.cmdline import *


print "Paribhasha of " + sys.argv[1]
x = paribhasha(sys.argv[1])
#print_dict(x)

a_obj = a()
exit(0)
for s_id in a().sutras({'Sutra_type' : "संज्ञा"}):
    s = a().sutra(s_id)
    print_dict({ 'id' : s_id, 
        'mahavakya_padacCheda' : s['mahavakya_padacCheda'] })
