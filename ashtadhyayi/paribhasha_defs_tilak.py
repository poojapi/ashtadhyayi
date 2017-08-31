#!/usr/bin/python
# -*- coding: utf-8 -*-

from ashtadhyayi import ashtadhyayi as a
from ashtadhyayi import Paribhasha
from pprint import pprint

def sutra_add_pada(sutra, pada_desc):
    out_sutra = sutra.copy()
    out_sutra['PadacCheda'].insert(0, pada_desc)
    return out_sutra


AND = a()._and
OR = a()._or
NOT = a()._not
SAMJNA = a().is_samjna
PRATYAYA = a().is_pratyaya
IT_ENDING = a().it_ending
        
paribhasha_defs = {
    str(11003) : [
            {
                "cond" : {
                    "mahavakya_PadacCheda" : {
                        "pada" : ["गुणः", "वृद्धिः"],
                        "vibhakti" : 1
                        },
                    "Sutra_type" : ["विधिः"]
                },
                "action" : lambda x: x
            }
        ],
    str(11046) : [
            {
                "cond" : {
                    "PadacCheda" : 
                        [AND, [[NOT, SAMJNA], [NOT, PRATYAYA],
                               [IT_ENDING, { "varna" : "ट्" } ]]],
                    "Sutra_type" : ["विधिः"]
                },
                "action" : [
                    sutra_add_pada, { "pada" : "षष्ठ्यन्तस्य",  "vibhakti" : 6, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "आदिः",  "vibhakti" : 1, 'type' : "सुबन्त"}
                    ]
            },
            {
                "cond" : {
                    "PadacCheda" : 
                        [AND, [[NOT, SAMJNA], [NOT, PRATYAYA],
                               [IT_ENDING, { "varna" : "क्"} ]]],
                    "Sutra_type" : ["विधिः"]
                },
                "action" : [
                    sutra_add_pada, { "pada" : "षष्ठ्यन्तस्य",  "vibhakti" : 6, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "अन्तः", "vibhakti": 1, 'type' : "सुबन्त"}
                    ]
            }
        ],
    str(11047) : [
            {
                "cond" : {
                    "PadacCheda" : 
                        [AND, [[NOT, SAMJNA],
                               [IT_ENDING, { "varna" : "म्" } ]]],
                    "Sutra_type" : ["विधिः"]
                },
                "action" : [
                    sutra_add_pada, { "pada" : "षष्ठ्यन्तस्य",  "vibhakti" : 6, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "अन्त्यात्",  "vibhakti" : 5, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "अचः",  "vibhakti" : 5, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "परः",  "vibhakti" : 1, 'type' : "सुबन्त"}
                    ]
            }
        ],
     str(11048) : [
            {
                "cond" : {
                    "PadacCheda" : {
                        "pada" : ["ह्रस्वः"],
                        "vibhakti" : 1
                        },
                    "Sutra_type" : ["विधिः"]
                },
               "action" : [
                    sutra_add_pada, { "pada" : "एचः",  "vibhakti" : 6, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "चेत्",  "vibhakti" : 0, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "इक्",  "vibhakti" : 1, 'type' : "सुबन्त"},
                    ]
	     }		
	],
    str(11049) : [
            {
                "cond" : {
                    "PadacCheda" :{ 
                        "type" : ["सुबन्त"],
			"vibhakti" : 6 
			},
                       "Sutra_type" : ["विधिः"]
                },
               "action" : [
                    sutra_add_pada, { "pada" : "एचः",  "vibhakti" : 6, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "चेत्",  "vibhakti" : 0, 'type' : "सुबन्त"},
                    sutra_add_pada, { "pada" : "इक्",  "vibhakti" : 1, 'type' : "सुबन्त"},
                    ]
	     },		
	]
}

def get_paribhasha(sutra_id):
    return Paribhasha(sutra_id, paribhasha_defs[str(sutra_id)])
