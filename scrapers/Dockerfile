FROM python:3.10.5-alpine3.16

RUN apk --update add ca-certificates && update-ca-certificates

COPY py-requirements.txt .
RUN pip install --no-cache-dir -r py-requirements.txt

COPY run.sh . 

RUN chmod +x ./run.sh

ENTRYPOINT ["./run.sh"]