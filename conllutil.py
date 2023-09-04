# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0


def parse_filelist(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            if line == '':
                continue
            yield line
