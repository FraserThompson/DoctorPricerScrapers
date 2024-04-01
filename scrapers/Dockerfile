FROM python:3.10.5-bullseye

RUN  apt-get update && apt-get install ca-certificates chromium-driver chromium -y && apt-get clean && update-ca-certificates

COPY py-requirements.txt .
RUN pip install --no-cache-dir -r py-requirements.txt

COPY run.sh . 

RUN chmod +x ./run.sh

ENTRYPOINT ["./run.sh"]