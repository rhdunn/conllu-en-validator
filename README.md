# English CoNLL-U Validator
> A tool for validating English CoNLL-U data files.

Usage:
```
./validate input.conllu OPTIONS | tee output.log
```

- `--language LANG` -- The default language to use if none is specified in the document metadata.
- `--validator VALIDATOR` -- The validation check to perform on the input file.

## Validators
The validator can be one of the following:

contractions
: Check that `'` in dialectal contractions are kept as a single token instead of
  incorrectly split into a multi-word token.

form
: Check that the token and word `FORM` field is consistent with the assigned `UPOS`,
  for example if punctuation tokens contains a single punctuation character.

mwt-tokens
: Check that `SpaceAfter` is not used within multi-word tokens. This will flag the use
  of `SpaceAfter` between other tokens that should be annotated as multi-word tokens.

mwt-words
: Check that the words in the multi-word token are correct.

pos-tags
: Check that the `UPOS` are valid Universal Dependencies values for all treebanks.
  Check that the `XPOS` are valid Penn TreeBank values for English treebanks.

sentence-text
: Check that the token stream matches the sentence text for all treebanks.
  Check that the word stream matches the sentence text for English treebanks.

split-sentences
: Check that the sentences are split correctly.

tokenization
: Check that tokens such as `Mrs.` are single tokens.

## License
Copyright (C) 2023 Reece H. Dunn

`SPDX-License-Identifier:` [Apache-2.0](LICENSE)
