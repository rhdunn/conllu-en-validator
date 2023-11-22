# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

import re

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


def normalized_form_lemma(form):
    for _from, _to in normalization_rules:
        form = form.replace(_from, _to)
    return form, form


def lowercase_form_lemma(form):
    return normalized_form_lemma(form.lower())


def capitalized_form_lemma(form):
    return normalized_form_lemma(form.capitalize())


def cardinal_number_lemma(form):
    normalized, _ = normalized_form_lemma(form.lower())
    normalized = normalized.replace(',', '')
    return normalized, normalized


def fractional_number_lemma(form):
    normalized, _ = normalized_form_lemma(form.lower())
    normalized = normalized.replace(',', '.')  # German fraction forms
    return normalized, normalized


def stemmed(form, normalize_lemma, stemming_rules):
    normalized, _ = normalize_lemma(form)
    for ending, replacement in stemming_rules:
        if isinstance(ending, re.Pattern):
            replaced, count = ending.subn(replacement, normalized)
            if count != 0:
                return normalized, replaced
        elif normalized.endswith(ending):
            return normalized, normalized[:-len(ending)] + replacement
    return normalized, normalized


lemmatization_rules = {
    'capitalized-form': capitalized_form_lemma,
    'cardinal-number': cardinal_number_lemma,
    'comparative': lambda form: stemmed(form, lowercase_form_lemma, comparative_stemming_rules),  # -er
    'fractional-number': fractional_number_lemma,
    'lowercase-form': lowercase_form_lemma,
    'normalized-form': normalized_form_lemma,
    'past-verb': lambda form: stemmed(form, lowercase_form_lemma, past_verb_stemming_rules),  # -ed
    'plural-common-noun': lambda form: stemmed(form, lowercase_form_lemma, plural_noun_stemming_rules),  # -s
    'plural-proper-noun': lambda form: stemmed(form, capitalized_form_lemma, plural_noun_stemming_rules),  # -s
    'present-verb': lambda form: stemmed(form, lowercase_form_lemma, present_verb_stemming_rules),  # -ing
    'present-3p-verb': lambda form: stemmed(form, lowercase_form_lemma, present_3p_verb_stemming_rules),  # -s/-es
    'superlative': lambda form: stemmed(form, lowercase_form_lemma, superlative_stemming_rules),  # -est
}

comparative_stemming_rules = [
    (re.compile(r'([eo]a[^aeiou])er$'), r'\1'),  # oaCer -> oaC ; eaCer -> eaC
    (re.compile(r'([ai][^aeiou]e)r$'), r'\1'),  # aCer -> aCe ; iCer -> iCe
    (re.compile(r'([dgnt])\1er$'), r'\1'),  # CCer -> C
    ('ier', 'y'),
    ('er', ''),
]

superlative_stemming_rules = [
    (re.compile(r'([eo]a[^aeiou])est$'), r'\1'),  # oaCest -> oaC ; eaCest -> eaC
    (re.compile(r'([ai][^aeiou]e)st$'), r'\1'),  # aCest -> aCe ; iCest -> iCe
    (re.compile(r'([dgnt])\1est$'), r'\1'),  # CCest -> C
    ('iest', 'y'),
    ('est', ''),
]

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

past_verb_stemming_rules = [
    # -VVCed ; -VVCen
    (re.compile(r'((ee|oo)z)ed$'), r'\1e'),  # VVzed -> VVze
    (re.compile(r'(([aeiou])\2[^aeiou]?)ed$'), r'\1'),  # VVC?ed -> VVC? ~ doubled vowel
    (re.compile(r'((ai|ea|io|o[ai])[^aeious])ed$'), r'\1'),  # VVCed -> VVC
    (re.compile(r'([^v]ie[^aeioufk])ed$'), r'\1e'),  # VVCed -> VVCe
    # -VCCed ; -VCCen
    (re.compile(r'([aeiou]([bdgmnprt]))\2ed$'), r'\1'),  # VCCed -> VC ~ doubled consonants
    (re.compile(r'([ou]l[gsv])ed$'), r'\1e'),  # VlCed -> VlCe
    (re.compile(r'((ch|r)a|e|fri|u)nged$'), r'\1nge'),  # Vnged -> Vnge
    (re.compile(r'([aeiu]n[cs])ed$'), r'\1e'),  # VnCed -> VnCe
    (re.compile(r'([aeou]r[cgsv])e[dn]$'), r'\1e'),  # VrCed -> VrCe ; VrCen -> VrCe
    (re.compile(r'([ptw]ast)ed$'), r'\1e'),  # asted -> aste
    # -VCed ; -VCen
    (re.compile(r'([aiou][^aeiou]e)[dn]$'), r'\1'),  # VCed -> VCe ; VCen -> VCe
    # -ed
    (re.compile(r'([^aeiourlw]l)ed$'), r'\1e'),  # Cled -> Cle
    (re.compile(r'([ue])ed$'), r'\1e'),  # Ved -> Ve
    ('ied', 'y'),
    ('ed', ''),
    # -en
    ('ozen', 'eeze'),
    ('en', ''),
]

present_verb_stemming_rules = [
    # -VVCing
    (re.compile(r'((ee|oo)z)ing$'), r'\1e'),  # VVzing -> VVze
    (re.compile(r'(([aeiou])\2[^aeiou]?)ing$'), r'\1'),  # VVC?ing -> VVC? ~ doubled vowel
    (re.compile(r'((ai|ea|io|o[ai])[^aeious])ing$'), r'\1'),  # VVCing -> VVC
    (re.compile(r'([^v]ie[^aeioufk])ing$'), r'\1e'),  # VVCing -> VVCe
    # -VCCing
    (re.compile(r'([aeiou]([bdgmnprt]))\2ing$'), r'\1'),  # VCCing -> VC ~ doubled consonants
    (re.compile(r'([ou]l[gsv])ing$'), r'\1e'),  # VlCing -> VlCe
    (re.compile(r'((ch|r)a|e|fri|u)nging$'), r'\1nge'),  # Vnging -> Vnge
    (re.compile(r'([aeiu]n[cs])ing$'), r'\1e'),  # VnCing -> VnCe
    (re.compile(r'([aeou]r[cgsv])ing$'), r'\1e'),  # VrCing -> VrCe
    (re.compile(r'([ptw]ast)ing$'), r'\1e'),  # asting -> aste
    # -VCing
    (re.compile(r'([aiou][^aeiou])ing$'), r'\1e'),  # VCing -> VCe
    # -ing
    (re.compile(r'([^aeiourlw]l)ing$'), r'\1e'),  # Cling -> Cle
    (re.compile(r'([ue])ing$'), r'\1e'),  # Ving -> Ve
    ('ing', ''),
]

present_3p_verb_stemming_rules = [
    # -VVCes
    (re.compile(r'((ee|oo)z)es$'), r'\1e'),  # VVzes -> VVze
    (re.compile(r'([^v]ie[^aeioufk])es$'), r'\1e'),  # VVCes -> VVCe
    # -VCCes
    (re.compile(r'([ou]l[gsv])es$'), r'\1e'),  # VlCes -> VlCe
    (re.compile(r'((ch|r)a|e|fri|u)nges$'), r'\1e'),  # Vnges -> Vnge
    (re.compile(r'([aeiu]n[cs])es$'), r'\1e'),  # VnCes -> VnCe
    (re.compile(r'([aeou]r[cgsv])es$'), r'\1e'),  # VrCes -> VrCe
    (re.compile(r'([ptw]ast)es$'), r'\1e'),  # astes -> aste
    # -VCes
    (re.compile(r'([aiou][^aeiou]e)s$'), r'\1'),  # VCes -> VCe
    # -es
    (re.compile(r'([^aeiourlw]l)es$'), r'\1e'),  # Cles -> Cle
    (re.compile(r'([ue])es$'), r'\1e'),  # Ves -> Ve
    ('ies', 'y'),
    # -es
    ('es', ''),
    ('s', ''),
]

lemmatization_rule_names = {
    'CC': 'lowercase-form',  # coordinating conjunction
    'CD/NumForm=Combi': 'normalized-form',  # cardinal number, digits with a suffix
    'CD/NumForm=Digit/NumType=Card': 'cardinal-number',  # cardinal number, integer
    'CD/NumForm=Digit/NumType=Frac': 'fractional-number',  # cardinal number, fraction
    'CD/NumForm=Roman': 'normalized-form',  # cardinal number, roman numerals
    'CD/NumForm=Word': 'lowercase-form',  # cardinal number, words
    'CD+PRON': 'lowercase-form',  # cardinal number, reciprocal pronoun -- "one/PRON+CD another"
    'DT': 'lowercase-form',  # determiner
    'EX': 'lowercase-form',  # existential "there"
    'IN': 'lowercase-form',  # preposition, subordinating conjunction
    'JJ': 'lowercase-form',  # adjective, positive (first degree)
    'JJR': 'comparative',  # adjective, comparative (second degree) [-er]
    'JJS': 'superlative',  # adjective, superlative (third degree) [-est]
    'LS': 'normalized-form',  # list item marker
    'MD': 'lowercase-form',  # verb, modal
    'NN': 'lowercase-form',  # noun
    'NNP': 'capitalized-form',  # proper noun
    'NNPS/Number=Coll': 'capitalized-form',  # proper noun, collective / singulare tantum (singular form as plural)
    'NNPS/Number=Plur': 'plural-proper-noun',  # proper noun, plural
    'NNPS/Number=Ptan': 'capitalized-form',  # proper noun, plurale tantum (plural form lemma)
    'NNS/Number=Coll': 'lowercase-form',  # noun, collective / singulare tantum (singular form as plural)
    'NNS/Number=Plur': 'plural-common-noun',  # noun, plural
    'NNS/Number=Ptan': 'lowercase-form',  # noun, plurale tantum (plural form lemma)
    'PDT': 'lowercase-form',  # predeterminer
    'POS': 'lowercase-form',  # possessive
    'PRP': 'lowercase-form',  # pronoun, personal
    'PRP$': 'lowercase-form',  # pronoun, possessive
    'RB': 'lowercase-form',  # adverb
    'RBR': 'comparative',  # adverb, comparative (second degree) [-er]
    'RBS': 'superlative',  # adverb, superlative (third degree) [-est]
    'RP': 'lowercase-form',  # particle
    'SYM': 'normalized-form',  # symbol
    'TO': 'lowercase-form',  # "to"
    'UH': 'lowercase-form',  # interjection
    'VB': 'lowercase-form',  # verb, base form
    'VBD': 'past-verb',  # verb, past tense [-ed]
    'VBG': 'present-verb',  # verb, gerund or present tense [-ing]
    'VBN': 'past-verb',  # verb, past participle [-ed]
    'VBP': 'lowercase-form',  # verb, singular present
    'VBZ': 'present-3p-verb',  # verb, singular present, third person [-s/-es]
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
    'JJR': {  # adjectives, comparative
        # irregular
        'better': 'good',
        'elder': 'old',  # eld/eald in Old English ~ older [old], elder [ancient] split in Modern English
        'farther': 'far',
        'further': 'far',
        'worse': 'bad',
        # -er exceptions
        'closer': 'close',
        'denser': 'dense',
        'larger': 'large',
        'ruder': 'rude',
        'simpler': 'simple',
        'stranger': 'strange',
    },
    'JJS': {  # adjectives, superlative
        # irregular
        'best': 'good',
        'eldest': 'old',  # eld/eald in Old English ~ oldest [old], eldest [ancient] split in Modern English
        'farthest': 'far',
        'furthest': 'far',
        'worst': 'bad',
        # -est exceptions
        'ablest': 'able',
        'closest': 'close',
        'largest': 'large',
        'rudest': 'rude',
        'simplest': 'simple',
        'surest': 'sure',
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
    'RBR': {  # adverb, comparative
        # irregular
        'better': 'well',
        'farther': 'far',
        'further': 'far',
        'less': 'little',
        'lesser': 'little',
        'worse': 'badly',
        # -er exceptions
        'closer': 'close',
    },
    'RBS': {  # adverb, superlative
        # irregular
        'best': 'well',
        'farthest': 'far',
        'furthest': 'far',
        'least': 'little',
        'worst': 'badly',
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
    'VBD': {  # verb, past tense
        # clitics
        '\'d': ['do', 'have'],  # did, had
        # irregular
        'arose': 'arise',
        'bore': 'bear',
        'bent': 'bend',
        'became': 'become',
        'began': 'begin',
        'betook': 'betake',
        'blew': 'blow',
        'broke': 'break',
        'brought': 'bring',
        'built': 'build',
        'caught': 'catch',
        'came': 'come',
        'chose': 'choose',
        'co-wrote': 'co-write',
        'did': 'do',
        'drew': 'draw',
        'drove': 'drive',
        'felt': 'feel',
        'flung': 'fling',
        'fought': 'fight',
        'found': 'find',
        'gave': 'give',
        'got': 'get',
        'grew': 'grow',
        'had': 'have',
        'happend': 'happen',
        'heard': 'hear',
        'held': 'hold',
        'kept': 'keep',
        'knew': 'know',
        'made': 'make',
        'rose': 'rise',
        'said': 'say',
        'sat': 'sit',
        'sent': 'send',
        'stood': 'stand',
        'spoke': 'speak',
        'taught': 'teach',
        'thought': 'think',
        'told': 'tell',
        'took': 'take',
        'underwent': 'undergo',
        'was': 'be',
        'went': 'go',
        'were': 'be',
        'wore': 'wear',
        'wrote': 'write',
        'wrought': 'wring',
        # -ed exceptions
        'coalesced': 'coalesce',
    },
    'VBG': {  # verb, gerund or present tense
        # -ing exceptions
        'having': 'have',
        'coalescing': 'coalesce',
    },
    'VBN': {  # verb, past participle
        # irregular
        'been': 'be',
        'caught': 'catch',
        'done': 'do',
        'fought': 'fight',
        'had': 'have',
        'taught': 'teach',
        # -ed exceptions
        'coalesced': 'coalesce',
    },
    'VBP': {  # verb, singular present
        # clitics
        '\'m': 'be',  # am
        '\'re': 'be',  # are
        '\'s': 'be',  # is
        '\'ve': 'have',
        # irregular
        'am': 'be',
        'are': 'be',
        'art': 'be',
        'is': 'be',
        'were': 'be',
        # multi-word tokens
        'ai': 'be',  # ai|n't
        'du': 'do',  # du|n|no
    },
    'VBZ': {  # verb, singular present, third person
        # clitics
        '\'s': ['be', 'have'],  # is, has
        # irregular
        'is': 'be',
        'does': 'do',
        'has': 'have',
        'hath': 'have',
        # multi-word tokens
        'ai': 'be',  # is
        # -es exceptions
        'coalesces': 'coalesce',
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
        if xpos in ['NNS', 'NNPS']:
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
            if isinstance(expected_lemma, list):
                expected_lemma = '|'.join(expected_lemma)
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
