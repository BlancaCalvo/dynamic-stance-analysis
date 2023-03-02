#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 10:19:24 2022
Permet calcular el IAA entre dos llistes de spans.
Implementació de la funció descrita aquí https://arxiv.org/pdf/1803.08614.pdf
@author: Ona de Gibert
"""
# Usage: add two lists of spans separated by commas
# python3 funcions_spans.py char 2:17 3:10,12:17
# python3 funcions_spans.py token hola,que,tal adeu,tal,que
# python3 funcions_spans.py string hola,que,tal adeu,tal,que

import sys
import re

def agreement(spans_x, spans_y):
    if not spans_x or not spans_y and spans_x != spans_y:
        agreement = 0
    elif not spans_x and not spans_y :
        agreement = 1
    else:
        agreement = len(set(spans_x).intersection(spans_y))/len(spans_x)
    return agreement

def avg_agreement(level, spans_a_raw, spans_b_raw): # each spans_x is a list of strings from both annotators
    #By default, level == string and formula from Wiebe et al.(2005)
    spans_a = []
    spans_b = []
    if level == 'string':
        spans_a = spans_a_raw#.split(",")
        spans_b = spans_b_raw#.split(",")
    if level == 'token':
        max_spans = max(len(spans_a_raw), len(spans_b_raw))
        for i in range(max_spans):
            try:
                spans_a = re.split(r'\W',spans_a_raw[i])
            except IndexError:
                continue
            try:
                spans_b = re.split(r'\W',spans_b_raw[i])
            except IndexError:
                continue
    elif level == 'char':
        for span in spans_a_raw:
            onset, offset = span.split(':')
            spans_a.extend(range(int(onset), int(offset)))
        for span in spans_b_raw:
            onset, offset = span.split(':')
            spans_b.extend(range(int(onset), int(offset)))
    spans_a_gs = agreement(spans_a, spans_b)
    spans_b_gs = agreement(spans_b, spans_a)
    avg_agreement = round((spans_a_gs+spans_b_gs)/2,2)
    return avg_agreement

def spans_iaa(spans_a, spans_b, level='token'):
    #level = sys.argv[1] #This should be char, token or string
    #spans_a = sys.argv[2]
    #spans_b = sys.argv[3]
    if len(spans_a) == 0 and len(spans_b) == 0:
        agreement = 1
    else:
        if level == 'char':
            spans_a = list(spans_a.split(','))
            spans_b = list(spans_b.split(','))
        agreement =  avg_agreement(level, spans_a, spans_b)

    return agreement

#if __name__ == "__main__":
#    main()