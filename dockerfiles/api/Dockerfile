FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app
RUN chmod -R 755 /app

COPY . /app
#COPY ../../plugins /app/plugins
#ENV PYTHONPATH="${PYTHONPATH}:/app/plugins"
RUN chmod -R 755 /app
