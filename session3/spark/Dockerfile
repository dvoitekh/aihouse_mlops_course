FROM spark-py:v3.3.0

USER root

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .
