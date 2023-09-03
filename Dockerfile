# build: docker build -t attackmate .

From kalilinux/kali-rolling

LABEL maintainer="wolfgang.hotwagner@ait.ac.at"

ENV VIRTUAL_ENV=/opt/venv
ARG DEBIAN_FRONTEND=noninteractive
# Essentials
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv nmap nikto ffuf
# For Father rootkit
RUN apt-get update && apt-get install -y gcc libpam0g-dev libgcrypt20-dev nasm build-essential
# For Sliver-Workaround https://github.com/moloch--/sliver-py/issues/28
RUN apt-get update && apt install -y python3-dev libssl-dev git

RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ADD . /attackmate
RUN pip install /attackmate
WORKDIR /attackmate
# Sliver-Workaround
RUN git clone https://github.com/grpc/grpc \
    && cd grpc \
    && git submodule update --init \
    && pip install -r requirements.txt \
    && pip uninstall --yes protobuf \
    && pip uninstall --yes grpcio-tools \
    && pip install --no-input protobuf==3.20.* \
    && pip install --no-input grpcio-tools \
    && GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=True pip install --use-pep517 --no-input .

RUN cd /attackmate && rm -rf grpc

ENTRYPOINT ["/opt/venv/bin/attackmate"]
