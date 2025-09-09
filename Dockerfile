FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gettext \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip "poetry==2.1.3" \
    && poetry config virtualenvs.create false --local

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-ansi

COPY . .

RUN python manage.py collectstatic --noinput --skip-checks