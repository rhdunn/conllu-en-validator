# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator.validator import Validator
from validator.logger import log, LogLevel


abbreviations = [
    'Dr',  # Doctor; Drive
    'Miss',
    'Mr',
    'Mrs',
    'St',  # Saint; Street
]


class TokenizationValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.prev_token = None

    def validate_sentence(self, sent):
        self.prev_token = None
        super().validate_sentence(sent)

    def validate_before_full_stop(self, sent, token):
        form = token['form']
        if form in abbreviations:
            log(LogLevel.ERROR, sent, token, f"abbreviation '{form}.' should be a single token")

    def validate_token(self, sent, token):
        upos = token['upos']
        form = token['form']
        if upos == 'PUNCT' and form == '.' and self.prev_token is not None:
            self.validate_before_full_stop(sent, self.prev_token)
        self.prev_token = token
