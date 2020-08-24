# Lint as: python3
# For general information on the Pynini grammar compilation library, see
# pynini.opengrm.org.
"""Constants for ASCII bytestrings, mirroring <ctype.h> functionality."""

import string

import pynini

# Note that [0] is missing, as it is always used to denote epsilon.
BYTES = pynini.union(*("[{}]".format(i) for i in range(1, 256))).optimize()
DIGIT = pynini.union(*string.digits).optimize()
LOWER = pynini.union(*string.ascii_lowercase).optimize()
UPPER = pynini.union(*string.ascii_uppercase).optimize()
ALPHA = pynini.union(LOWER, UPPER).optimize()
ALNUM = pynini.union(DIGIT, ALPHA).optimize()
HEX = pynini.union(*string.hexdigits).optimize()

# NB: Python's string.whitespace includes \v and \f, but Thrax's bytes.grm
# doesn't, and we follow the latter.
SPACE = pynini.union(" ", "\t", "\n", "\r").optimize()
NOT_SPACE = pynini.difference(BYTES, SPACE).optimize()
NOT_QUOTE = pynini.difference(BYTES, r'"').optimize()

# NB: Doing this manually as otherwise I'd have to escape the brackets.
PUNCT = pynini.union(r"!", r'"', r"#", r"$", r"%", r"&", r"'", r"(", r")", r"*",
                     r"+", r",", r"-", r".", r"/", r":", r"<", r"=", r">", r"?",
                     r"@", r"\[", r"\\", r"\]", r"^", r"_", r"`", r"{", r"|",
                     r"}", r"~").optimize()
GRAPH = pynini.union(ALNUM, PUNCT).optimize()

