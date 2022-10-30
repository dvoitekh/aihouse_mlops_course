FROM python:3.9-slim

ADD . /app

WORKDIR /app

RUN mkdir /katib
RUN pip install --no-cache-dir -r requirements.txt

RUN chgrp -R 0 /app \
  && chmod -R g+rwX /app \
  && chgrp -R 0 /katib \
  && chmod -R g+rwX /katib

ENTRYPOINT ["python3", "/app/main.py"]
