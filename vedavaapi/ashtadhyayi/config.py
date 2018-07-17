import os.path
from os.path import dirname, realpath, join, exists
from .utils import *

My_config = DotDict({
    "sutras_json_file" : "ashtadhyayi-sutras.json",
    "rootdir" : dirname(realpath(__file__)),
    "datadir" : join(dirname(realpath(__file__)), "data"),
    "outdir" : "/tmp/vedavaapi/ashtadhyayi/data"
    })

def getpath(fname):
    return join(My_config['rootdir'], fname)

def outpath(fname):
    return join(My_config['outdir'], fname)

def datapath(fname):
    return join(My_config['datadir'], fname)

def config_init():
    try:
        if not exists(My_config['outdir']):
            os.makedirs(My_config['outdir'])
    except Exception as e:
        print "Abort: Couldn't create directory {}: {}".format(My_config['outdir'], e)
        exit(1)
