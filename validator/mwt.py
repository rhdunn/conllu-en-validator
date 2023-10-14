# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

from conllu.models import Token

from validator import conllutil
from validator.validator import Validator
from validator.logger import log, LogLevel


mwt_suffixes = {
    '\'d': {
        'he': [Token(form='he', lemma='he'), Token(form='\'d', lemma=['have', 'would'])],  # he had, he would
        'how': [Token(form='how', lemma='how'), Token(form='\'d', lemma=['have', 'would'])],  # how had, how would
        'I': [Token(form='I', lemma='I'), Token(form='\'d', lemma=['have', 'would'])],  # I had, I would
        'it': [Token(form='it', lemma='it'), Token(form='\'d', lemma=['have', 'would'])],  # it had, it would
        'she': [Token(form='she', lemma='she'), Token(form='\'d', lemma=['have', 'would'])],  # she had, she would
        'that': [Token(form='that', lemma='that'), Token(form='\'d', lemma=['have', 'would'])],  # that had, that would
        'there': [Token(form='there', lemma='there'), Token(form='\'d', lemma=['have', 'would'])],  # there had, there would
        'they': [Token(form='they', lemma='they'), Token(form='\'d', lemma=['have', 'would'])],  # they had, they would
        'we': [Token(form='we', lemma='we'), Token(form='\'d', lemma=['have', 'would'])],  # we had, we would
        'what': [Token(form='what', lemma='what'), Token(form='\'d', lemma=['do', 'have', 'would'])],  # what did, what had, what would
        'where': [Token(form='where', lemma='where'), Token(form='\'d', lemma=['have', 'would'])],  # where had, where would
        'who': [Token(form='who', lemma='who'), Token(form='\'d', lemma=['have', 'would'])],  # who had, who would
        'y': [Token(form='y', lemma='you'), Token(form='\'d', lemma=['have', 'would'])],  # you had, you would
        'you': [Token(form='you', lemma='you'), Token(form='\'d', lemma=['have', 'would'])],  # you had, you would
        None: [Token(upos=['NOUN', 'PROPN']), Token(form='\'d', lemma=['have', 'would'])],  # _ had, _ would
    },
    '\'ll': {
        'he': [Token(form='he', lemma='he'), Token(form='\'ll', lemma='will')],  # he will
        'I': [Token(form='I', lemma='I'), Token(form='\'ll', lemma='will')],  # I will
        'it': [Token(form='it', lemma='it'), Token(form='\'ll', lemma='will')],  # it will
        'nobody': [Token(form='nobody', lemma='nobody'), Token(form='\'ll', lemma='will')],  # nobody will
        'she': [Token(form='she', lemma='she'), Token(form='\'ll', lemma='will')],  # she will
        'that': [Token(form='that', lemma='that'), Token(form='\'ll', lemma='will')],  # that will
        'there': [Token(form='there', lemma='there'), Token(form='\'ll', lemma='will')],  # there will
        'they': [Token(form='they', lemma='they'), Token(form='\'ll', lemma='will')],  # they will
        'this': [Token(form='this', lemma='this'), Token(form='\'ll', lemma='will')],  # this will
        'we': [Token(form='we', lemma='we'), Token(form='\'ll', lemma='will')],  # we will
        'what': [Token(form='what', lemma='what'), Token(form='\'ll', lemma='will')],  # what will
        'where': [Token(form='where', lemma='where'), Token(form='\'ll', lemma='will')],  # where will
        'you': [Token(form='you', lemma='you'), Token(form='\'ll', lemma='will')],  # you will
        None: [Token(upos=['NOUN', 'PROPN']), Token(form='\'ll', lemma='will')],  # _ will
    },
    '\'m': {
        'I': [Token(form='I', lemma='I'), Token(form='\'m', lemma='be')],  # I am
        'no': [Token(form='no', lemma='no'), Token(form='\'m', lemma='madam')],  # no madam
        'yes': [Token(form='yes', lemma='yes'), Token(form='\'m', lemma='madam')],  # yes madam
        None: [Token(upos='VERB'), Token(form='\'m', lemma='they')],  # _ them
    },
    '\'n': {
        None: [Token(), Token(form='\'n', lemma='than')],  # _ than
    },
    '\'re': {
        'they': [Token(form='they', lemma='they'), Token(form='\'re', lemma='be')],  # they are
        'we': [Token(form='we', lemma='we'), Token(form='\'re', lemma='be')],  # we are
        'what': [Token(form='what', lemma='what'), Token(form='\'re', lemma='be')],  # what are
        'where': [Token(form='where', lemma='where'), Token(form='\'re', lemma='be')],  # where are
        'who': [Token(form='who', lemma='who'), Token(form='\'re', lemma='be')],  # who are
        'you': [Token(form='you', lemma='you'), Token(form='\'re', lemma='be')],  # you are
    },
    '\'s': {
        'another': [Token(form='another', lemma='another'), Token(form='\'s', lemma='\'s')],  # POS
        'anybody': [Token(form='anybody', lemma='anybody'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
        'anyone': [Token(form='anyone', lemma='anyone'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
        'anything': [Token(form='anything', lemma='anything'), Token(form='\'s', lemma=['\'s', 'be'])],  # POS, anything is
        'dunno': [Token(form='du', lemma='do'), Token(form='n', lemma='not'), Token(form='no', lemma='know'), Token(form='\'s', lemma='as')],  # do not know as
        'else': [Token(form='else', lemma='else'), Token(form='\'s', lemma='\'s')],  # POS
        'everybody': [Token(form='everybody', lemma='everybody'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
        'everyone': [Token(form='everyone', lemma='everyone'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
        'everything': [Token(form='everything', lemma='everything'), Token(form='\'s', lemma='be')],  # everything is
        'good': [Token(form='good', lemma='good'), Token(form='\'s', lemma='be')],  # good is
        'he': [Token(form='he', lemma='he'), Token(form='\'s', lemma=['be', 'have'])],  # he is, he has
        'here': [Token(form='here', lemma='here'), Token(form='\'s', lemma='be')],  # here is
        'how': [Token(form='how', lemma='how'), Token(form='\'s', lemma='be')],  # how is
        'it': [Token(form='it', lemma='it'), Token(form='\'s', lemma=['be', 'have'])],  # it is, it has
        'let': [Token(form='let', lemma='let'), Token(form='\'s', lemma='we')],  # let us
        'many': [Token(form='many', lemma='many'), Token(form='\'s', lemma='be')],  # many is
        'more': [Token(form='more', lemma='more'), Token(form='\'s', lemma='be')],  # more is
        'nobody': [Token(form='nobody', lemma='nobody'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
        'nothing': [Token(form='nothing', lemma='nothing'), Token(form='\'s', lemma='be')],  # nothing is
        'one': [Token(form='one', lemma='one'), Token(form='\'s', lemma=['\'s', 'be'])],  # POS, _ is
        'other': [Token(form='other', lemma='other'), Token(form='\'s', lemma='\'s')],  # POS
        'she': [Token(form='she', lemma='she'), Token(form='\'s', lemma=['be', 'have'])],  # she is, she has
        'so': [Token(form='so', lemma='so'), Token(form='\'s', lemma='be')],  # so is
        'somebody': [Token(form='somebody', lemma='somebody'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
        'someone': [Token(form='someone', lemma='someone'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
        'something': [Token(form='something', lemma='something'), Token(form='\'s', lemma='be')],  # something is
        'that': [Token(form='that', lemma='that'), Token(form='\'s', lemma=['be', 'have'])],  # that is, that has
        'there': [Token(form='there', lemma='there'), Token(form='\'s', lemma=['be', 'have'])],  # there is, there has
        'this': [Token(form='this', lemma='this'), Token(form='\'s', lemma='be')],  # this is
        'what': [Token(form='what', lemma='what'), Token(form='\'s', lemma='be')],  # what is
        'whatever': [Token(form='whatever', lemma='whatever'), Token(form='\'s', lemma='be')],  # whatever is
        'when': [Token(form='when', lemma='when'), Token(form='\'s', lemma='be')],  # when is
        'where': [Token(form='where', lemma='where'), Token(form='\'s', lemma='be')],  # where is
        'which': [Token(form='which', lemma='which'), Token(form='\'s', lemma='be')],  # which is
        'who': [Token(form='who', lemma='who'), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, who is, who has
        'why': [Token(form='why', lemma='why'), Token(form='\'s', lemma='be')],  # why is
        None: [Token(upos=['NOUN', 'PROPN', 'NUM', 'VERB']), Token(form='\'s', lemma=['\'s', 'be', 'have'])],  # POS, _ is, _ has
    },
    '\'ve': {
        'can\'t': [Token(form='ca', lemma='can'), Token(form='n\'t', lemma='not'), Token(form='\'ve', lemma='have')],  # can not have
        'could': [Token(form='could', lemma='could'), Token(form='\'ve', lemma='have')],  # could have
        'I': [Token(form='I', lemma='I'), Token(form='\'ve', lemma='have')],  # I have
        'must': [Token(form='must', lemma='must'), Token(form='\'ve', lemma='have')],  # must have
        'probably': [Token(form='probably', lemma='probably'), Token(form='\'ve', lemma='have')],  # probably have
        'should': [Token(form='should', lemma='should'), Token(form='\'ve', lemma='have')],  # should have
        'they': [Token(form='they', lemma='they'), Token(form='\'ve', lemma='have')],  # they have
        'what': [Token(form='what', lemma='what'), Token(form='\'ve', lemma='have')],  # what have
        'we': [Token(form='we', lemma='we'), Token(form='\'ve', lemma='have')],  # we have
        'who': [Token(form='who', lemma='who'), Token(form='\'ve', lemma='have')],  # who have
        'would': [Token(form='would', lemma='would'), Token(form='\'ve', lemma='have')],  # would have
        'you': [Token(form='you', lemma='you'), Token(form='\'ve', lemma='have')],  # you have
    },
    'if': {
        '\'s': [Token(form='\'s', lemma='as'), Token(form='if', lemma='if')],  # as if
    },
    'is': {
        '\'t': [Token(form='\'t', lemma='it'), Token(form='is', lemma='be')],  # it is
    },
    'n\'t': {
        '\'tai': [Token(form='\'t', lemma='it'), Token(form='ai', lemma='be'), Token(form='n\'t', lemma='not')],  # it is not
        '\'tis': [Token(form='\'t', lemma='it'), Token(form='is', lemma='be'), Token(form='n\'t', lemma='not')],  # it is not
        '\'twas': [Token(form='\'t', lemma='it'), Token(form='was', lemma='be'), Token(form='n\'t', lemma='not')],  # it was not
        'ai': [Token(form='ai', lemma='be'), Token(form='n\'t', lemma='not')],  # are not
        'are': [Token(form='are', lemma='be'), Token(form='n\'t', lemma='not')],  # are not
        'c\'d': [Token(form='c\'d', lemma='could'), Token(form='n\'t', lemma='not')],  # could not
        'ca': [Token(form='ca', lemma='can'), Token(form='n\'t', lemma='not')],  # can not
        'could': [Token(form='could', lemma='could'), Token(form='n\'t', lemma='not')],  # could not
        'did': [Token(form='did', lemma='do'), Token(form='n\'t', lemma='not')],  # did not
        'do': [Token(form='do', lemma='do'), Token(form='n\'t', lemma='not')],  # do not
        'does': [Token(form='does', lemma='do'), Token(form='n\'t', lemma='not')],  # does not
        'had': [Token(form='had', lemma='have'), Token(form='n\'t', lemma='not')],  # had not
        'hai': [Token(form='hai', lemma='have'), Token(form='n\'t', lemma='not')],  # has not, have not
        'has': [Token(form='has', lemma='have'), Token(form='n\'t', lemma='not')],  # has not
        'have': [Token(form='have', lemma='have'), Token(form='n\'t', lemma='not')],  # have not
        'is': [Token(form='is', lemma='be'), Token(form='n\'t', lemma='not')],  # is not
        'may': [Token(form='may', lemma='may'), Token(form='n\'t', lemma='not')],  # may not
        'might': [Token(form='might', lemma='might'), Token(form='n\'t', lemma='not')],  # might not
        'mus': [Token(form='mus', lemma='must'), Token(form='n\'t', lemma='not')],  # must not
        'must': [Token(form='must', lemma='must'), Token(form='n\'t', lemma='not')],  # must not
        'need': [Token(form='need', lemma='need'), Token(form='n\'t', lemma='not')],  # need not
        'ought': [Token(form='ought', lemma='ought'), Token(form='n\'t', lemma='not')],  # ought not
        'sha': [Token(form='sha', lemma='shall'), Token(form='n\'t', lemma='not')],  # shall not
        'should': [Token(form='should', lemma='should'), Token(form='n\'t', lemma='not')],  # should not
        'was': [Token(form='was', lemma='be'), Token(form='n\'t', lemma='not')],  # was not
        'were': [Token(form='were', lemma='be'), Token(form='n\'t', lemma='not')],  # were not
        'wo': [Token(form='wo', lemma='will'), Token(form='n\'t', lemma='not')],  # will not
        'would': [Token(form='would', lemma='would'), Token(form='n\'t', lemma='not')],  # would not
    },
    'na': {
        'gon': [Token(form='gon', lemma='go'), Token(form='na', lemma='to')],  # going to
        'wan': [Token(form='wan', lemma='want'), Token(form='na', lemma='to')],  # want to
    },
    'no': {
        'dun': [Token(form='du', lemma='do'), Token(form='n', lemma='not'), Token(form='no', lemma='know')],  # do not know
    },
    'not': {
        'can': [Token(form='can', lemma='can'), Token(form='not', lemma='not')],  # can not
    },
    's\'': {
        None: [Token(upos=['NOUN', 'PROPN']), Token(form='\'', lemma='\'s')],  # POS
    },
    'ta': {
        'got': [Token(form='got', lemma='get'), Token(form='ta', lemma='to')],  # got to
        'ough': [Token(form='ought', lemma='ought'), Token(form='a', lemma='to')],  # ought to
        'out': [Token(form='out', lemma='out'), Token(form='ta', lemma='of')],  # out of
        'sor': [Token(form='sort', lemma='sort'), Token(form='a', lemma='of')],  # sort of
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
                value = token[field]
                if field == 'form':
                    value = conllutil.normalized_form(token)

                if isinstance(part[field], str):
                    if value != part[field]:
                        log(LogLevel.ERROR, sent, token,
                            f"unexpected multi-word token '{mwt['form']}' part {field} '{value}', expected '{part[field]}'")
                else:  # list
                    if value not in part[field]:
                        expected = '|'.join(part[field])
                        log(LogLevel.ERROR, sent, token,
                            f"unexpected multi-word token '{mwt['form']}' part {field} '{value}', expected '{expected}'")
            self.part_index = self.part_index + 1

    def tokenize_mwt(self, parts, form):
        self.parts = []
        part_offset = 0
        for part in parts:
            part_len = len(part['form'])
            self.parts.append(Token(part))
            self.parts[-1]['form'] = form[part_offset:part_offset + part_len]
            part_offset = part_offset + part_len

    def match_suffix(self, form, suffix, is_upper_case=False):
        if form.endswith(suffix):
            return form.replace(suffix, ''), suffix, '\'', is_upper_case

        curly_suffix = suffix.replace('\'', '’')
        if form.endswith(curly_suffix):
            return form.replace(curly_suffix, ''), curly_suffix, '’', is_upper_case

        if not is_upper_case:
            return self.match_suffix(form, suffix.upper(), True)
        return None, None, None, False

    def mwt_text(self, sent, start_id, end_id):
        form = ''
        for token in sent:
            if isinstance(token['id'], int) and token['id'] >= start_id and token['id'] <= end_id:
                form = form + conllutil.normalized_form(token)
        return form

    def validate_mwt_token(self, sent, token):
        form = self.mwt_text(sent, token['id'][0], token['id'][2])
        for suffix, bases in mwt_suffixes.items():
            base_form, suffix, quote_style, is_upper_case = self.match_suffix(form, suffix)
            if base_form is None:
                continue

            base_form = form.replace(suffix, '').replace('’', '\'')
            if base_form in bases:  # lowercase
                self.tokenize_mwt(bases[base_form], form)
            elif base_form == 'i' and 'I' in bases:  # incorrectly capitalized personal pronoun 'I'
                self.tokenize_mwt(bases['I'], form)
            elif base_form.lower() in bases:  # capitalized, uppercase
                self.tokenize_mwt(bases[base_form.lower()], form)
            elif None in bases:  # part of speech + suffix
                self.parts = [Token(part) for part in bases[None]]
                if is_upper_case:
                    self.parts[1]['form'] = self.parts[1]['form'].upper().replace('\'', quote_style)
                else:
                    self.parts[1]['form'] = self.parts[1]['form'].replace('\'', quote_style)
                self.parts[0]['form'] = form.replace(self.parts[1]['form'], '')
            else:
                log(LogLevel.ERROR, sent, token, f"unrecognized multi-word base form '{base_form}' for suffix '{suffix}'")
                self.parts = [Token(form=base_form), Token(form=suffix)]

            self.part_index = 0
            return

        log(LogLevel.ERROR, sent, token, f"unrecognized multi-word token form '{form}'")
        self.parts = []
        self.index = -1
