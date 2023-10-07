# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
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


def validate_mwt_tokens(sent, language):
    first_mwt_id = 0
    last_mwt_id = 0
    prev_form = ' '
    for token in sent:
        if type(token['id']) is int:
            form = token['form']
            if last_mwt_id < token['id'] or first_mwt_id == token['id']:
                mwt_end = is_mwt_end(form, prev_form)
                if is_mwt_start(prev_form) and mwt_end is not None and not token['deprel'] == 'reparandum':
                    if mwt_end == LogLevel.ERROR:
                        log(mwt_end, sent, token,
                            f"multi-word continuation without a multi-word token range for '{prev_form}][{form}'")
                    else:
                        log(mwt_end, sent, token,
                            f"possible multi-word continuation without a multi-word token range for '{prev_form}][{form}'")
            elif conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'No':
                log(LogLevel.ERROR, sent, token, f"multi-word token contains a SpaceAfter=No annotation")

            if conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes':
                prev_form = ' '
            elif conllutil.get_misc(token, 'CorrectSpaceAfter', 'No') == 'Yes':
                prev_form = ' '
            else:
                prev_form = form
        else:
            first_mwt_id = token['id'][0]
            last_mwt_id = token['id'][2]
            if first_mwt_id == last_mwt_id:
                log(LogLevel.ERROR, sent, token, f"multi-word token of length 1 is redundant")
