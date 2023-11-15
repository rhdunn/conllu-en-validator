# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


def match_lowercase_lemma(sent, token, form, lemma):
    if form.lower() != lemma:
        log(LogLevel.ERROR, sent, token,
            f"{token['xpos']} lemma '{lemma}' is not the lowercase form '{form}' text")


lemma_validators = {
    'RB': match_lowercase_lemma,  # adverb
}


class TokenLemmaValidator(Validator):
    def __init__(self, language):
        super().__init__(language)

    def validate_token(self, sent, token):
        form = conllutil.normalized_form(token)
        lemma = token['lemma']
        xpos = token['xpos']
        if lemma is None or lemma == '_':
            if token['upos'] == 'X' and token['deprel'] == 'goeswith':
                pass  # goeswith have `_` as the lemma
            else:
                log(LogLevel.ERROR, sent, token, f"missing lemma text")
        elif form is None:
            pass  # Missing form text is reported by the 'form' validator.
        elif xpos in lemma_validators:
            lemma_validators[xpos](sent, token, form, lemma)
        else:
            pass
