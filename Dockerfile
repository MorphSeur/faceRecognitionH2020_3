# syntax=docker/dockerfile:1

FROM python:3.7-slim-buster
LABEL maintainer="koussaila.moulouel@u-pe.fr"

COPY * /app/

WORKDIR /app/

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1

RUN apt-get clean

RUN apt-get update
RUN apt-get install -y build-essential cmake
RUN apt-get install -y libgtk-3-dev
RUN apt-get install -y libboost-all-dev

RUN apt-get update
RUN apt-get install -qqy x11-apps
ENV DISPLAY :1
CMD xeyes

RUN apt-get -y install xauth

# Default port
EXPOSE 5000

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN apt-get update

CMD [ "sh", "/app/docker-entrypoint.sh"  ]