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
    # suffices and compound words
    ('children', 'child'),
    ('men', 'man'),
]

lemmatization_rule_names = {
    'DT': 'lowercase-form',  # determiner
    'EX': 'lowercase-form',  # existential "there"
    'NNS/Number=Coll': 'lowercase-form',  # noun, collective / singulare tantum (singular form as plural)
    'NNS/Number=Plur': 'plural-noun',  # noun, plural
    'NNS/Number=Ptan': 'lowercase-form',  # noun, plurale tantum (plural form lemma)
    'RB': 'lowercase-form',  # adverb
    'TO': 'lowercase-form',  # "to"
}

lemma_exceptions = {
    'DT': {  # determiners
        'an': 'a',
        'these': 'this',
        'those': 'that',
    },
    'NNS/Number=Plur': { # plural nouns
        'analyses': 'analysis',
        'appendices': 'appendix',
        'bases': ['base', 'basis'],
        'biases': 'bias',
        'buses': 'bus',
        'censuses': 'census',
        'criteria': 'criterion',
        'feet': 'foot',
        'gases': 'gas',
        'geniuses': 'genius',
        'halves': 'half',
        'heroes': 'hero',
        'hypotheses': 'hypothesis',
        'indices': 'index',
        'knives': 'knife',
        'lives': 'life',
        'mice': 'mouse',
        'people': 'person',
        'potatoes': 'potato',
        'shelves': 'shelf',
        'sinuses': 'sinus',
        'species': 'specie',  # should be annotated as Number=Ptan in most cases
        'surpluses': 'surplus',
        'syntheses': 'synthesis',
        'teeth': 'tooth',
        'thieves': 'thief',
        'wives': 'wife',
        'wolves': 'wolf',
        'zeroes': 'zero',
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

    def get_lemma_type(self, token):
        xpos = token['xpos']
        if xpos == 'NNS':
            number = conllutil.get_feat(token, 'Number', None)
            if number is not None:
                return f"{xpos}/Number={number}"
        return xpos

    def match_lemma(self, lemma, expected_lemma):
        if isinstance(expected_lemma, list):
            return lemma in expected_lemma
        return lemma == expected_lemma

    def validate_lemma(self, sent, token, rule, form, lemma, lemma_type):
        normalized_form, expected_lemma = lemmatization_rules[rule](form)
        if lemma_type in lemma_exceptions and normalized_form in lemma_exceptions[lemma_type]:
            # use the exception lemma instead of the rule-based lemma
            expected_lemma = lemma_exceptions[lemma_type][normalized_form]
        if self.match_lemma(lemma, expected_lemma):
            pass  # matched via lemmatization rule
        else:
            log(LogLevel.ERROR, sent, token,
                f"{lemma_type} lemma '{lemma}' does not match {rule} applied to form '{form}', expected '{expected_lemma}'")

    def validate_token(self, sent, token):
        form = conllutil.normalized_form(token)
        lemma = token['lemma']
        if lemma is None or lemma == '_':
            if token['upos'] == 'X' and token['deprel'] == 'goeswith':
                return  # goeswith have `_` as the lemma
            if lemma == '_' and token['xpos'] == 'NFP':
                return  # underscore as an actual lemma, not a missing entry
            log(LogLevel.ERROR, sent, token, f"missing lemma text")
            return
        if form is None:
            return  # Missing form text is reported by the 'form' validator.

        lemma_type = self.get_lemma_type(token)
        if lemma_type in lemmatization_rule_names:
            rule = lemmatization_rule_names[lemma_type]
            self.validate_lemma(sent, token, rule, form, lemma, lemma_type)
