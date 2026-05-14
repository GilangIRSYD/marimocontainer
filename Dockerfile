# syntax=docker/dockerfile:1.4

# Pilih versi Python yang sesuai
FROM python:3.11-slim

# Install uv untuk manajemen paket yang cepat
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Copy requirements
COPY --link requirements.txt .

# Install dependencies
RUN uv pip install -r requirements.txt

# Copy file aplikasi
COPY --link app.py .

EXPOSE 8080

# Buat non-root user
RUN useradd -m app_user
USER app_user

CMD [ "marimo", "run", "app.py", "--host", "0.0.0.0", "-p", "8080" ]
