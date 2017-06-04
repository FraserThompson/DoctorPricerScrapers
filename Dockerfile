FROM python:3.6.1
ENV PYTHONUNBUFFERED 1

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' 9.6 > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
    apt-key add -

RUN apt-get update && apt-get install postgresql-9.6 postgresql-9.6-postgis postgresql-server-dev-9.6 python-psycopg2 libmemcached-dev zlib1g-dev -y

RUN mkdir /code
WORKDIR /code

ADD py-requirements.txt .
RUN pip install -r py-requirements.txt

ADD *.py ./
ADD scrapers ./scrapers
ADD dp_server ./dp_server

ADD usrlocalbin /usr/local/bin
RUN chmod +x /usr/local/bin/migrate && chmod +x /usr/local/bin/createsuperuser

CMD python manage.py runserver 0.0.0.0:8000