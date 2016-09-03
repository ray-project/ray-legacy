# Base image for tests. This differs from the deploy image in that
# rather than downloading source code from github it instead adds
# it from a tar file creaetd by test/travis-ci/install.sh

FROM ubuntu:xenial
RUN apt-get update
RUN apt-get -y install apt-utils
RUN apt-get -y install sudo
RUN apt-get install -y git cmake build-essential autoconf curl libtool python-dev python-numpy python-pip libboost-all-dev unzip graphviz
RUN pip install ipython funcsigs subprocess32 protobuf colorama graphviz cloudpickle
ADD ray.tar /home/root/ray
WORKDIR /home/root/ray
RUN ./setup.sh
RUN ./build.sh
WORKDIR /home/root/ray/lib/python
RUN python setup.py develop --user
WORKDIR /home/root/ray
