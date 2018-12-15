FROM python:3.6.1
ENV PYTHONUNBUFFERED 1

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' 9.6 > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
    apt-key add -

RUN apt-get update && apt-get install postgresql-9.6 -y && apt-get clean
RUN apt-get install postgresql-9.6-postgis-2.3 postgresql-contrib-9.6 postgresql-9.6-postgis-2.3-scripts python-psycopg2=2.5.4+dfsg-1 libmemcached-dev zlib1g-dev -y && apt-get clean

COPY ["run_server.sh", "/run_server.sh"]
COPY ["run_celery.sh", "/run_celery.sh"]
COPY ["usrlocalbin", "/usr/local/bin"]

RUN chmod +x /usr/local/bin/migrate && \
    chmod +x /usr/local/bin/createsuperuser && \
    chmod +x /run_server.sh && \
    chmod +x /run_celery.sh

WORKDIR /var/www

COPY ["py-requirements.txt", "."]
RUN pip install -r py-requirements.txt

COPY ["conf", "/conf"]

RUN mkdir /run/django && chown www-data:www-data /run/django

COPY ["*.py", "./"]
COPY ["scrapers", "./scrapers"]
COPY ["dp_server", "./dp_server"]

RUN  groupadd varwwwusers && \
    adduser www-data varwwwusers && \
    chown -R www-data:varwwwusers /var/www/ && \
    chmod -R 760 /var/www/ && \
    mkdir -p /var/www/dp_server/assets && \
    mkdir -p /var/www/dp_server/migrations && \
    chown www-data:www-data /var/www/dp_server/assets && \
    chown www-data:www-data /var/www/dp_server/migrations

USER www-data

VOLUME ["/run/django"]