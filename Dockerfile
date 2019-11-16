FROM python:3.8.0-buster
ENV PYTHONUNBUFFERED 1

# We need lsb-release so we can use the lsb_release command to determine the version
RUN apt-get update && apt-get install -y lsb-release && apt-get clean

# Adding keys for the postgresql repository so we can get postgresql
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
    apt-key add -

# Getting postresql and its dependencies
RUN apt-get update && apt-get install postgresql-10 -y && apt-get clean
RUN apt-get install postgresql-10-postgis-2.4 postgresql-contrib-10 postgresql-10-postgis-2.4-scripts python-psycopg2 libmemcached-dev zlib1g-dev -y && apt-get clean

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