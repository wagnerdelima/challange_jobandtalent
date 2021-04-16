FROM python:3.9.4-slim-buster
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/

RUN pip install -r requirements.txt

ADD . /code/

EXPOSE 80 80/tcp