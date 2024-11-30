FROM python:3.13-slim

# Version
ENV FRONTEND_VERSION=1.0.1

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt


# Install application in work dir
#COPY assets ./assets
#COPY tabs ./tabs
#COPY app.py .
#COPY config.py .
#COPY member.py .

EXPOSE 8501
