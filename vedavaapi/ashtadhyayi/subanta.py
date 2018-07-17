import locale
import sys
import json
import re
import os.path
from .utils import *
from .config import *
from pprint import pprint

class Subanta:
    vibhakti_suffixes = []
    def __init__(self):
        if not Subanta.vibhakti_suffixes:
            try:
                print "Loading vibhakti suffixes .."
                with open(datapath("vibhakti_templates_slp1.json")) as f:
                    vibhakti_dict = json.load(f)
                    Subanta.vibhakti_suffixes = vibhakti_dict['suffixes']
            except Exception as e:
                print "Error loading vibhaktidictslp.json: ", e
                exit(1)

    @classmethod
    def analyze(clss, pada_desc):
        if 'vibhakti' not in pada_desc:
            return None

        pada = sanscript.transliterate(pada_desc['pada'],
                    sanscript.DEVANAGARI, sanscript.SLP1)
        if pada_desc['vibhakti'] == 0:
            # Avyayam
            return [{'praatipadikam' : pada, 'stem' : pada, 'anta' : ''}]
        vibhakti = pada_desc['vibhakti']
        vachana = pada_desc['vachana']

        matches = []
        max_len = -1
        #print s_id
        # Find vibhaktis with a maximal match of suffix
        #pprint(self.vibhakti_suffixes)
        for v_entry in clss.vibhakti_suffixes:
            v = v_entry["vibhaktis"]
            suffix_str = v[vibhakti-1][vachana-1]
            for suffix in suffix_str.split('/'):
                pada = re.sub(r'[mM]$', 'm', pada)
                suffix = re.sub(r'[mM]$', 'm', suffix)
                if pada.endswith(suffix):
                    l = len(suffix)
                    if l < max_len:
                        continue
                    elif l > max_len:
                        matches = []
                    max_len = l

                    stem = pada if l <= 0 else pada[:- l]
                    praatipadikam = stem + v_entry['anta']
                    prathamaa_rupam = stem + v[0][0]
                    #print str(vibhakti) + ", " + str(vachana) + ": " + v_entry['anta'] + " " + v_entry['linga'] + " " + pada + " -> " + praatipadikam + " -> " + prathamaa_rupam
                    matches.append({'anta' : v_entry['anta'], 
                        'linga' : v_entry['linga'], 
                        'praatipadikam' : praatipadikam, 'stem' : stem})
        return matches

    @staticmethod
    def praatipadikam(pada_desc):
        if 'analysis' not in pada_desc or \
                len(pada_desc['analysis']) == 0:
            return None
        praatipadikam = pada_desc['analysis'][0]['praatipadikam']
        return praatipadikam if praatipadikam else None

Subanta()
