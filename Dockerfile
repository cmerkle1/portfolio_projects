FROM python:3.11-slim

ENV PYTHONWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y netcat-openbsd
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-db.sh /app/
RUN chmod +x /app/wait-for-db.sh

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]