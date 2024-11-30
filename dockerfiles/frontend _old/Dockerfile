# Utilisation de l'image Python officielle
FROM python:3.9-slim

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie de l'application Streamlit dans le conteneur
COPY . /app
WORKDIR /app

# Installation des dépendances Python
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

# Exposition du port utilisé par Streamlit
EXPOSE 8501

