#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from vedavaapi.ashtadhyayi.cmdline import *

if (len(sys.argv) < 2):
    print("Usage: " + sys.argv[0] + " <sutranum>")
    print("    For sutra 1.1.1, give 11001")
    exit(1)

print "Mahavakya of " + sys.argv[1]
x = mahavakya(sys.argv[1])
print_dict(x)
exit(0)
