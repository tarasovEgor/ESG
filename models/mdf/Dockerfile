FROM python:3.10-slim

WORKDIR "/app"
ENV PYTHONPATH /app/
COPY requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
