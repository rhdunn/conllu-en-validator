# Copyright (C) 2023 Reece H. Dunn. SPDX-License-Identifier: Apache-2.0

error_count = 0


class LogLevel:
    ERROR = 'ERROR'
    WARN = 'WARN'


def log(level, sent, token, message, expect=None, actual=None):
    if level == LogLevel.ERROR:
        global error_count
        error_count = error_count + 1

    if token is None:
        print(f"{level}: Sentence {sent.metadata['sent_id']} -- {message}")
    elif isinstance(token['id'], int):
        print(f"{level}: Sentence {sent.metadata['sent_id']} token {token['id']} -- {message}")
    else:
        print(f"{level}: Sentence {sent.metadata['sent_id']} token {token['id'][0]}-{token['id'][2]} -- {message}")

    if expect is not None and actual is not None:
        print(f"... Expect: {expect}")
        print(f"... Actual: {actual}")
