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

    def validate_mwt_pair(self, sent, prev_token, token, mwt):
        form = prev_token['form'] + token['form']
        form = form.replace('’', '\'')
        if '\'' in form and self.is_contraction(form):
            log(LogLevel.ERROR, sent, token,
                f"incorrectly split dialectal contraction for '{prev_token['form']}][{token['form']}'")
