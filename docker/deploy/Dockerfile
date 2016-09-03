# The deploy Docker image build a self-contained Ray instance suitable
# for end users.

FROM ubuntu:xenial
RUN apt-get update
RUN apt-get -y install apt-utils
RUN apt-get -y install sudo
RUN apt-get install -y git cmake build-essential autoconf curl libtool python-dev python-numpy python-pip libboost-all-dev unzip graphviz
RUN pip install ipython funcsigs subprocess32 protobuf colorama graphviz cloudpickle
WORKDIR /home/root
RUN git clone https://github.com/amplab/ray
WORKDIR /home/root/ray
RUN ./setup.sh
RUN ./build.sh
WORKDIR /home/root/ray/lib/python
RUN python setup.py develop --user
WORKDIR /home/root/ray
ENTRYPOINT bash
