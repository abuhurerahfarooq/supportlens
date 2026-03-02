FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY run.py ./run.py

EXPOSE 5000

CMD ["sh", "-c", "python -m app.bootstrap && exec gunicorn --workers 2 --bind 0.0.0.0:5000 run:app"]
