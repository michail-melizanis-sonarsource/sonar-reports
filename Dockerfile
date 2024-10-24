FROM python:3.13-slim

RUN apt-get --assume-yes update && apt-get --assume-yes install bash

RUN mkdir /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY /src/ /app/
COPY /deployment/startup/extract.sh /app/extract.sh

WORKDIR /app
ENTRYPOINT ["python", "/app/main.py"]