# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8
ADD . /code
WORKDIR /code

RUN pip3 install -r requirements.txt

CMD python wsgi.py
