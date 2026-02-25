FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y build-essential libssl-dev libffi-dev libmariadb-dev

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

RUN ls -alh /app

EXPOSE 8000