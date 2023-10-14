# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

class Validator:
    def __init__(self, language):
        self.language = language

    def switch_language(self, language):
        self.language = language

    def validate_sentence(self, sent):
        mwt = None
        for token in sent:
            if type(token['id']) is int:  # token, word
                if mwt is not None:
                    if mwt['id'][2] >= token['id']:
                        self.validate_word(sent, token, mwt)
                    else:
                        self.validate_token(sent, token)
                else:
                    self.validate_token(sent, token)
            elif '.' in token['id']:  # empty node
                self.validate_empty_node(sent, token)
            else:  # multi-word token
                mwt = token
                self.validate_mwt_token(sent, token)

    def validate_token(self, sent, token):
        pass

    def validate_word(self, sent, token, mwt):
        self.validate_token(sent, token)

    def validate_mwt_token(self, sent, token):
        pass

    def validate_empty_node(self, sent, token):
        pass


class MwtValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.prev_token = None

    def validate_sentence(self, sent):
        self.prev_token = None
        super().validate_sentence(sent)

    def validate_token(self, sent, token):
        self.prev_token = token

    def validate_word(self, sent, token, mwt):
        self.prev_token = token
