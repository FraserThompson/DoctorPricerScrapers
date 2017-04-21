FROM python:3.6.1
ENV PYTHONUNBUFFERED 1

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' 9.6 > /etc/apt/sources.list.d/pgdg.list && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
    apt-key add -

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - 

RUN apt-get install nodejs postgresql-9.6 postgresql-9.6-postgis postgresql-server-dev-9.6 python-psycopg2 -y

RUN mkdir /code
WORKDIR /code

ADD package.json .
RUN npm install

ADD py-requirements.txt .
RUN pip install -r py-requirements.txt

ADD scrapers ./scrapers
ADD scrapers_ui ./scrapers_ui
ADD assets ./assets
ADD *.py ./
ADD *.js ./

ADD usrlocalbin /usr/local/bin
RUN chmod +x /usr/local/bin/migrate && chmod +x /usr/local/bin/webpack-watch && chmod +x /usr/local/bin/createsuperuser

CMD /code/node_modules/.bin/webpack --config webpack.config.js && python manage.py runserver 0.0.0.0:8000