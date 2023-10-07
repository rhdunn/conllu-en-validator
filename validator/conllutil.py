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


def get_misc(token, attr, default):
    if 'misc' not in token:
        return default
    misc = token['misc']
    if misc is None or attr not in misc:
        return default
    return misc[attr]
