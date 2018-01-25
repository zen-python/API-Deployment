FROM alpine:latest
MAINTAINER Javier Torres Heredia <jtorres@minsegpres.gob.cl>

ENV LANG en_US.utf8

RUN apk add --no-cache --update build-base linux-headers python3 python3-dev rsync sudo && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    rm -rf /var/cache/apk/*

ADD requirements.txt /opt/app/
WORKDIR /opt/app
RUN pip3 install --no-cache-dir -r requirements.txt
RUN deluser xfs
RUN set -x ; \
  addgroup -g 33 -S www-data ; \
  adduser -u 33 -D -S -G www-data www-data && exit 0 ; exit 1
RUN adduser -D default

