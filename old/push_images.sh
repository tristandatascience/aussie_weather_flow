#!/bin/bash

# Demander le nom d'utilisateur Docker Hub
read -p "Entrez votre nom d'utilisateur Docker Hub : " DOCKERHUB_USERNAME

# Demander le nom du dépôt Docker Hub
read -p "Entrez le nom du dépôt Docker Hub (par exemple, mlops-meteo) : " DOCKERHUB_REPOSITORY

# Version pour le tag
VERSION='0.1'

# Se connecter à Docker Hub
docker login

# Liste des images à retaguer et pousser
IMAGES=(
    mlops-meteo-airflow-init
    mlops-meteo-airflow-scheduler
    mlops-meteo-airflow-triggerer
    mlops-meteo-airflow-webserver
    mlops-meteo-airflow-worker
    mlops-meteo-fastapi
    mlops-meteo-mlflow-webserver
    mlops-meteo-frontend
)

# Boucle pour retaguer et pousser chaque image
for IMAGE in "${IMAGES[@]}"
do
    # Récupérer l'ID de l'image locale
    IMAGE_ID=$(docker images "$IMAGE" --format "{{.ID}}" | head -n 1)

    if [ -n "$IMAGE_ID" ]; then
        # Nouveau nom avec le tag sous le même dépôt
        NEW_IMAGE="$DOCKERHUB_USERNAME/$DOCKERHUB_REPOSITORY:${IMAGE##mlops-meteo-}-$VERSION"

        # Retagger l'image
        docker tag "$IMAGE_ID" "$NEW_IMAGE"

        # Pousser l'image sur Docker Hub
        docker push "$NEW_IMAGE"

        echo "Image $IMAGE retaguée et poussée en tant que $NEW_IMAGE"
    else
        echo "Image $IMAGE non trouvée localement."
    fi
done