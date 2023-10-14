# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil


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
        self.prev_space_after = True

    def validate_sentence(self, sent):
        self.prev_token = None
        self.prev_space_after = True
        super().validate_sentence(sent)

    def validate_mwt_pair(self, sent, prev_token, token, mwt):
        pass

    def validate_token(self, sent, token):
        if self.prev_token is not None and not self.prev_space_after:
            self.validate_mwt_pair(sent, self.prev_token, token, None)
        self.prev_token = token
        self.prev_space_after = conllutil.space_after(token)

    def validate_word(self, sent, token, mwt):
        if self.prev_token is not None and not self.prev_space_after:
            self.validate_mwt_pair(sent, self.prev_token, token, mwt)
        self.prev_token = token
        if token['id'] == mwt['id'][2]:  # last word
            self.prev_space_after = conllutil.space_after(mwt)
        else:
            self.prev_space_after = True
