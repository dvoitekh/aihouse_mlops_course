FROM python:3.9.6

ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /app
WORKDIR /app

RUN pip install .

CMD gunicorn --workers 1 --bind 0.0.0.0:5000 wsgi:app
