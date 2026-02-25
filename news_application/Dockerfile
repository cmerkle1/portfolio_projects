FROM python:3.11-slim

ENV PYTHONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /app

# We still need these to build the mysqlclient driver
RUN apt-get update && apt-get install -y \
    pkg-config \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000