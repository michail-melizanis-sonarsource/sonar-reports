FROM python:3.11-slim

RUN apt-get --assume-yes update && apt-get --assume-yes install bash

RUN mkdir /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY report.sh /app/
RUN chmod +x /app/report.sh

COPY /src /app/

WORKDIR /app
ENTRYPOINT ["bash", "/app/report.sh"]