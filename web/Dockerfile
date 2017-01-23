FROM python:3.5

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
COPY requirements.txt /
RUN pip3 install -r /requirements.txt

RUN mkdir /web
WORKDIR /web

# for production server, uncomment these lines and remove the dev section from docker-compose file
#COPY . /web/
#CMD gunicorn common.wsgi:application -w 2 -b :8000


