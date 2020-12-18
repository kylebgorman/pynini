Pynini is a Python extension module which allows the user to compile, optimize,
and apply grammar rules. Rules can be compiled into weighted finite state
transducers, pushdown transducers, or multi-pushdown transducers. For general
information and a detailed tutorial, see
[pynini.opengrm.org](http://pynini.opengrm.org).

Pynini is primarily developed by [Kyle Gorman](mailto:kbg@google.com) with the
help of contributors. If you use Pynini in your research, we would appreciate if
you cite the following paper:

> K. Gorman. 2016.
> [Pynini: A Python library for weighted finite-state grammar compilation](http://openfst.cs.nyu.edu/twiki/pub/GRM/Pynini/pynini-paper.pdf).
> In *Proc. ACL Workshop on Statistical NLP and Weighted Automata*, 75-80.

(Note that some of the code samples in the paper are now out of date and not
expected to work.)

# Installation instructions

Users can either install using
[conda-forge](https://conda-forge.org/%5D%5Bconda-forge), or can compile the
extensions and their dependencies from scratch.

### Conda installation

Linux (x86) and Mac OS X users who already have
[conda](https://docs.conda.io/en/latest/) can install Pynini and all
dependencies with the following command

```
conda install -c conda-forge pynini
```

### Source installation

Pynini depends on:

-   A standards-compliant C++17 compiler (GCC \>= 7 or Clang \>= 700)
-   The compatible recent version of [OpenFst](http://openfst.org) (see
    [`NEWS`](NEWS) for this) built with the `far`, `pdt`, `mpdt`, and `script`
    extensions (i.e., built with `./configure --enable-grm`) and headers
-   [Python 3.6+](https://www.python.org) and headers

Once these are installed, issue the following command:

```
python setup.py install
```

To confirm successful installation, run `python test/pynini_test.py`; if all
tests pass, the final line will read `OK`.

Pynini source installation for the current version has been tested on Debian
Linux 5.7.17-1 on x86\_64, GCC 10.2.0, and Python 3.8.5.

# Python version support

Pynini 2.0.0 and onward support Python 3. The Pynini 2.1 versions (onward) drop
Python 2 support.

# License

Pynini is released under the Apache license. See `LICENSE` for more information.

# Interested in contributing?

See `CONTRIBUTING` for more information.

# Mandatory disclaimer

This is not an official Google product.
