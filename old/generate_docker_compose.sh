#!/bin/bash

# Définir les variables
DOCKERHUB_USERNAME='tristandatascience'  # À remplacer par votre nom d'utilisateur Docker Hub
DOCKERHUB_REPOSITORY='mlops-meteo'          # À remplacer par le nom de votre dépôt
VERSION='0.1'                               # À remplacer par la version souhaitée

# Exporter les variables pour qu'elles soient disponibles pour envsubst
export DOCKERHUB_USERNAME
export DOCKERHUB_REPOSITORY
export VERSION
echo $DOCKERHUB_USERNAME
echo $DOCKERHUB_REPOSITORY
echo $VERSION
# Générer le fichier docker-compose.prod.yml
envsubst < docker-compose.prod.yml.template > docker-compose.prod.yml

echo "Le fichier docker-compose.prod.yml a été généré avec succès."