#!/usr/bin/python

import sys
from ashtadhyayi.cmdline import *

if len(sys.argv) > 1:
    pada = sys.argv[1]
if len(sys.argv) > 2:
    vibhakti = int(sys.argv[2])
if len(sys.argv) > 3:
    vachana = int(sys.argv[3])
print_dict(praatipadika(sys.argv[1], vibhakti, vachana))
