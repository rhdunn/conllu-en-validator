# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

import re

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


def unmodified_form_lemma(form):
    return form, form


def normalized_form_lemma(form):
    for _from, _to in normalization_rules:
        form = form.replace(_from, _to)
    return form, form


def lowercase_form_lemma(form):
    return normalized_form_lemma(form.lower())


def uppercase_form_lemma(form):
    return normalized_form_lemma(form.upper())


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
    'normalized-form': normalized_form_lemma,
    'unmodified-form': unmodified_form_lemma,
    # casing
    'capitalized-form': capitalized_form_lemma,
    'lowercase-form': lowercase_form_lemma,
    'uppercase-form': uppercase_form_lemma,
    # degree
    'comparative': lambda form: stemmed(form, lowercase_form_lemma, comparative_stemming_rules),  # -er
    'superlative': lambda form: stemmed(form, lowercase_form_lemma, superlative_stemming_rules),  # -est
    # numbers
    'cardinal-number': cardinal_number_lemma,
    'fractional-number': fractional_number_lemma,
    # nouns
    'plural-common-noun': lambda form: stemmed(form, lowercase_form_lemma, plural_noun_stemming_rules),  # -s
    'plural-proper-noun': lambda form: stemmed(form, capitalized_form_lemma, plural_noun_stemming_rules),  # -s
    'plural-proper-abbr': lambda form: stemmed(form, normalized_form_lemma, plural_noun_stemming_rules),  # -s
    # verbs
    'past-participle-verb': lambda form: stemmed(form, lowercase_form_lemma, past_participle_verb_stemming_rules),  # -en/-ed
    'past-tense-verb': lambda form: stemmed(form, lowercase_form_lemma, past_tense_verb_stemming_rules),  # -ed
    'present-verb': lambda form: stemmed(form, lowercase_form_lemma, present_verb_stemming_rules),  # -ing
    'present-3p-verb': lambda form: stemmed(form, lowercase_form_lemma, present_3p_verb_stemming_rules),  # -s/-es
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

past_participle_verb_stemming_rules = [
    # -VVCe[dn]
    (re.compile(r'((ee|oo)z)ed$'), r'\1e'),  # VVzed -> VVze
    (re.compile(r'(([aeiou])\2[^aeiou]?)ed$'), r'\1'),  # VVC?ed -> VVC? ~ doubled vowel
    (re.compile(r'((crea|[^v]ie)[^aeioufk])ed$'), r'\1e'),  # VVCed -> VVCe
    ('leaved', 'leave'),
    (re.compile(r'((ai|ea|io|o[aiu])[^aeious])e[dn]$'), r'\1'),  # VVCed -> VVC
    # -VCCe[dn]
    (re.compile(r'([aeiou]([bdgmnprt]))\2e[dn]$'), r'\1'),  # VCCed -> VC ~ doubled consonants
    (re.compile(r'([ou]l[gsv])ed$'), r'\1e'),  # VlCed -> VlCe
    (re.compile(r'((cha|ra|e|fri|u)[dn])ged$'), r'\1ge'),  # V[dn]ged -> V[dn]ge
    (re.compile(r'([aeiu]n[cs])ed$'), r'\1e'),  # VnCed -> VnCe
    (re.compile(r'([aeou]r[cgsv])e[dn]$'), r'\1e'),  # VrCe[dn] -> VrCe
    (re.compile(r'([ptw]ast)ed$'), r'\1e'),  # asted -> aste
    # -VCe[dn]
    (re.compile(r'(i[^aeiou]it)e[dn]$'), r'\1'),  # VCite[dn] -> VCit
    (re.compile(r'([aiou][^aeiouwy])e[dn]$'), r'\1e'),  # VCe[dn] -> VCe
    # -e[dn]
    (re.compile(r'([^aeiourlw]l)ed$'), r'\1e'),  # Cled -> Cle
    (re.compile(r'([ue])ed$'), r'\1e'),  # Ved -> Ve
    (re.compile(r'^([^aeiou])ied$'), r'\1ie'),  # Cied -> Cie
    ('ied', 'y'),
    ('ed', ''),
    ('en', ''),
    # -n
    (re.compile(r'([ao]w)n$'), r'\1'),  # Vwn -> Vw
]

past_tense_verb_stemming_rules = [
    # -VVCed
    (re.compile(r'((ee|oo)z)ed$'), r'\1e'),  # VVzed -> VVze
    (re.compile(r'(([aeiou])\2[^aeiou]?)ed$'), r'\1'),  # VVC?ed -> VVC? ~ doubled vowel
    (re.compile(r'((crea|[^v]ie)[^aeioufk])ed$'), r'\1e'),  # VVCed -> VVCe
    ('leaved', 'leave'),
    (re.compile(r'((ai|ea|io|o[aiu])[^aeious])ed$'), r'\1'),  # VVCed -> VVC
    # -VCCed
    (re.compile(r'([aeiou]([bdgmnprt]))\2ed$'), r'\1'),  # VCCed -> VC ~ doubled consonants
    (re.compile(r'([ou]l[gsv])ed$'), r'\1e'),  # VlCed -> VlCe
    (re.compile(r'((cha|ra|e|fri|u)[dn])ged$'), r'\1ge'),  # V[dn]ged -> V[dn]ge
    (re.compile(r'([aeiu]n[cs])ed$'), r'\1e'),  # VnCed -> VnCe
    (re.compile(r'([aeou]r[cgsv])ed$'), r'\1e'),  # VrCed -> VrCe
    (re.compile(r'([ptw]ast)ed$'), r'\1e'),  # asted -> aste
    # -VCed
    (re.compile(r'(i[^aeiou]it)ed$'), r'\1'),  # VCited -> VCit
    (re.compile(r'([aiou][^aeiouwy])ed$'), r'\1e'),  # VCed -> VCe
    # -ed
    (re.compile(r'([^aeiourlw]l)ed$'), r'\1e'),  # Cled -> Cle
    (re.compile(r'([ue])ed$'), r'\1e'),  # Ved -> Ve
    (re.compile(r'^([^aeiou])ied$'), r'\1ie'),  # Cied -> Cie
    ('ied', 'y'),
    ('ed', ''),
]

present_verb_stemming_rules = [
    # -VVCing
    (re.compile(r'((ee|oo)z)ing$'), r'\1e'),  # VVzing -> VVze
    (re.compile(r'(([aeiou])\2[^aeiou]?)ing$'), r'\1'),  # VVC?ing -> VVC? ~ doubled vowel
    (re.compile(r'((crea|[^v]ie)[^aeioufk])ing$'), r'\1e'),  # VVCing -> VVCe
    ('leaving', 'leave'),
    (re.compile(r'((ai|ea|io|o[aiu])[^aeious])ing$'), r'\1'),  # VVCing -> VVC
    # -VCCing
    (re.compile(r'([aeiou]([bdgmnprt]))\2ing$'), r'\1'),  # VCCing -> VC ~ doubled consonants
    (re.compile(r'([ou]l[gsv])ing$'), r'\1e'),  # VlCing -> VlCe
    (re.compile(r'((cha|ra|e|fri|u)[dn])ging$'), r'\1ge'),  # V[dn]ging -> V[dn]ge
    (re.compile(r'([aeiu]n[cs])ing$'), r'\1e'),  # VnCing -> VnCe
    (re.compile(r'([aeou]r[cgsv])ing$'), r'\1e'),  # VrCing -> VrCe
    (re.compile(r'([ptw]ast)ing$'), r'\1e'),  # asting -> aste
    # -VCing
    (re.compile(r'(i[^aeiou]it)ing$'), r'\1'),  # VCited -> VCit
    (re.compile(r'([aiou][^aeiouwy])ing$'), r'\1e'),  # VCing -> VCe
    # -ing
    (re.compile(r'([^aeiourlw]l)ing$'), r'\1e'),  # Cling -> Cle
    (re.compile(r'([ue])ing$'), r'\1e'),  # Ving -> Ve
    (re.compile(r'^([^aeiou])ying$'), r'\1ie'),  # Cying -> Cie
    ('ing', ''),
]

present_3p_verb_stemming_rules = [
    # -VVCes
    (re.compile(r'((ee|oo)z)es$'), r'\1e'),  # VVzes -> VVze
    (re.compile(r'((crea|[^v]ie)[^aeioufk])es$'), r'\1e'),  # VVCes -> VVCe
    ('leaves', 'leave'),
    # -VCCes
    (re.compile(r'([ou]l[gsv])es$'), r'\1e'),  # VlCes -> VlCe
    (re.compile(r'((cha|ra|e|fri|u)[dn])ges$'), r'\1ge'),  # V[dn]ges -> V[dn]ge
    (re.compile(r'([aeiu]n[cs])es$'), r'\1e'),  # VnCes -> VnCe
    (re.compile(r'([aeou]r[cgsv])es$'), r'\1e'),  # VrCes -> VrCe
    (re.compile(r'([ptw]ast)es$'), r'\1e'),  # astes -> aste
    # -VCes
    (re.compile(r'(i[^aeiou]it)es$'), r'\1'),  # VCites -> VCit
    (re.compile(r'([aiou][^aeiouwy]e)s$'), r'\1'),  # VCes -> VCe
    # -es
    (re.compile(r'([^aeiourlw]l)es$'), r'\1e'),  # Cles -> Cle
    (re.compile(r'([ue])es$'), r'\1e'),  # Ves -> Ve
    (re.compile(r'^([^aeiou])ies$'), r'\1ie'),  # Cies -> Cie
    ('ies', 'y'),
    # -es
    ('es', ''),
    ('s', ''),
]

lemmatization_rule_names = {
# https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    'CC': 'lowercase-form',  # coordinating conjunction
    'CD/NumForm=Combi': 'normalized-form',  # cardinal number, digits with a suffix
    'CD/NumForm=Digit/NumType=Card': 'cardinal-number',  # cardinal number, integer
    'CD/NumForm=Digit/NumType=Frac': 'fractional-number',  # cardinal number, fraction
    'CD/NumForm=Roman': 'normalized-form',  # cardinal number, roman numerals
    'CD/NumForm=Word': 'lowercase-form',  # cardinal number, words
    'CD/NumForm=Word/Abbr=Yes': 'lowercase-form',  # cardinal number, word abbreviations
    'CD+PRON': 'lowercase-form',  # cardinal number, reciprocal pronoun -- "one/PRON+CD another"
    'DT': 'lowercase-form',  # determiner
    'EX': 'lowercase-form',  # existential "there"
    'FW/Abbr=Yes': 'lowercase-form',  # foreign word abbreviation
    'IN': 'lowercase-form',  # preposition, subordinating conjunction
    'IN/Abbr=Yes': 'lowercase-form',  # abbreviation of a preposition or subordinating conjunction
    'JJ': 'lowercase-form',  # adjective, positive (first degree)
    'JJR': 'comparative',  # adjective, comparative (second degree) [-er]
    'JJS': 'superlative',  # adjective, superlative (third degree) [-est]
    'LS': 'normalized-form',  # list item marker
    'MD': 'lowercase-form',  # verb, modal
    'NN': 'lowercase-form',  # noun
    'NN/Abbr=Yes': 'uppercase-form',  # noun abbreviations
    'NNP': 'capitalized-form',  # proper noun
    'NNP/Abbr=Yes': 'uppercase-form',  # proper noun abbreviations
    'NNPS/Number=Coll': 'capitalized-form',  # proper noun, collective / singulare tantum (singular form as plural)
    'NNPS/Number=Plur': 'plural-proper-noun',  # proper noun, plural
    'NNPS/Number=Plur/Abbr=Yes': 'plural-proper-abbr',  # proper noun abbreviations, plural
    'NNPS/Number=Ptan': 'capitalized-form',  # proper noun, plurale tantum (plural form lemma)
    'NNS/Number=Coll': 'lowercase-form',  # noun, collective / singulare tantum (singular form as plural)
    'NNS/Number=Plur': 'plural-common-noun',  # noun, plural
    'NNS/Number=Plur/Abbr=Yes': 'plural-common-noun',  # noun, plural abbreviation
    'NNS/Number=Ptan': 'lowercase-form',  # noun, plurale tantum (plural form lemma)
    'PDT': 'lowercase-form',  # predeterminer
    'POS': 'lowercase-form',  # possessive
    'PRP': 'lowercase-form',  # pronoun, personal
    'PRP$': 'lowercase-form',  # pronoun, possessive
    'RB': 'lowercase-form',  # adverb
    'RB/Abbr=Yes': 'uppercase-form',  # adverb abbreviations
    'RBR': 'comparative',  # adverb, comparative (second degree) [-er]
    'RBS': 'superlative',  # adverb, superlative (third degree) [-est]
    'RP': 'lowercase-form',  # particle
    'SYM': 'normalized-form',  # symbol
    'TO': 'lowercase-form',  # "to"
    'TO/Abbr=Yes': 'lowercase-form',  # "to" abbreviations
    'UH': 'lowercase-form',  # interjection
    'VB': 'lowercase-form',  # verb, base form
    'VBD': 'past-tense-verb',  # verb, past tense [-ed]
    'VBG': 'present-verb',  # verb, gerund or present tense [-ing]
    'VBN': 'past-participle-verb',  # verb, past participle [-en/-ed]
    'VBP': 'lowercase-form',  # verb, singular present
    'VBZ': 'present-3p-verb',  # verb, singular present, third person [-s/-es]
    'WDT': 'lowercase-form',  # determiner, wh-
    'WP': 'lowercase-form',  # pronoun, wh-
    'WP$': 'lowercase-form',  # pronoun, possessive wh-
    'WRB': 'lowercase-form',  # adverb, wh-
# https://universaldependencies.org/tagset-conversion/en-penn-uposf.html
# https://www.ldc.upenn.edu/sites/www.ldc.upenn.edu/files/etb-supplementary-guidelines-2009-addendum.pdf
    '\'\'': 'unmodified-form',  # right (end) quote
    '$': 'unmodified-form',  # currency symbol
    ',': 'unmodified-form',  # mid-sentence punctuation -- comma, semicolon, or ellipsis
    '.': 'unmodified-form',  # sentence-final punctuation -- full stop, exclamation mark, or question mark
    ':': 'unmodified-form',  # colon or dash
    '``': 'unmodified-form',  # left (start) quote
    '-LRB-': 'unmodified-form',  # left parenthesis or bracket
    '-RRB-': 'unmodified-form',  # right parenthesis or bracket
    'ADD': 'lowercase-form',  # web address
    'AFX': 'lowercase-form',  # non-hyphenated affix
    'HYPH': 'unmodified-form',  # hyphen
    'NFP': 'lowercase-form',  # non-functional punctuation
}

lemma_exceptions = {
    ':': {  # colon or dash
        '\u2013': '-',  # EN DASH
        '\u2014': '-',  # EM DASH
        '...': '\u2026',  # HORIZONTAL ELLIPSIS
    },
    'CD/NumForm=Word/Abbr=Yes': {  # cardinal numbers, word
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
    'FW/Abbr=Yes': {  # foreign word abbreviations
        'etc': 'etc.',
        'mlle.': 'Mlle.',
    },
    'IN/Abbr=Yes': {  # preposition, subordinating conjunction
        'vs': 'versus',
    },
    'JJ': {  # adjectives
        # proper noun adjectives
        'afghan': 'Afghan',
        'african': 'African',
        'american': 'American',
        'arab': 'Arab',
        'argentinian': 'Argentinian',
        'asian': 'Asian',
        'british': 'British',
        'chilean': 'Chilean',
        'egyptian': 'Egyptian',
        'french': 'French',
        'german': 'German',
        'indian': 'Indian',
        'iranian': 'Iranian',
        'iraqi': 'Iraqi',
        'irish': 'Irish',
        'islamic': 'Islamic',
        'israeli': 'Israeli',
        'italian': 'Italian',
        'japanese': 'Japanese',
        'jordanian': 'Jordanian',
        'lebanese': 'Lebanese',
        'mediterranean': 'Mediterranean',
        'mexican': 'Mexican',
        'muslim': 'Muslim',
        'norwegian': 'Norwegian',
        'pakistani': 'Pakistani',
        'palestinian': 'Palestinian',
        'saudi': 'Saudi',
        'scottish': 'Scottish',
        'shiite': 'Shiite',
        'siamese': 'Siamese',
        'spanish': 'Spanish',
        'sunni': 'Sunni',
        'swedish': 'Swedish',
        'syrian': 'Syrian',
        'thai': 'Thai',
        'wahhabi': 'Wahhabi',
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
        '\'d': 'would', # See https://github.com/UniversalDependencies/UD_English-EWT/issues/450 for modal "would" not lemmatizing to "will".
        '\'ll': 'will',
        # multi-word tokens
        'ca': 'can',  # ca|n't
        'wo': 'will',  # wo|n't
    },
    'NN/Abbr=Yes': {  # noun abbreviations
        'ED.': ['edition', 'editor'],
        'NO.': 'number',
        'P.': 'page',
        'VOL.': 'volume',
        # units
        'cm': 'centimeter',
        'hr': 'hour',
        'mcg': 'microgram',
        'mg': 'milligram',
        'min': 'minutes',
        'yr': 'year',
        # multi-word
        'A.M.': 'a.m.',  # ante meridiem (before noon)
        'P.M.': 'p.m.',  # post meridiem (after noon)
    },
    'NNS/Number=Plur/Abbr=Yes': {  # noun abbreviations, plural
        # units
        'cm': 'centimeter',
        'hrs': 'hour',
        'min': 'minute',
        'mins': 'minute',
        'ppl': 'person',
        'yrs': 'year',
    },
    'NNP/Abbr=Yes': {  # proper noun abbreviations
        'AVE': 'Avenue',
        'CAL': 'California',
        'DR': ['Doctor', 'Drive'],  # before noun; after noun
        'INC': 'Incorporated',
        'JR': 'Junior',
        'MR': 'Mister',
        'MRS': 'Mistress',
        'MT': 'Mount',
        'OP': 'Opus',
        'PROF': 'Professor',
        'ST': ['Saint', 'Street'],  # before noun; after noun
        # days of the week
        'MON': 'Monday',
        'TUE': 'Tuesday',
        'TUES': 'Tuesday',
        'WED': 'Wednesday',
        'THU': 'Thursday',
        'THUR': 'Thursday',
        'FRI': 'Friday',
        'SAT': 'Saturday',
        'SUN': 'Sunday',
        # months of the year
        'JAN': 'January',
        'FEB': 'February',
        'MAR': 'March',
        'APR': 'April',
        'JUN': 'June',
        'JUL': 'July',
        'AUG': 'August',
        'SEP': 'September',
        'SEPT': 'September',
        'OCT': 'October',
        'NOV': 'November',
        'DEC': 'December',
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
        # singular and plural -- not plural only (plurale tantum), so shouldn't use Number=Ptan
        'series': 'series',
        'species': 'species',
        # uncountable -- not plural only (plurale tantum), so shouldn't use Number=Ptan
        'economics': 'economics',
        'news': 'news',
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
        'geniuses': 'genius',
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
    },
    'RB/Abbr=Yes': {  # adverb abbreviations
        'AKA': 'a.k.a.',  # also known as
    },
    'RBR': {  # adverb, comparative
        # irregular
        'better': 'well',
        'farther': 'far',
        'further': 'far',
        'less': 'little',
        'lesser': 'little',
        'worse': 'bad',
        # -er exceptions
        'closer': 'close',
    },
    'RBS': {  # adverb, superlative
        # irregular
        'best': 'well',
        'farthest': 'far',
        'furthest': 'far',
        'least': 'little',
        'worst': 'bad',
    },
    'SYM': {  # symbol
        '\u2013': '\u002D',  # EN DASH -> HYPHEN-MINUS
        '\u2014': '\u002D',  # EM DASH -> HYPHEN-MINUS
    },
    'TO/Abbr=Yes': { # PART+TO -- "to"
        'a': 'to',  # ought|a, etc.
        'na': 'to',  # wan|na, etc.
        'ta': 'to',  # got|ta, etc.
    },
    'UH': {  # interjection
        'christ': 'Christ',
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
        'ate': 'eat',
        'bade': 'bid',
        'bore': 'bear',
        'bent': 'bend',
        'became': 'become',
        'began': 'begin',
        'betook': 'betake',
        'bit': 'bite',
        'blew': 'blow',
        'bought': 'buy',
        'broke': 'break',
        'brought': 'bring',
        'built': 'build',
        'caught': 'catch',
        'came': 'come',
        'chose': 'choose',
        'clung': 'cling',
        'co-wrote': 'co-write',
        'cowrit': 'cowrite',
        'crept': 'creep',
        'cross-bred': 'cross-breed',
        'de-froze': 'de-freeze',
        'dealt': 'deal',
        'did': 'do',
        'died': 'die',
        'drank': 'drink',
        'drew': 'draw',
        'drove': 'drive',
        'dwelt': 'dwell',
        'fell': 'fall',
        'felt': 'feel',
        'fled': 'flee',
        'flew': 'fly',
        'flung': 'fling',
        'forbade': 'forbid',
        'foresaw': 'foresee',
        'forgave': 'forgive',
        'forgot': 'forget',
        'fought': 'fight',
        'found': 'find',
        'froze': 'freeze',
        'gave': 'give',
        'got': 'get',
        'grew': 'grow',
        'had': 'have',
        'happend': 'happen',
        'heard': 'hear',
        'held': 'hold',
        'hid': 'hide',
        'hung': 'hang',
        'kept': 'keep',
        'knelt': 'kneel',
        'knew': 'know',
        'laid': 'lay',
        'lay': 'lie',
        'led': 'lead',
        'leant': 'lean',
        'learnt': 'learn',
        'left': 'leave',
        'lit': 'light',
        'lost': 'lose',
        'made': 'make',
        'meant': 'mean',
        'met': 'meet',
        'mistook': 'mistake',
        'outshone': 'outshine',
        'overran': 'overrun',
        'overseen': 'oversee',  # past participle or non-standard past tense
        'overthrew': 'overthrow',
        'overtook': 'overtake',
        'paid': 'pay',
        'ran': 'run',
        'rang': 'ring',
        'rebuilt': 'rebuild',
        'retook': 'retake',
        'rid': ['rid', 'ride'],
        'rode': 'ride',
        'rose': 'rise',
        'said': 'say',
        'sang': 'sing',
        'sank': 'sink',
        'sat': 'sit',
        'saw': 'see',
        'seen': 'see',  # past participle or non-standard past tense
        'sent': 'send',
        'shone': 'shine',
        'shook': 'shake',
        'shot': 'shoot',
        'shrunk': 'shrink',
        'slept': 'sleep',
        'slid': 'slide',
        'slung': 'sling',
        'snuck': 'sneak',
        'sold': 'sell',
        'sought': 'seek',
        'sped': 'speed',
        'squoze': 'squeeze',
        'stole': 'steal',
        'stood': 'stand',
        'struck': 'strike',
        'spent': 'spend',
        'spoke': 'speak',
        'sprang': 'spring',
        'stuck': 'stick',
        'stunk': 'stink',
        'sunk': 'sink',
        'swam': 'swim',
        'swept': 'sweep',
        'swore': 'swear',
        'swung': 'swing',
        'taught': 'teach',
        'thought': 'think',
        'threw': 'throw',
        'told': 'tell',
        'took': 'take',
        'trod': ['trod', 'tread'],
        'understood': 'understand',
        'undertook': 'undertake',
        'underwent': 'undergo',
        'was': 'be',
        'went': 'go',
        'were': 'be',
        'withdrew': 'withdraw',
        'woke': 'wake',
        'won': 'win',
        'wore': 'wear',
        'wound': 'wind',
        'writ': 'write',
        'wrote': 'write',
        'wrought': 'wring',
        # -ed exceptions
        'added': 'add',
        'coalesced': 'coalesce',
        'eyed': 'eye',
    },
    'VBG': {  # verb, gerund or present tense
        # -ing exceptions
        'being': 'be',
        'eyeing': 'eye',
        'eying': 'eye',
        'having': 'have',
        'coalescing': 'coalesce',
    },
    'VBN': {  # verb, past participle
        # irregular
        'been': 'be',
        'begun': 'begin',
        'born': 'bear',
        'bound': 'bind',
        'done': 'do',
        'flown': 'fly',
        'foretold': 'foretell',
        'forgone':'forgo',
        'gone': 'go',
        'sprung': 'spring',
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
        'eyes': 'eye',
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
        lemma_type = xpos

        if xpos in ['NNS', 'NNPS']:
            # https://universaldependencies.org/u/feat/Number.html
            number = conllutil.get_feat(token, 'Number', None)
            if number is not None:
                lemma_type = f"{lemma_type}/Number={number}"
        elif xpos == 'CD':
            # https://universaldependencies.org/u/feat/NumForm.html
            # https://universaldependencies.org/u/feat/NumType.html
            num_form = conllutil.get_feat(token, 'NumForm', None)
            num_type = conllutil.get_feat(token, 'NumType', None)
            if num_form == 'Digit' and num_type is not None:
                lemma_type = f"{lemma_type}/NumForm={num_form}/NumType={num_type}"
            elif num_form is not None:
                lemma_type = f"{lemma_type}/NumForm={num_form}"
            elif num_form is None and num_type is None:
                # https://universaldependencies.org/en/pos/PRON.html#reciprocal-pronouns
                lemma_type = f"{lemma_type}+{upos}"

        # https://universaldependencies.org/u/feat/Abbr.html
        # https://universaldependencies.org/misc.html#correctform
        abbr = conllutil.get_feat(token, 'Abbr', None)
        correct_form = conllutil.get_misc(token, 'CorrectForm', None)
        if abbr is not None and (correct_form is None or correct_form == '_'):
            lemma_type = f"{lemma_type}/Abbr={abbr}"

        return lemma_type

    def match_lemma(self, lemma, expected_lemma):
        if isinstance(expected_lemma, list):
            return lemma in expected_lemma
        return lemma == expected_lemma

    def validate_lemma(self, sent, token, rule, form, lemma, lemma_type):
        normalized_form, expected_lemma = lemmatization_rules[rule](form)

        if lemma_type == 'VBN':
            if form.endswith('en') and expected_lemma in lemma_exceptions['VBD']:
                # VBN + -en => VBD => VB : e.g. hidden => hid => hide
                rule = 'lemma-exception'
                expected_lemma = lemma_exceptions['VBD'][expected_lemma]
            elif normalized_form in lemma_exceptions['VBD']:
                # use VBD for other lemma exceptions
                rule = 'lemma-exception'
                expected_lemma = lemma_exceptions['VBD'][normalized_form]

        if lemma_type in lemma_exceptions and normalized_form in lemma_exceptions[lemma_type]:
            # use the exception lemma instead of the rule-based lemma
            rule = 'lemma-exception'
            expected_lemma = lemma_exceptions[lemma_type][normalized_form]

        if 'Abbr=Yes' in lemma_type and form.endswith('.'):
            abbr_form = normalized_form[:-1]
            # check the abbreviation without the trailing '.'
            if lemma_type in lemma_exceptions and abbr_form in lemma_exceptions[lemma_type]:
                rule = 'lemma-exception'
                expected_lemma = lemma_exceptions[lemma_type][abbr_form]

        if self.match_lemma(lemma, expected_lemma):
            pass  # matched via lemmatization rule
        else:
            if isinstance(expected_lemma, list):
                expected_lemma = '|'.join(expected_lemma)
            log(LogLevel.ERROR, sent, token,
                f"{lemma_type} lemma '{lemma}' does not match {rule} applied to form '{form}', expected '{expected_lemma}'")

    def validate_token(self, sent, token):
        form = conllutil.correct_form(token)
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
        elif lemma_type not in ['FW', 'GW']:  # ignore foreign word (FW) and grouped word (GW) lemmas
            log(LogLevel.WARN, sent, token, f"{lemma_type} lemma '{lemma}' does not have a validation rule for form '{form}'")
