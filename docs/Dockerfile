# in your Dockerfile
FROM sphinxdoc/sphinx

WORKDIR /docs
ADD requirements.txt /docs
USER root
RUN pip3 install -r requirements.txt
