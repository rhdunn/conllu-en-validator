# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0
import re

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

RE_CARDINAL_DIGITS = re.compile("^\+?[0-9,\-'’#;:/]+$")

RE_ROMAN_DIGITS = re.compile(r"""^
                     [Mm]{0,3}  # 1000 - 3000
    ([Cc][MmDd]|[Dd]?[Cc]{0,3}) #  100 -  900
    ([Xx][CcLl]|[Ll]?[Xx]{0,3}) #   10 -   90
    ([Ii][XxVv]|[Vv]?[Ii]{0,3}) #    1 -    9
$""", re.VERBOSE)

num_formats = {
    'NumType=Card|NumForm=Digit': lambda form: RE_CARDINAL_DIGITS.fullmatch(form),
    'NumType=Card|NumForm=Roman': lambda form: RE_ROMAN_DIGITS.fullmatch(form),
}


class TokenFormValidator(Validator):
    def __init__(self, language):
        super().__init__(language)

    @staticmethod
    def validate_punct(form):
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
            return upos, None
        else:
            return upos, None

    def validate_token(self, sent, token):
        context, matcher = self.get_validator(sent, token)
        form = conllutil.normalized_form(token)
        if matcher is not None and not matcher(form):
            log(LogLevel.ERROR, sent, token, f"invalid {context} form '{form}'")
