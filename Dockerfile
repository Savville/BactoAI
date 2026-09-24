FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements-ml.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data



# Expose port
EXPOSE 8080

# Run with gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
