# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


def apply_stemming_rules(form, rules):
    for ending, replacement in rules:
        if form.endswith(ending):
            return form[:-len(ending)] + replacement
    return form


def normalized_form_lemma(form):
    for _from, _to in normalization_rules:
        form = form.replace(_from, _to)
    return form, form


def lowercase_form_lemma(form):
    return normalized_form_lemma(form.lower())


def cardinal_form_lemma(form):
    normalized, _ = normalized_form_lemma(form.lower())
    normalized = normalized.replace(',', '')
    return normalized, normalized


def fractional_form_lemma(form):
    normalized, _ = normalized_form_lemma(form.lower())
    normalized = normalized.replace(',', '.')  # German fraction forms
    return normalized, normalized


def plural_noun_lemma(form):
    normalized, _ = lowercase_form_lemma(form)
    return normalized, apply_stemming_rules(normalized, plural_noun_stemming_rules)


lemmatization_rules = {
    'cardinal-form': cardinal_form_lemma,
    'fractional-form': fractional_form_lemma,
    'lowercase-form': lowercase_form_lemma,
    'normalized-form': normalized_form_lemma,
    'plural-noun': plural_noun_lemma,
}

plural_noun_stemming_rules = [
    # suffices and compound words
    ('children', 'child'),
    ('heroes', 'hero'),
    ('men', 'man'),
    # general rules
    ('ches', 'ch'),
    ('shes', 'sh'),
    ('sses', 'ss'),
    ('ies', 'y'),
    ('xes', 'x'),
    ('s', ''),
    ('(s)', ''),
    # foreign
    ('ae', 'a'),
]

lemmatization_rule_names = {
    'CC': 'lowercase-form',  # coordinating conjunction
    'CD/NumForm=Combi': 'normalized-form',  # cardinal number, digits with a suffix
    'CD/NumForm=Digit/NumType=Card': 'cardinal-form',  # cardinal number, integer
    'CD/NumForm=Digit/NumType=Frac': 'fractional-form',  # cardinal number, fraction
    'CD/NumForm=Roman': 'normalized-form',  # cardinal number, roman numerals
    'CD/NumForm=Word': 'lowercase-form',  # cardinal number, words
    'CD+PRON': 'lowercase-form',  # cardinal number, reciprocal pronoun -- "one/PRON+CD another"
    'DT': 'lowercase-form',  # determiner
    'EX': 'lowercase-form',  # existential "there"
    'IN': 'lowercase-form',  # preposition, subordinating conjunction
    'JJ': 'lowercase-form',  # adjective
    'LS': 'normalized-form',  # list item marker
    'MD': 'lowercase-form',  # verb, modal
    'NN': 'lowercase-form',  # noun
    'NNS/Number=Coll': 'lowercase-form',  # noun, collective / singulare tantum (singular form as plural)
    'NNS/Number=Plur': 'plural-noun',  # noun, plural
    'NNS/Number=Ptan': 'lowercase-form',  # noun, plurale tantum (plural form lemma)
    'PDT': 'lowercase-form',  # predeterminer
    'POS': 'lowercase-form',  # possessive
    'PRP': 'lowercase-form',  # pronoun, personal
    'PRP$': 'lowercase-form',  # pronoun, possessive
    'RB': 'lowercase-form',  # adverb
    'RP': 'lowercase-form',  # particle
    'SYM': 'normalized-form',  # symbol
    'TO': 'lowercase-form',  # "to"
    'UH': 'lowercase-form',  # interjection
    'VB': 'lowercase-form',  # verb, base form
    'WDT': 'lowercase-form',  # determiner, wh-
    'WP': 'lowercase-form',  # pronoun, wh-
    'WP$': 'lowercase-form',  # pronoun, possessive wh-
    'WRB': 'lowercase-form',  # adverb, wh-
}

lemma_exceptions = {
    'CD/NumForm=Word': {  # cardinal numbers, word
        'b': 'billion',
        'bn': 'billion',
        'k': 'thousand',
        'm': 'million',
        't': 'trillion',
    },
    'DT': {  # determiners
        'an': 'a',
        'these': 'this',
        'those': 'that',
    },
    'MD': {  # verb, modal
        'wilt': 'will',
        # clitics
        '\'d': 'will',
        '\'ll': 'will',
        # multi-word tokens
        'ca': 'can',
        'wo': 'will',  # would
    },
    'NNS/Number=Plur': { # plural nouns
        # irregular
        'alumni': 'alumnus',
        'antipasti': 'antipasto',
        'criteria': 'criterion',
        'data': 'datum',
        'feet': 'foot',
        'media': 'medium',
        'mice': 'mouse',
        'people': 'person',
        'phenomena': 'phenomenon',
        'stimuli': 'stimulus',
        'teeth': 'tooth',
        # -s exceptions
        'analyses': 'analysis',
        'appendices': 'appendix',
        'bases': ['base', 'basis'],
        'biases': 'bias',
        'buses': 'bus',
        'cacti': 'cactus',
        'calves': 'calf',
        'censuses': 'census',
        'codices': 'codex',
        'concerti': 'concerto',
        'corpora': 'corpus',
        'crises': 'crisis',
        'gases': 'gas',
        'genitalia': 'genitale',  # unused; should be annotated as Number=Ptan
        'geniuses': 'genius',
        'graffiti': 'graffito',  # uncommon; should be annotated as Number=Ptan
        'halves': 'half',
        'hooves': 'hoof',
        'hypotheses': 'hypothesis',
        'indices': 'index',
        'knives': 'knife',
        'lives': 'life',
        'leaves': 'leaf',
        'loaves': 'loaf',
        'potatoes': 'potato',
        'quizzes': 'quiz',
        'shelves': 'shelf',
        'sinuses': 'sinus',
        'species': 'specie',  # should be annotated as Number=Ptan in most cases
        'surpluses': 'surplus',
        'syntheses': 'synthesis',
        'taxes': ['tax', 'taxis'],
        'thieves': 'thief',
        'tomatoes': 'tomato',
        'volcanoes': 'volcano',
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
    'POS': {  # possessive
        '\'': '\'s',
    },
    'PRP': {  # pronoun, personal
        'i': 'I',
        # Nominative : https://universaldependencies.org/en/pos/PRON.html#personal-pronouns
        'me': 'I',
        'us': 'we',
        'thee': 'thou',
        'him': 'he',
        'her': 'she',
        'them': 'they',
        # Independent Possessive : https://universaldependencies.org/en/pos/PRON.html#personal-pronouns
        'mine': 'my',
        'ours': 'our',
        'yours': 'your',
        'thine': 'thy',
        'hers': 'her',
        'theirs': 'their',
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
    'SYM': {  # symbol
        '\u2013': '\u002D',  # EN DASH -> HYPHEN-MINUS
        '\u2014': '\u002D',  # EM DASH -> HYPHEN-MINUS
    },
    'TO': { # PART+TO -- "to"
        'na': 'to',  # wan|na, etc.
        'ta': 'to',  # got|ta, etc.
    },
    'UH': {  # interjection
        'christ': 'Christ',
        'ok': 'OK',
        'tl;dr': 'TL;DR',
    },
    'VB': {  # verb, base form
        # clitics
        '\'ve': 'have',
        # multi-word tokens
        'no': 'know',  # du|n|no
        'wan': 'want',  # wan|na
    },
    'WP': {  # pronoun, possessive wh-
        # https://universaldependencies.org/en/pos/PRON.html#relativeinterrogative-wh-pronouns
        'whom': 'who',
        'whomever': 'whoever',
    },
}

normalization_rules = [
    ('’', '\''),
    ('æ', 'ae'),
]


class TokenLemmaValidator(Validator):
    def __init__(self, language):
        super().__init__(language)

    def get_lemma_type(self, token):
        upos = token['upos']
        xpos = token['xpos']
        if xpos == 'NNS':
            # https://universaldependencies.org/u/feat/Number.html
            number = conllutil.get_feat(token, 'Number', None)
            if number is not None:
                return f"{xpos}/Number={number}"
        elif xpos == 'CD':
            # https://universaldependencies.org/u/feat/NumForm.html
            # https://universaldependencies.org/u/feat/NumType.html
            num_form = conllutil.get_feat(token, 'NumForm', None)
            num_type = conllutil.get_feat(token, 'NumType', None)
            if num_form == 'Digit' and num_type is not None:
                return f"{xpos}/NumForm={num_form}/NumType={num_type}"
            elif num_form is not None:
                return f"{xpos}/NumForm={num_form}"
            elif num_form is None and num_type is None:
                # https://universaldependencies.org/en/pos/PRON.html#reciprocal-pronouns
                return f"{xpos}+{upos}"
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
