# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

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


class TokenFormValidator(Validator):
    def __init__(self, language):
        super().__init__(language)

    def validate_token(self, sent, token):
        upos = token['upos']
        form = conllutil.normalized_form(token)
        if upos == 'PUNCT':
            if form not in punct_forms:
                log(LogLevel.ERROR, sent, None,
                    f"unknown punctuation form '{form}'")
