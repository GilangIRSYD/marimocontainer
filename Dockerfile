FROM ghcr.io/marimo-team/marimo:latest-data

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
