FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry==1.8.5

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only=main --no-root

COPY . .
RUN poetry install --only=main

EXPOSE 8000
CMD ["gunicorn", "medibot.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
