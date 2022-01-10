# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10.1-alpine
WORKDIR /code

RUN apk --update --upgrade add --no-cache  gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev

RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 7007
COPY . .
CMD [ "python", "wsgi.py" ]