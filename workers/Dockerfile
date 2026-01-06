FROM python:3.11-slim

WORKDIR /worker

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/worker

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--pool=solo"]
