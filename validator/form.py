# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0
import re
import unicodedata

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


punct_forms = [
    # ASCII
    '\u0021',  # EXCLAMATION MARK
    '\u0022',  # QUOTATION MARK
    '\u0027',  # APOSTROPHE; SINGLE QUOTATION MARK
    '\u0028',  # LEFT PARENTHESIS
    '\u0029',  # RIGHT PARENTHESIS
    '\u002C',  # COMMA
    '\u002D',  # HYPHEN-MINUS
    '\u002E',  # FULL STOP
    '\u002F',  # SOLIDUS
    '\u002E\u002E\u002E',  # ELLIPSIS
    '\u003A',  # COLON
    '\u003B',  # SEMICOLON
    '\u003F',  # QUESTION MARK
    # Unicode
    '\u2013',  # EN DASH
    '\u2014',  # EM DASH
    '\u2018',  # LEFT SINGLE QUOTATION MARK
    '\u2019',  # RIGHT SINGLE QUOTATION MARK
    '\u201C',  # LEFT DOUBLE QUOTATION MARK
    '\u201D',  # RIGHT DOUBLE QUOTATION MARK
    '\u2026',  # HORIZONTAL ELLIPSIS
]

cardinal_word_forms = [
    "zero", "nil",  # 0
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",  # 1 - 10
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",  # 11 - 19
    "dozen",  # 12 / 13
    "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",  # 2x - 9x
    "hundred",  # 100
    "k", "thousand",  # 1,000
    "m", "million", "mill", "mm",  # 1,000,000
    "b", "billion", "bn",  # 1,000,000,000
    "t", "trillion",  # 1,000,000,000,000
]

ordinal_word_forms = [
    "zeroth",  # 0
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",  # 1 - 10
    "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth",  # 11 - 19
    "twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth", "seventieth", "eightieth", "ninetieth",  # 2x - 9x
    "hundredth",  # 100
    "thousandth",  # 1,000
    "millionth",  # 1,000,000
    "billionth",  # 1,000,000,000
    "trillionth",  # 1,000,000,000,000
]

fractional_word_forms = [
    "half",  # 1/2
]
fractional_word_forms.extend(fractional_word_forms)  # 1/N

multiplicative_word_forms = [
    "once",
    "twice",
]

symbol_general_categories = [
    'Po',  # punctuation (other)
    'Sc',  # symbol (currency)
    'Sk',  # symbol (non-letterlike modifier)
    'Sm',  # symbol (math)
    'So',  # symbol (other)
]

word_general_categories = [
    'Ll',  # letter (lowercase)
    'Lt',  # letter (titlecase)
    'Lu',  # letter (uppercase)
    'Lm',  # letter (modifier)
]

word_form_additional_characters = [
    '\u0027',  # APOSTROPHE; SINGLE QUOTATION MARK
    '\u002D',  # HYPHEN-MINUS
    '\u002E',  # FULL STOP
    '\u2019',  # RIGHT SINGLE QUOTATION MARK
]

symbol_additional_forms = [
    # Sideways Emoticons: https://en.wikipedia.org/wiki/List_of_emoticons
    ':)', ':-)', '=)', '(:',  # smiling
    ':D', ':-D', '=D', 'D:',  # laughing; grinning
    ':(', ':-(', '=(',  # frowning; sad
    ':/', ':-/', '=/',  # skeptical
    ':O', ':-O', '=O',  # surprised
    ':P', ':-P', '=p', ';P',  # tongue sticking out
    ';)', ';-)', ';D',  # winking
    '>:(',  # angry
    # Upright Emoticons: https://en.wikipedia.org/wiki/List_of_emoticons
    '^_^',  # joyful
    'o_o',  # surprised
    '-_-',  # sleepy
    'x_x', 'x.x',  # dead
]

RE_CARDINAL = re.compile("^[0-9][0-9A-Za-z]+$")

RE_CARDINAL_DIGITS = re.compile("^\+?[0-9,\-'’#;:/]+$")

RE_ORDINAL_COMBINED = re.compile(r"""^
            [0456789]th|1st|2nd|3rd| #  0 -  9
               1[0-9]th|             # 10 - 19
    [0-9,]+([0456789]th|1st|2nd|3rd) # 20+
$""", re.VERBOSE)

RE_FRACTIONAL_DIGITS = re.compile(r"""^
    [0-9]+\.[0-9]+|       # 1.25 ; etc.
    \.[0-9]+|             #  .50 ; etc.
    [\u00BC-\u00BE]|      # unicode fractions: 1/4, 1/2, 3/4
    [\u2150-\u215F\u2189] # unicode number forms
$""", re.VERBOSE)

RE_ROMAN_DIGITS = re.compile(r"""^
                     [Mm]{0,3}  # 1000 - 3000
    ([Cc][MmDd]|[Dd]?[Cc]{0,3}) #  100 -  900
    ([Xx][CcLl]|[Ll]?[Xx]{0,3}) #   10 -   90
    ([Ii][XxVv]|[Vv]?[Ii]{0,3}) #    1 -    9
$""", re.VERBOSE)


def cardinal_number(sent, token, form):
    # NumForm=Digit
    if RE_CARDINAL_DIGITS.fullmatch(form):
        log(LogLevel.ERROR, sent, token, f"NumType=Card should be paired with NumForm=Digit for form '{form}'")
        return True
    # NumForm=Roman
    if RE_ROMAN_DIGITS.fullmatch(form):
        log(LogLevel.ERROR, sent, token, f"NumType=Card should be paired with NumForm=Roman for form '{form}'")
        return True
    # NumForm=Word
    if form.lower() in cardinal_word_forms:
        log(LogLevel.ERROR, sent, token, f"NumType=Card should be paired with NumForm=Word for form '{form}'")
        return True
    # other
    return RE_CARDINAL.fullmatch(form)


def ordinal_number(sent, token, form):
    # NumForm=Combi
    if RE_ORDINAL_COMBINED.fullmatch(form):
        log(LogLevel.ERROR, sent, token, f"NumType=Ord should be paired with NumForm=Combi for form '{form}'")
        return True
    # NumForm=Word
    if form.lower() in ordinal_word_forms:
        log(LogLevel.ERROR, sent, token, f"NumType=Ord should be paired with NumForm=Word for form '{form}'")
        return True
    # other
    return False


def multiplicative_number(sent, token, form):
    # NumForm=Word
    if form.lower() in multiplicative_word_forms:
        log(LogLevel.ERROR, sent, token, f"NumType=Mult should be paired with NumForm=Word for form '{form}'")
        return True
    # other
    return False


def symbol_form(sent, token, form):
    for c in form:
        cat = unicodedata.category(c)
        if cat not in symbol_general_categories:
            return form in symbol_additional_forms
    return len(form) == 1 or form in symbol_additional_forms


def word_form(sent, token, form):
    for c in form:
        cat = unicodedata.category(c)
        if cat not in word_general_categories and c not in word_form_additional_characters:
            return False
    return True


num_formats = {
    'NumType=Card': cardinal_number,
    'NumType=Card|NumForm=Digit': lambda sent, token, form: RE_CARDINAL_DIGITS.fullmatch(form),
    'NumType=Card|NumForm=Roman': lambda sent, token, form: RE_ROMAN_DIGITS.fullmatch(form),
    'NumType=Card|NumForm=Word': lambda sent, token, form: form.lower() in cardinal_word_forms,
    'NumType=Frac|NumForm=Digit': lambda sent, token, form: RE_FRACTIONAL_DIGITS.fullmatch(form),
    'NumType=Frac|NumForm=Word': lambda sent, token, form: form.lower() in fractional_word_forms,
    'NumType=Mult': multiplicative_number,
    'NumType=Mult|NumForm=Word': lambda sent, token, form: form.lower() in multiplicative_word_forms,
    'NumType=Ord': ordinal_number,
    'NumType=Ord|NumForm=Combi': lambda sent, token, form: RE_ORDINAL_COMBINED.fullmatch(form),
    'NumType=Ord|NumForm=Word': lambda sent, token, form: form.lower() in ordinal_word_forms,
}


class TokenFormValidator(Validator):
    def __init__(self, language):
        super().__init__(language)

    @staticmethod
    def validate_punct(sent, token, form):
        return form in punct_forms

    @staticmethod
    def get_validator(sent, token):
        upos = token['upos']
        if upos == 'PUNCT':
            return upos, TokenFormValidator.validate_punct
        elif upos in ['ADJ', 'ADV', 'DET', 'NUM']:
            num_format = []

            num_type = conllutil.get_feat(token, 'NumType', None)
            if num_type is not None:
                num_format.append(f"NumType={num_type}")

            num_form = conllutil.get_feat(token, 'NumForm', None)
            if num_form is not None:
                num_format.append(f"NumForm={num_form}")

            num_format = '|'.join(num_format)
            if num_format in num_formats:
                return f"{upos} with {num_format}", num_formats[num_format]
            if upos != 'NUM':
                return upos, word_form
            return upos, None
        elif upos == 'SYM':
            return upos, symbol_form
        else:
            return upos, word_form

    def validate_token(self, sent, token):
        context, matcher = self.get_validator(sent, token)
        form = conllutil.normalized_form(token)
        if form is None:
            log(LogLevel.ERROR, sent, token, f"missing form text")
        elif matcher is not None and not matcher(sent, token, form):
            log(LogLevel.ERROR, sent, token, f"invalid {context} form '{form}'")
