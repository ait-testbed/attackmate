From kalilinux/kali-rolling

LABEL maintainer="wolfgang.hotwagner@ait.ac.at"

ENV VIRTUAL_ENV=/opt/venv
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv nmap nikto ffuf
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ADD . /penpal
RUN pip install -e /penpal
WORKDIR /penpal

ENTRYPOINT ["/opt/venv/bin/penpal"]
