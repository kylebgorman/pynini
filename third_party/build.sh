#!/bin/bash
docker build --build-arg "TARGET_ARCH=`uname -m`" --target=run-tests -t build-pynini-wheels -f third_party/Dockerfile . 
