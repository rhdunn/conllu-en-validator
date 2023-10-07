# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


class SentenceTextValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.token_text = ""
        self.word_text = ""
        self.need_space = False
        self.last_mwt_id = 0
        self.need_mwt_space = False

    def validate_sentence(self, sent):
        self.token_text = ""
        self.word_text = ""
        self.need_space = False
        self.last_mwt_id = 0
        self.need_mwt_space = False
        super().validate_sentence(sent)

        if 'text' in sent.metadata:
            if self.token_text != sent.metadata['text']:
                log(LogLevel.ERROR, sent, None, "text does not match the token sequence",
                    expect=sent.metadata['text'],
                    actual=self.token_text)
            if self.language == 'en' and self.word_text != sent.metadata['text']:
                log(LogLevel.ERROR, sent, None, "text does not match the word sequence",
                    expect=sent.metadata['text'],
                    actual=self.word_text)
        else:
            log(LogLevel.ERROR, sent, None, "sentence text is missing")

    def validate_token(self, sent, token):
        if self.need_space:
            self.token_text += " "
            self.word_text += " "
        if self.last_mwt_id >= token['id']:
            if self.last_mwt_id == token['id']:
                self.need_space = self.need_mwt_space
            else:
                self.need_space = False
        else:
            self.need_space = conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes'
            if self.last_mwt_id < token['id']:
                self.token_text += token['form']
        self.word_text += token['form']

    def validate_mwt_token(self, sent, token):
        if self.need_space:
            self.token_text += " "
            self.word_text += " "
            self.need_space = False
        self.last_mwt_id = token['id'][2]
        self.need_mwt_space = conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes'
        self.token_text += token['form']
