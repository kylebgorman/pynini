# Dockerfile
# Pierre-André Noël, May 12th 2020
# Copyright © Element AI Inc. All rights reserved.
# Apache License, Version 2.0
#
# This builds `manylinux_2_28_x86_64` Python wheels for `pynini`, wrapping
# all its dependencies.
#
# This Dockerfile uses multi-stage builds; for more information, see:
# https://docs.docker.com/develop/develop-images/multistage-build/
# 
# The recommended installation method for Pynini is through Conda-Forge. This gives Linux
# x86-64 users another option: installing a precompiled module from PyPI.
# 
# 
# To build wheels and run Pynini's tests, run:
# 
#     docker build --target=run-tests -t build-pynini-wheels .
# 
# To extract the resulting wheels from the Docker image, run:
#
#     docker run --rm -v `pwd`:/io build-pynini-wheels cp -r /wheelhouse /io
#
# Notice that this also generates Cython wheels.
# 
# Then, `twine` (https://twine.readthedocs.io/en/latest/) can be used to
# publish the resulting Pynini wheels.

# ******************************************************
# *** All the following images are based on this one ***
# ******************************************************
from quay.io/pypa/manylinux_2_28_x86_64 AS common

# The versions we want in the wheels.
ENV FST_VERSION "1.8.3"
ENV PYNINI_VERSION "2.1.6.post1"

# Python 3.6m and 3.7m are end-of-life. The code genreated by Cython appears to
# be incompatble with the Python 3.13t CPython API.
RUN rm -rd \
    /opt/python/cp36-cp36m \
    /opt/python/cp37-cp37m \
    /opt/python/cp313-cp313t

# ***********************************************************************
# *** Image providing all the requirements for building Pynini wheels ***
# ***********************************************************************
FROM common AS wheel-building-env

# Location of OpenFst and Pynini.
ENV FST_DOWNLOAD_PREFIX "https://www.openfst.org/twiki/pub/FST/FstDownload"
ENV PYNINI_DOWNLOAD_PREFIX "https://www.opengrm.org/twiki/pub/GRM/PyniniDownload"

# Note that our certificates are not known to the version of wget available in this image.

# Gets and unpack OpenFst source.
RUN yum install -y wget
RUN cd /tmp \
    && wget -q --no-check-certificate "${FST_DOWNLOAD_PREFIX}/openfst-${FST_VERSION}.tar.gz" \
    && tar -xzf "openfst-${FST_VERSION}.tar.gz" \
    && rm "openfst-${FST_VERSION}.tar.gz"

# Compiles OpenFst.
RUN cd "/tmp/openfst-${FST_VERSION}" \
    && ./configure --enable-grm \
    && make --jobs 4 install \
    && rm -rd "/tmp/openfst-${FST_VERSION}"

# Gets and unpacks Pynini source.
RUN mkdir -p /src && cd /src \
    && wget -q --no-check-certificate "${PYNINI_DOWNLOAD_PREFIX}/pynini-${PYNINI_VERSION}.tar.gz" \
    && tar -xzf "pynini-${PYNINI_VERSION}.tar.gz" \
    && rm "pynini-${PYNINI_VERSION}.tar.gz"

# Installs requirements in all our Pythons.
RUN for PYBIN in /opt/python/*/bin; do \
    "${PYBIN}/pip" install --verbose --upgrade \
        pip -r "/src/pynini-${PYNINI_VERSION}/requirements.txt" || exit; \
done

# **********************************************************
# *** Image making pynini wheels (placed in /wheelhouse) ***
# **********************************************************
FROM wheel-building-env AS build-wheels

# Compiles the wheels to a temporary directory.
RUN for PYBIN in /opt/python/*/bin; do \
    "${PYBIN}/pip" wheel -v "/src/pynini-${PYNINI_VERSION}" -w /tmp/wheelhouse/ \
    || exit; \
done

# Bundles external shared libraries into the wheels.
# See https://github.com/pypa/manylinux/tree/manylinux2014
RUN for WHL in /tmp/wheelhouse/pynini*.whl; do \
    auditwheel repair "${WHL}" -w /wheelhouse/ || exit; \
done

# Removes the non-repaired wheels.
RUN rm -rd /tmp/wheelhouse

# *******************************************************
# *** Installs wheels in a fresh (OpenFst-free) image ***
# *******************************************************
FROM common AS install-pynini-from-wheel

# Grabs the wheels (but just the wheels) from the previous image.
COPY --from=build-wheels /wheelhouse /wheelhouse

# Installs the wheels in all our Pythons.
RUN for PYBIN in /opt/python/*/bin; do \
    "${PYBIN}/pip" install pynini --no-index -f /wheelhouse || exit; \
done

# ***************************
# *** Runs Pynini's tests ***
# ***************************
FROM install-pynini-from-wheel AS run-tests

# Copies Pynini's tests and testing assets.
COPY --from=wheel-building-env "/src/pynini-${PYNINI_VERSION}/tests" /tests

# Runs Pynini's tests for each of our Pythons.
RUN for PYBIN in /opt/python/*/bin; do \
    "${PYBIN}/pip" install absl-py || exit; \
    for TEST in tests/*_test.py; do \
        # This test requires external attributes, so we don't bother.
        if [[ "${TEST}" == "tests/chatspeak_model_test.py" ]]; then \
            continue; \
        fi; \
        "${PYBIN}/python" "${TEST}" || exit; \
    done \
done
