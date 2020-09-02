FROM alpine
ARG DEPLOY_ENV

RUN apk --update-cache add \
    python3 \
    python3-dev \
    py3-pip \
    gcc \
    g++ \
    curl \
    bash

RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

RUN apk update  \
    && apk upgrade  \
    && gcloud components install kubectl

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

RUN apk --no-cache add tzdata && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    apk del tzdata

RUN mkdir -p /src

COPY ./transfer-gcs-objects.py /src/transfer-gcs-objects.py
COPY ./config.ini /src/config.ini
COPY ./${DEPLOY_ENV}_gcs_buckets.json /src/${DEPLOY_ENV}_gcs_buckets.json

WORKDIR /src
