#!/bin/bash

# Nom du fichier docker-compose à modifier
COMPOSE_FILE="docker-compose.prod.yml"

# Nom d'utilisateur Docker Hub
DOCKERHUB_USERNAME="tristandatascience"
# Nom du dépôt Docker Hub
DOCKERHUB_REPOSITORY="mlops-meteo"

# Nouvelle version pour les images
VERSION="0.1"

# Liste des services et des images correspondantes
declare -A SERVICES_IMAGES=(
    ["airflow-init"]="airflow-init"
    ["airflow-scheduler"]="airflow-scheduler"
    ["airflow-triggerer"]="airflow-triggerer"
    ["airflow-webserver"]="airflow-webserver"
    ["airflow-worker"]="airflow-worker"
    ["fastapi"]="fastapi"
    ["mlflow-webserver"]="mlflow-webserver"
    ["frontend"]="frontend"
)

# Parcourir chaque service et mettre à jour l'image correspondante
for SERVICE in "${!SERVICES_IMAGES[@]}"; do
    IMAGE_NAME="${SERVICES_IMAGES[$SERVICE]}"
    FULL_IMAGE="${DOCKERHUB_USERNAME}/${DOCKERHUB_REPOSITORY}:${IMAGE_NAME}-${VERSION}"

    # Utiliser sed pour remplacer l'image dans le fichier docker-compose
    # On échappe les caractères spéciaux nécessaires pour sed
    ESCAPED_IMAGE=$(echo $FULL_IMAGE | sed 's/\//\\\//g')

    # Construire l'expression régulière pour identifier la ligne à remplacer
    # Elle cherche la ligne commençant par "image: " suivie de l'ancien nom d'image
    sed -i '' -E "/^\s*${SERVICE}:/,/^.*image:.*$/s|(^\s*image:\s*).*|\1${ESCAPED_IMAGE}|" $COMPOSE_FILE

    echo "Mise à jour de l'image pour le service ${SERVICE} : ${FULL_IMAGE}"
done

echo "Mise à jour des versions terminée dans ${COMPOSE_FILE}."