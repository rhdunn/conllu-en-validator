# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


mwt_suffixes = {
    '\'d': [
        'he',
        'I',
        'it',
        'she',
        'they',
        'we',
        'you',
    ]
}


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


class MwtWordValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.parts = []
        self.part_index = -1

    def validate_word(self, sent, token, mwt):
        if len(self.parts) == 0:
            return

        form = token['form']
        if len(self.parts) == self.part_index:
            log(LogLevel.ERROR, sent, token, f"unexpected multi-word token part '{form}'")
        else:
            part_form = self.parts[self.part_index]
            if form != part_form:
                log(LogLevel.ERROR, sent, token, f"unexpected multi-word token part '{form}', expected '{part_form}'")
            self.part_index = self.part_index + 1

    def validate_mwt_token(self, sent, token):
        form = token['form']
        for suffix, bases in mwt_suffixes.items():
            if form.endswith(suffix):
                pass
            else:
                continue

            base_form = form.replace(suffix, '')
            if base_form in bases:  # lowercase
                pass
            elif base_form not in ['I', 'i'] and base_form.lower() in bases:  # capitalized, uppercase
                pass
            else:
                log(LogLevel.ERROR, sent, token, f"unrecognized multi-word base form '{base_form}' for suffix '{suffix}'")

            self.parts = [base_form, suffix]
            self.part_index = 0
            return

        log(LogLevel.ERROR, sent, token, f"unrecognized multi-word token form '{form}'")
        self.parts = []
        self.index = -1
