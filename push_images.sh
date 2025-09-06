#!/bin/bash

# Définir les variables nécessaires
VERSION='0.2'
DOCKERHUB_USERNAME='tristandatascience'  # À remplacer par votre nom d'utilisateur Docker Hub
DOCKERHUB_REPOSITORY='aussie_weather_flow'          # À remplacer par le nom de votre dépôt sur Docker Hub

# Se connecter à Docker Hub
docker login

# Liste des images à construire, retaguer et pousser
IMAGES=(
    mlops-meteo-airflow-base
    mlops-meteo-fastapi
    mlops-meteo-mlflow-webserver
    mlops-meteo-frontend
)

# Dictionnaire associant les images aux chemins de leurs Dockerfiles
declare -A IMAGE_PATHS=(
    ["mlops-meteo-airflow-base"]="./dockerfiles/airflow"
    ["mlops-meteo-fastapi"]="./dockerfiles/api"
    ["mlops-meteo-mlflow-webserver"]="./dockerfiles/mlflow"
    ["mlops-meteo-frontend"]="./dockerfiles/frontend"
)

# Boucle pour construire chaque image
for IMAGE in "${IMAGES[@]}"
do
    # Obtenir le chemin du Dockerfile pour cette image
    BUILD_PATH="${IMAGE_PATHS[$IMAGE]}"

    if [ -d "$BUILD_PATH" ]; then
        echo "Construction de l'image $IMAGE à partir de $BUILD_PATH..."
        # Construire l'image avec le nom local $IMAGE
        docker build -t "$IMAGE" "$BUILD_PATH"
        echo "Image $IMAGE construite avec succès."
    else
        echo "Chemin de construction $BUILD_PATH non trouvé pour l'image $IMAGE."
    fi
done

# Boucle pour retaguer et pousser chaque image
for IMAGE in "${IMAGES[@]}"
do
    # Récupérer l'ID de l'image locale
    IMAGE_ID=$(docker images "$IMAGE" --format "{{.ID}}" | head -n 1)

    if [ -n "$IMAGE_ID" ]; then
        # Nouveau nom avec le tag sous le même dépôt
        IMAGE_NAME="${IMAGE##mlops-meteo-}"  # Extrait le nom de l'image sans le préfixe "mlops-meteo-"
        NEW_IMAGE="$DOCKERHUB_USERNAME/$DOCKERHUB_REPOSITORY:${IMAGE_NAME}-$VERSION"

        # Retagger l'image
        docker tag "$IMAGE_ID" "$NEW_IMAGE"

        # Pousser l'image sur Docker Hub
        docker push "$NEW_IMAGE"

        echo "Image $IMAGE retaguée et poussée en tant que $NEW_IMAGE"
    else
        echo "Image $IMAGE non trouvée localement."
    fi
done