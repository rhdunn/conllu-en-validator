# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from conllu.models import Token

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


mwt_suffixes = {
    '\'d': {
        'he': [Token(form='he', lemma='he'), Token(form='\'d', lemma='would')],
        'I': [Token(form='I', lemma='I'), Token(form='\'d', lemma='would')],
        'it': [Token(form='it', lemma='it'), Token(form='\'d', lemma='would')],
        'she': [Token(form='she', lemma='she'), Token(form='\'d', lemma='would')],
        'they': [Token(form='they', lemma='they'), Token(form='\'d', lemma='would')],
        'we': [Token(form='we', lemma='we'), Token(form='\'d', lemma='would')],
        'you': [Token(form='you', lemma='you'), Token(form='\'d', lemma='would')],
    },
    '\'m': {
        'I': [Token(form='I', lemma='I'), Token(form='\'m', lemma='be')],  # I am
    },
    '\'re': {
        'they': [Token(form='they', lemma='they'), Token(form='\'re', lemma='be')],  # they are
        'we': [Token(form='we', lemma='we'), Token(form='\'re', lemma='be')],  # we are
        'you': [Token(form='you', lemma='you'), Token(form='\'re', lemma='be')],  # you are
    },
    '\'s': {
        'he': [Token(form='he', lemma='he'), Token(form='\'s', lemma=['be', 'have'])],  # he is, he has
        'here': [Token(form='here', lemma='here'), Token(form='\'s', lemma='be')],  # here is
        'it': [Token(form='it', lemma='it'), Token(form='\'s', lemma=['be', 'have'])],  # it is, it has
        'let': [Token(form='let', lemma='let'), Token(form='\'s', lemma='we')],  # let us
        'she': [Token(form='she', lemma='she'), Token(form='\'s', lemma=['be', 'have'])],  # she is, she has
        'that': [Token(form='that', lemma='that'), Token(form='\'s', lemma='be')],  # that is
        'there': [Token(form='there', lemma='there'), Token(form='\'s', lemma='be')],  # there is
        'what': [Token(form='what', lemma='what'), Token(form='\'s', lemma='be')],  # what is
        'who': [Token(form='who', lemma='who'), Token(form='\'s', lemma='be')],  # who is
        None: [Token(upos=['NOUN', 'PROPN']), Token(form='\'s', lemma=['\'s', 'be'])],  # possessive, _ is
    },
}


def is_mwt_start(form):
    return form[-1].isalpha()


def is_mwt_end(form, prev_form):
    if form[0] in ['\'', '’']:
        for c in form:
            if c.isalpha():
                return LogLevel.ERROR
        if len(form) == 1 and prev_form[-1] in ['s', 'S']:
            return LogLevel.WARN  # possessive or end quote
    if form[0].isalpha():
        return LogLevel.ERROR
    return None


class MwtTokenValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.prev_form = ' '

    def validate_sentence(self, sent):
        self.prev_form = ' '
        super().validate_sentence(sent)

    def validate_word(self, sent, token, mwt):
        form = token['form']
        if mwt['id'][0] == token['id']:
            mwt_end = is_mwt_end(form, self.prev_form)
            if is_mwt_start(self.prev_form) and mwt_end is not None and not token['deprel'] == 'reparandum':
                if mwt_end == LogLevel.ERROR:
                    log(mwt_end, sent, token,
                        f"multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")
                else:
                    log(mwt_end, sent, token,
                        f"possible multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")
        elif conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'No':
            log(LogLevel.ERROR, sent, token, f"multi-word token contains a SpaceAfter=No annotation")

        if conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes':
            self.prev_form = ' '
        elif conllutil.get_misc(token, 'CorrectSpaceAfter', 'No') == 'Yes':
            self.prev_form = ' '
        else:
            self.prev_form = form

    def validate_token(self, sent, token):
        form = token['form']
        mwt_end = is_mwt_end(form, self.prev_form)
        if is_mwt_start(self.prev_form) and mwt_end is not None and not token['deprel'] == 'reparandum':
            if mwt_end == LogLevel.ERROR:
                log(mwt_end, sent, token,
                    f"multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")
            else:
                log(mwt_end, sent, token,
                    f"possible multi-word continuation without a multi-word token range for '{self.prev_form}][{form}'")

        if conllutil.get_misc(token, 'SpaceAfter', 'Yes') == 'Yes':
            self.prev_form = ' '
        elif conllutil.get_misc(token, 'CorrectSpaceAfter', 'No') == 'Yes':
            self.prev_form = ' '
        else:
            self.prev_form = form

    def validate_mwt_token(self, sent, token):
        if token['id'][0] == token['id'][2]:
            log(LogLevel.ERROR, sent, token, f"multi-word token of length 1 is redundant")


class MwtWordValidator(Validator):
    def __init__(self, language):
        super().__init__(language)
        self.parts = []
        self.part_index = -1

    def validate_word(self, sent, token, mwt):
        if len(self.parts) == 0:
            return

        if len(self.parts) == self.part_index:
            log(LogLevel.ERROR, sent, token, f"unexpected multi-word token '{mwt['form']}' part '{token['form']}'")
        else:
            part = self.parts[self.part_index]
            for field in part.keys():
                if isinstance(part[field], str):
                    if token[field] != part[field]:
                        log(LogLevel.ERROR, sent, token,
                            f"unexpected multi-word token '{mwt['form']}' part {field} '{token[field]}', expected '{part[field]}'")
                else:  # list
                    if token[field] not in part[field]:
                        expected = '|'.join(part[field])
                        log(LogLevel.ERROR, sent, token,
                            f"unexpected multi-word token '{mwt['form']}' part {field} '{token[field]}', expected '{expected}'")
            self.part_index = self.part_index + 1

    def validate_mwt_token(self, sent, token):
        form = token['form']
        for suffix, bases in mwt_suffixes.items():
            if form.endswith(suffix):
                pass
            else:
                continue

            base_form = form.replace(suffix, '')
            if base_form in bases:  # lowercase
                self.parts = bases[base_form]
            elif base_form == 'i' and 'I' in bases:  # incorrectly capitalized personal pronoun 'I'
                parts = bases['I']
                self.parts = [
                    Token(form=base_form, lemma=parts[0]['lemma']),
                    Token(form=suffix, lemma=parts[1]['lemma'])
                ]
            elif base_form.lower() in bases:  # capitalized, uppercase
                parts = bases[base_form.lower()]
                self.parts = [
                    Token(form=base_form, lemma=parts[0]['lemma']),
                    Token(form=suffix, lemma=parts[1]['lemma'])
                ]
            elif None in bases:  # part of speech + suffix
                parts = bases[None]
                self.parts = [
                    Token(form=base_form, upos=parts[0]['upos']),
                    Token(form=suffix, lemma=parts[1]['lemma'])
                ]
            else:
                log(LogLevel.ERROR, sent, token, f"unrecognized multi-word base form '{base_form}' for suffix '{suffix}'")
                self.parts = [Token(form=base_form), Token(form=suffix)]

            self.part_index = 0
            return

        log(LogLevel.ERROR, sent, token, f"unrecognized multi-word token form '{form}'")
        self.parts = []
        self.index = -1
