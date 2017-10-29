FROM python:3.6.1
ENV PYTHONUNBUFFERED 1

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' 9.6 > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
    apt-key add -

RUN apt-get update && apt-get install postgresql-9.6 -y && apt-get clean
RUN apt-get install postgresql-9.6-postgis-2.3 postgresql-contrib-9.6 postgresql-9.6-postgis-scripts python-psycopg2 libmemcached-dev zlib1g-dev -y && apt-get clean

ADD run_server.sh /run_server.sh
ADD run_celery.sh /run_celery.sh

RUN mkdir -p /var/www/dp_server/assets
WORKDIR /var/www

ADD py-requirements.txt .
RUN pip install -r py-requirements.txt

ADD usrlocalbin /usr/local/bin
ADD conf /conf
RUN chmod +x /usr/local/bin/migrate && chmod +x /usr/local/bin/createsuperuser
RUN mkdir /socks && chown www-data:www-data /socks

USER www-data

ADD *.py ./
ADD scrapers ./scrapers
ADD dp_server ./dp_server
