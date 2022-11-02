FROM python:3.9.5

ADD ./requirements.txt /tmp/requirements.txt

RUN pip install setuptools==41.2.0 pip==21.0.1 && \
    pip install -r /tmp/requirements.txt

ENV AWS_ACCESS_KEY_ID minioadmin
ENV AWS_SECRET_ACCESS_KEY minioadmin
ENV FEAST_S3_ENDPOINT_URL http://helm-minio.default.svc:9000

ADD . /app
WORKDIR /app
