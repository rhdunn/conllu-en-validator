# English CoNLL-U Validator
> A tool for validating English CoNLL-U data files.

Usage:
```
./validate input.conllu OPTIONS | tee output.log
```

- `--language LANG` -- The default language to use if none is specified in the document metadata.

## Validators
The `--validator` can be one of the following:

mwt-tokens
: Check that `SpaceAfter` is not used within multi-word tokens. This will flag the use
of `SpaceAfter` between other tokens that should be annotated as multi-word tokens.

mwt-words
: Check that the words in the multi-word token are correct.

pos-tags
: Check that the `UPOS` are valid Universal Dependencies values for all treebanks.
Check that the `XPOS` are valid Penn TreeBank values for English treebanks.

sentence-text
: Check that the token stream match the sentence text for all treebanks. 
  Check that the word stream match the sentence text for English treebanks.

## License
Copyright (C) 2023 Reece H. Dunn

`SPDX-License-Identifier:` [Apache-2.0](LICENSE)
