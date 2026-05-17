FROM ghcr.io/marimo-team/marimo:latest-sql

WORKDIR /app

# Copy dependency definition and install standard packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Create volume target folder
RUN mkdir -p /app/notebooks

# Expose default Marimo port
EXPOSE 2718

# Default run command pointing to notebooks folder
CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "2718", "notebooks/"]
