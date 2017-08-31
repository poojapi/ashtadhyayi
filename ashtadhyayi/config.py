import os.path
from .utils import *

My_config = DotDict({
    "sutras_json_file" : "ashtadhyayi-sutras.json",
    "rootdir" : os.path.dirname(os.path.realpath(__file__))
    })

def getpath(fname):
    return os.path.join(My_config['rootdir'], fname)
