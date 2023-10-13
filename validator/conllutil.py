# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

import conllu


def parse_filelist(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            if line == '':
                continue
            yield line


def parse_conllu(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for sent in conllu.parse_incr(f):
            yield sent


def get_feat(token, attr, default):
    if 'feats' not in token:
        return default
    feat = token['feats']
    if feat is None or attr not in feat:
        return default
    return feat[attr]


def get_misc(token, attr, default):
    if 'misc' not in token:
        return default
    misc = token['misc']
    if misc is None or attr not in misc:
        return default
    return misc[attr]


def normalized_form(token):
    form = token['form']
    if get_feat(token, 'Typo', 'No') == 'Yes':
        return get_misc(token, 'CorrectForm', form)
    if get_feat(token, 'Abbr', 'No') == 'Yes':
        return get_misc(token, 'CorrectForm', form)
    if get_feat(token, 'Style', 'None') in ['Coll', 'Expr', 'Vrnc']:  # colloquial, expressive, vernacular
        return get_misc(token, 'CorrectForm', form)
    if get_feat(token, 'Style', 'None') == 'Arch':  # archaic
        return get_misc(token, 'ModernForm', form)
    return form
