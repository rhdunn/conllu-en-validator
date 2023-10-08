# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

class Validator:
    def __init__(self, language):
        self.language = language

    def switch_language(self, language):
        self.language = language

    def validate_sentence(self, sent):
        mwt = None
        for token in sent:
            if type(token['id']) is int:
                if mwt is not None:
                    if mwt['id'][2] >= token['id']:
                        self.validate_word(sent, token, mwt)
                    else:
                        self.validate_token(sent, token)
                else:
                    self.validate_token(sent, token)
            else:
                mwt = token
                self.validate_mwt_token(sent, token)

    def validate_token(self, sent, token):
        pass

    def validate_word(self, sent, token, mwt):
        self.validate_token(sent, token)

    def validate_mwt_token(self, sent, token):
        pass
