#!/bin/bash

# Définir les variables
DOCKERHUB_USERNAME='tristandatascience'
DOCKERHUB_REPOSITORY='mlops-meteo'
VERSION='0.4'

# Installation de yq
if ! command -v yq &> /dev/null; then
    echo "Installation de yq..."
    # Pour Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq && chmod +x /usr/bin/yq
    # Pour MacOS
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install yq
    else
        echo "Système d'exploitation non supporté pour l'installation automatique de yq"
        exit 1
    fi
fi

# Copier le template vers docker-compose.yml
cp docker-compose.dev.yml.template docker-compose.prod.yml

# Remplacer le build par l'image pour x-airflow-common
yq eval -i '
  .x-airflow-common |= (
    del(.build) |
    .image = "'"$DOCKERHUB_USERNAME"'/'"$DOCKERHUB_REPOSITORY"':airflow-base-'"$VERSION"'"
  )
' docker-compose.prod.yml

# Remplacer le build par l'image pour mlflow-webserver
yq eval -i '
  .services.mlflow-webserver |= (
    del(.build) |
    .image = "'"$DOCKERHUB_USERNAME"'/'"$DOCKERHUB_REPOSITORY"':mlflow-webserver-'"$VERSION"'"
  )
' docker-compose.prod.yml

# Remplacer le build par l'image pour fastapi
yq eval -i '
  .services.fastapi |= (
    del(.build) |
    .image = "'"$DOCKERHUB_USERNAME"'/'"$DOCKERHUB_REPOSITORY"':fastapi-'"$VERSION"'"
  )
' docker-compose.prod.yml

# Remplacer le build par l'image pour frontend
yq eval -i '
  .services.frontend |= (
    del(.build) |
    .image = "'"$DOCKERHUB_USERNAME"'/'"$DOCKERHUB_REPOSITORY"':frontend-'"$VERSION"'"
  )
' docker-compose.prod.yml

echo "Le fichier docker-compose.prod.yml a été généré avec succès en remplaçant les builds par les images Docker Hub."