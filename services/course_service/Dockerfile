FROM python:3.11-slim

WORKDIR /app

# Убедиться, что /app доступен для записи
RUN chmod 777 /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY entrypoint.sh .

# Сделать entrypoint исполняемым
RUN chmod +x entrypoint.sh

EXPOSE 5002

ENTRYPOINT ["./entrypoint.sh"]

