FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY spotify2apple ./spotify2apple

RUN uv pip install --system -r spotify2apple/requirements.txt

COPY static ./static