# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator.validator import MwtValidator
from validator.logger import log, LogLevel


dialectal_continuations = [
    'an\'',  # and
    '\'bout',  # about
    '\'em',  # them
    '\'fore',  # before
    '\'twas',  # 't was
    '\'twill',  # 't will
]


class ContractionValidator(MwtValidator):
    def __init__(self, language):
        super().__init__(language)

    @staticmethod
    def is_contraction(form):
        if form.endswith('in\'') and form[0].isalpha():  # -in' -> ing
            return True
        return form.lower() in dialectal_continuations

    @staticmethod
    def is_punctuation(token):
        if token['upos'] not in ['PUNCT', 'SYM']:
            return False
        if token['form'] in ['\'', '’']:
            return token['deprel'] == 'reparandum'
        return False

    def validate_mwt_pair(self, sent, prev_token, token, mwt):
        if self.is_punctuation(prev_token) or self.is_punctuation(token):
            return
        form = prev_token['form'] + token['form']
        form = form.replace('’', '\'')
        if '\'' in form and self.is_contraction(form):
            log(LogLevel.ERROR, sent, token,
                f"incorrectly split dialectal contraction for '{prev_token['form']}][{token['form']}'")
