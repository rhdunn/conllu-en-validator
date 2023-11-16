# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


def lowercase_form_lemma(form):
    return form.lower().replace('’', '\'')


lemmatization_rules = {
    'lowercase-form': lowercase_form_lemma,
}

xpos_lemmatization_rule_names = {
    'DT': 'lowercase-form',  # determiner
    'RB': 'lowercase-form',  # adverb
    'TO': 'lowercase-form',  # "to"
}

lemma_exceptions = {
    'DT': {  # determiners
        'an': 'a',
        'these': 'this',
        'those': 'these',
    },
    'RB': {  # adverbs
        # PART
        'n\'t': 'not',
        'n`t': 'not',
        'nt': 'not',
        # uppercase abbreviations
        'ad': 'AD',  # Anno Domini
        'asap': 'ASAP',  # as soon as possible
        'bc': 'BC',  # Before Christ
        'bce': 'BCE',  # Before the Common/Current/Christian Era
        'btw': 'BTW',  # by the way
        'ce': 'CE',  # Common/Current/Christian Era
        'e': 'E',  # east
        'iirc': 'IIRC',  # if I remember correctly
        'imo': 'IMO',  # in my opinion
        'irl': 'IRL',  # in real life
        'n': 'N',  # north
        'ps': 'PS',  # postscript
        's': 'S',  # south
        'w': 'W',  # west
        # dotted abbreviations
        'aka': 'a.k.a.',  # also known as
    },
    'TO': { # PART+TO -- "to"
        'na': 'to',  # wan|na, etc.
        'ta': 'to',  # got|ta, etc.
    }
}


class TokenLemmaValidator(Validator):
    def __init__(self, language):
        super().__init__(language)

    def validate_lemma(self, sent, token, rule, form, lemma, xpos):
        lower_form = lemmatization_rules[rule](form)
        if lower_form == lemma:
            pass  # matched
        elif xpos in lemma_exceptions and lower_form in lemma_exceptions[xpos]:
            pass  # matched via a special case
        else:
            log(LogLevel.ERROR, sent, token,
                f"{token['xpos']} lemma '{lemma}' does not match {rule} applied to form '{form}'")

    def validate_token(self, sent, token):
        form = conllutil.normalized_form(token)
        lemma = token['lemma']
        xpos = token['xpos']
        if lemma is None or lemma == '_':
            if token['upos'] == 'X' and token['deprel'] == 'goeswith':
                pass  # goeswith have `_` as the lemma
            elif lemma == '_' and xpos == 'NFP':
                pass  # underscore as an actual lemma, not a missing entry
            else:
                log(LogLevel.ERROR, sent, token, f"missing lemma text")
        elif form is None:
            pass  # Missing form text is reported by the 'form' validator.
        elif xpos in xpos_lemmatization_rule_names:
            rule = xpos_lemmatization_rule_names[xpos]
            self.validate_lemma(sent, token, rule, form, lemma, xpos)
        else:
            pass
