# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.logger import log, LogLevel


def validate_sentence_text(sent, language):
    token_text = ""
    word_text = ""
    need_space = False
    last_mwt_id = 0
    need_mwt_space = False
    for token in sent:
        if type(token['id']) is int:
            if need_space:
                token_text += " "
                word_text += " "
            if last_mwt_id >= token['id']:
                if last_mwt_id == token['id']:
                    need_space = need_mwt_space
                else:
                    need_space = False
            else:
                need_space = conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes'
                if last_mwt_id < token['id']:
                    token_text += token['form']
            word_text += token['form']
        elif '-' in token['id']:
            if need_space:
                token_text += " "
                word_text += " "
                need_space = False
            last_mwt_id = token['id'][2]
            need_mwt_space = conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes'
            token_text += token['form']

    if 'text' in sent.metadata:
        if token_text != sent.metadata['text']:
            log(LogLevel.ERROR, sent, None, "text does not match the token sequence",
                expect=sent.metadata['text'],
                actual=token_text)
        if language == 'en' and word_text != sent.metadata['text']:
            log(LogLevel.ERROR, sent, None, "text does not match the word sequence",
                expect=sent.metadata['text'],
                actual=word_text)
    else:
        log(LogLevel.ERROR, sent, None, "sentence text is missing")
