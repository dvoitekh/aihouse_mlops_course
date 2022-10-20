FROM python:3.9.5

USER root

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .
