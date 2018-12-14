FROM python:3.7.1-alpine3.8

COPY py-requirements.txt .
RUN pip install --no-cache-dir -r py-requirements.txt

COPY run.sh . 

RUN chmod +x ./run.sh

ENTRYPOINT ["./run.sh"]