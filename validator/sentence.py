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

    def validate_sentence(self, sent):
        self.token_text = ""
        self.word_text = ""
        self.need_space = False
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

    def validate_word(self, sent, token, mwt):
        if self.need_space:
            self.token_text += " "
            self.word_text += " "
        if mwt['id'][2] == token['id']:
            self.need_space = conllutil.get_misc(mwt, 'SpaceAfter', 'Yes') == 'Yes'
        else:
            self.need_space = False
        self.word_text += token['form']

    def validate_token(self, sent, token):
        if self.need_space:
            self.token_text += " "
            self.word_text += " "
        self.need_space = conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes'
        self.token_text += token['form']
        self.word_text += token['form']

    def validate_mwt_token(self, sent, token):
        if self.need_space:
            self.token_text += " "
            self.word_text += " "
            self.need_space = False
        self.token_text += token['form']


class SplitSentenceValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.prev_sent = None

    def validate_sentence(self, sent):
        if self.prev_sent is not None:
            etok = self.prev_sent[-1]
            if etok['upos'] not in ['PUNCT']:
                if 'newpar' not in sent.metadata and 'newpar id' not in sent.metadata:
                    log(LogLevel.ERROR, sent, None,
                        f"sentence ends without punctuation or new paragraph metadata")
        self.prev_sent = sent
