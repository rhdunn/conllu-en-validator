# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


def apply_stemming_rules(form, rules):
    for ending, replacement in rules:
        if form.endswith(ending):
            return form[:-len(ending)] + replacement
    return form


def lowercase_form_lemma(form):
    normalized = form.lower().replace('’', '\'')
    return normalized, normalized


def plural_noun_lemma(form):
    normalized, _ = lowercase_form_lemma(form)
    if normalized in plural_noun_unmodified_lemma:
        return normalized, normalized
    return normalized, apply_stemming_rules(normalized, plural_noun_stemming_rules)



lemmatization_rules = {
    'lowercase-form': lowercase_form_lemma,
    'plural-noun': plural_noun_lemma,
}

plural_noun_stemming_rules = [
    ('ches', 'ch'),
    ('shes', 'sh'),
    ('sses', 'ss'),
    ('ies', 'y'),
    ('xes', 'x'),
    ('s', ''),
    ('men', 'man'),
]

plural_noun_unmodified_lemma = [
    'series',
    'species',
    # numbers
    'tens', 'mid-tens',
    'twenties', 'mid-twenties',
    'thirties', 'mid-thirties',
    'fourties', 'mid-fourties',
    'fifties', 'mid-fifties',
    'sixties', 'mid-sixties',
    'seventies', 'mid-seventies',
    'eighties', 'mid-eighties',
    'nineties', 'mid-nineties',
]

xpos_lemmatization_rule_names = {
    'DT': 'lowercase-form',  # determiner
    'EX': 'lowercase-form',  # existential "there"
    'NNS': 'plural-noun',  # noun, plural
    'RB': 'lowercase-form',  # adverb
    'TO': 'lowercase-form',  # "to"
}

lemma_exceptions = {
    'DT': {  # determiners
        'an': 'a',
        'these': 'this',
        'those': 'these',
    },
    'NNS': { # plural nouns
        'children': 'child',
        'feet': 'foot',
        'mice': 'mouse',
        'people': 'person',
        'teeth': 'tooth',
        # -ches exceptions
        'aches': 'ache',
        'caches': 'cache',
        'headaches': 'headache',
        'heartaches': 'heartache',
        'niches': 'niche',
        # -ies exceptions
        'budgies': 'budgie',
        'cookies': 'cookie',
        'hippies': 'hippie',
        'kiddies': 'kiddie',
        'lies': 'lie',
        'monies': 'money',
        'movies': 'movie',
        'newbies': 'newbie',
        'pies': 'pie',
        'pinkies': 'pinkie',
        'pixies': 'pixie',
        'ties': 'tie',
        'yachties': 'yachtie',
        # -ives
        'knives': 'knife',
        'lives': 'life',
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
        normalized_form, expected_lemma = lemmatization_rules[rule](form)
        if xpos in lemma_exceptions and normalized_form in lemma_exceptions[xpos]:
            # use the exception lemma instead of the rule-based lemma
            expected_lemma = lemma_exceptions[xpos][normalized_form]
        if expected_lemma == lemma:
            pass  # matched via lemmatization rule
        else:
            log(LogLevel.ERROR, sent, token,
                f"{token['xpos']} lemma '{lemma}' does not match {rule} applied to form '{form}', expected '{expected_lemma}'")

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
