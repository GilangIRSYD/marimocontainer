FROM ghcr.io/marimo-team/marimo:latest-sql

# Switch to root to ensure full installation permissions
USER root

WORKDIR /app

# Install system build dependencies (essential for Postgres driver and any compilation fallbacks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel to ensure compatibility with modern precompiled wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy dependency definition and install standard packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Create volume target folder
RUN mkdir -p /app/notebooks

# Expose default Marimo port
EXPOSE 2718

# Default run command pointing to notebooks folder
CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "2718", "notebooks/"]
