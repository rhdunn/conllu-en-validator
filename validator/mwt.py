# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


def is_mwt_start(form):
    return form[-1].isalpha()


def is_mwt_end(form, prev_form):
    if form[0] in ['\'', '’']:
        for c in form:
            if c.isalpha():
                return LogLevel.ERROR
        if len(form) == 1 and prev_form[-1] in ['s', 'S']:
            return LogLevel.WARN  # possessive or end quote
    if form[0].isalpha():
        return LogLevel.ERROR
    return None


class MwtTokenValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.prev_form = ' '

    def validate_sentence(self, sent):
        self.prev_form = ' '
        super().validate_sentence(sent)

    def validate_word(self, sent, token, mwt):
        form = token['form']
        if mwt['id'][0] == token['id']:
            mwt_end = is_mwt_end(form, self.prev_form)
            if is_mwt_start(self.prev_form) and mwt_end is not None and not token['deprel'] == 'reparandum':
                if mwt_end == LogLevel.ERROR:
                    log(mwt_end, sent, token,
                        f"multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")
                else:
                    log(mwt_end, sent, token,
                        f"possible multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")
        elif conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'No':
            log(LogLevel.ERROR, sent, token, f"multi-word token contains a SpaceAfter=No annotation")

        if conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes':
            self.prev_form = ' '
        elif conllutil.get_misc(token, 'CorrectSpaceAfter', 'No') == 'Yes':
            self.prev_form = ' '
        else:
            self.prev_form = form

    def validate_token(self, sent, token):
        form = token['form']
        mwt_end = is_mwt_end(form, self.prev_form)
        if is_mwt_start(self.prev_form) and mwt_end is not None and not token['deprel'] == 'reparandum':
            if mwt_end == LogLevel.ERROR:
                log(mwt_end, sent, token,
                    f"multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")
            else:
                log(mwt_end, sent, token,
                    f"possible multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")

        if conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes':
            self.prev_form = ' '
        elif conllutil.get_misc(token, 'CorrectSpaceAfter', 'No') == 'Yes':
            self.prev_form = ' '
        else:
            self.prev_form = form

    def validate_mwt_token(self, sent, token):
        if token['id'][0] == token['id'][2]:
            log(LogLevel.ERROR, sent, token, f"multi-word token of length 1 is redundant")
