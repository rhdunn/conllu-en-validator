# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

class Validator:
    def __init__(self, language):
        self.language = language

    def validate_sentence(self, sent):
        for token in sent:
            if type(token['id']) is int:
                self.validate_token(sent, token)
            else:
                self.validate_mwt_token(sent, token)

    def validate_token(self, sent, token):
        pass

    def validate_mwt_token(self, sent, token):
        pass
