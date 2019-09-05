FROM balenalib/raspberrypi3-alpine

RUN mkdir -p /var/socks

RUN apk add git python3 build-base

RUN apk add openblas-dev gfortran py3-scipy py3-numpy py3-crypto py3-zmq

#RUN apk add hidapi
RUN apk add hidapi --update-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/

RUN cd /usr/bin \
  && ln -sf pip3 pip \
  && { [ -e easy_install ] || ln -s easy_install-* easy_install; } \
  && ln -sf idle3 idle \
  && ln -sf pydoc3 pydoc \
  && ln -sf python3 python \
  && ln -sf python3-config python-config

WORKDIR /app

COPY src src
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/usr/bin/python3"]
