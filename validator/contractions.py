# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import MwtValidator
from validator.logger import log, LogLevel


class ContractionValidator(MwtValidator):
    def __init__(self, language):
        super().__init__(language)

    @staticmethod
    def is_contraction(form):
        if form.endswith('in\'') and form[0].isalpha():  # -in' -> ing
            return True
        return False

    @staticmethod
    def is_punctuation(token):
        return token['upos'] in ['PUNCT', 'SYM'] and token['form'] not in ['\'', '’']

    def validate_mwt_pair(self, sent, prev_token, token, mwt):
        if self.is_punctuation(prev_token) or self.is_punctuation(token):
            return
        form = prev_token['form'] + token['form']
        form = form.replace('’', '\'')
        if '\'' in form and self.is_contraction(form):
            log(LogLevel.ERROR, sent, token,
                f"incorrectly split dialectal contraction for '{prev_token['form']}][{token['form']}'")