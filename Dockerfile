FROM python:3.10.5-bullseye
ENV PYTHONUNBUFFERED 1

# Getting postresql and its dependencies
RUN apt-get update && apt-get install postgresql -y && apt-get clean
RUN apt-get install postgresql-13-postgis-3 postgresql-contrib-13 postgresql-13-postgis-3-scripts python3-psycopg2 libmemcached-dev zlib1g-dev chromium-driver chromium -y && apt-get clean

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