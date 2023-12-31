# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator.validator import Validator
from validator.logger import log, LogLevel

upos_values = [
    '_',      # missing
    # open class words
    'ADJ',    # adjective
    'ADV',    # adverb
    'INTJ',   # interjection
    'NOUN',   # noun
    'PROPN',  # proper noun
    'VERB',   # verb
    # closed class words
    'ADP',    # adposition
    'AUX',    # auxiliary verb
    'CCONJ',  # coordinating conjunction
    'DET',    # determiner
    'NUM',    # number
    'PART',   # part
    'PRON',   # pronoun
    'SCONJ',  # subordinating conjunction
    # other
    'PUNCT',  # punctuation
    'SYM',    # symbol
    'X',      # other
]

upenn_xpos_values = [
    "ADD", "AFX",
    "CC", "CD",
    "DT",
    "EX",
    "FW",
    "GW",
    "HYPH",
    "IN",
    "JJ", "JJR", "JJS",
    "LS",
    "MD",
    "NFP", "NN", "NNP", "NNPS", "NNS",
    "PDT", "POS", "PRP", "PRP$",
    "RB", "RBR", "RBS", "RP",
    "SYM",
    "TO",
    "UH",
    "VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
    "WDT", "WP", "WP$", "WRB",
    "$", ".", ",", ":", "``", "''",
    "-LCB-", "-RCB-", "-LRB-", "-RRB-", "-LSB-", "-RSB-",
]


class PosTagValidator(Validator):
    def __init__(self, language):
        super().__init__(language)

    def validate_token(self, sent, token):
        upos = token['upos']
        xpos = token['xpos']
        if upos not in upos_values:
            log(LogLevel.ERROR, sent, token, f"unknown UPOS value '{upos}'")
        if self.language == 'en' and xpos not in upenn_xpos_values:
            log(LogLevel.ERROR, sent, token, f"unknown XPOS value '{xpos}'")
