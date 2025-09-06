#!/usr/bin/env python3
"""
Script Python pour générer docker-compose.prod.yml à partir de docker-compose.dev.yml
Remplace les sections 'build' par des 'image'指向 Docker Hub
"""

import os
import re
import shutil
from pathlib import Path

# Configuration
DOCKERHUB_USERNAME = 'tristandatascience'
DOCKERHUB_REPOSITORY = 'aussie_weather_flow'
VERSION = '0.2'
SOURCE_FILE = 'docker-compose.dev.yml'
OUTPUT_FILE = 'docker-compose.prod.yml'

# Services à modifier
SERVICES_TO_MODIFY = {
    'x-airflow-common': {
        'image': f'{DOCKERHUB_USERNAME}/{DOCKERHUB_REPOSITORY}:airflow-base-{VERSION}'
    },
    'mlflow-webserver': {
        'image': f'{DOCKERHUB_USERNAME}/{DOCKERHUB_REPOSITORY}:mlflow-webserver-{VERSION}'
    },
    'fastapi': {
        'image': f'{DOCKERHUB_USERNAME}/{DOCKERHUB_REPOSITORY}:fastapi-{VERSION}'
    },
    'frontend': {
        'image': f'{DOCKERHUB_USERNAME}/{DOCKERHUB_REPOSITORY}:frontend-{VERSION}'
    }
}

def read_file(filepath):
    """Lire le contenu d'un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erreur: Le fichier {filepath} n'existe pas")
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {filepath}: {e}")
        return None

def write_file(filepath, content):
    """Écrire du contenu dans un fichier"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier {filepath}: {e}")
        return False

def remove_build_section(content, service_name, image_name):
    """
    Supprimer la section 'build' et ajouter la section 'image'
    pour un service donné en utilisant des expressions régulières
    """
    # Pattern pour trouver la section du service (plus robuste)
    if service_name == 'x-airflow-common':
        # Pour les sections avec alias, chercher dans les services
        service_pattern = r'(x-airflow-common:.*?&airflow-common\s+)(.*?)(?=\n\s+[a-zA-Z]|\nversion:|\nvolumes:|\nservices:)'
        def replace_build(match):
            prefix, service_content = match.groups()
            # Supprimer la section build
            service_content = re.sub(r'(\s+build:.*?\n)(?=\s+[a-zA-Z]|\s+\w+:)', '', service_content, flags=re.DOTALL)
            # Ajouter l'image si elle n'existe pas
            if 'image:' not in service_content:
                service_content = service_content.rstrip() + f'\n    image: {image_name}\n'
            return prefix + service_content
    else:
        # Pour les services normaux
        service_pattern = rf'({service_name}:.*?)(?=\n\s{service_name}:|\n\s[a-zA-Z]|\nversion:|\nvolumes:|\nservices:)'
        def replace_build(match):
            service_content = match.group(1)
            # Supprimer la section build
            service_content = re.sub(r'(\s+build:.*?\n)(?=\s+[a-zA-Z]|\s+\w+:)', '', service_content, flags=re.DOTALL)
            # Ajouter l'image si elle n'existe pas
            if 'image:' not in service_content:
                service_content = service_content.rstrip() + f'\n    image: {image_name}\n'
            return service_content
    
    # Appliquer la modification
    modified_content = re.sub(service_pattern, replace_build, content, flags=re.DOTALL)
    
    return modified_content

def generate_prod_compose():
    """Générer le fichier docker-compose.prod.yml"""
    
    print("=== Génération de docker-compose.prod.yml ===")
    
    # Vérifier si le fichier source existe
    if not os.path.exists(SOURCE_FILE):
        print(f"Erreur: Le fichier source {SOURCE_FILE} n'existe pas")
        return False
    
    # Lire le fichier source
    content = read_file(SOURCE_FILE)
    if content is None:
        return False
    
    print(f"Fichier source {SOURCE_FILE} lu avec succès")
    
    # Modifier chaque service
    for service_name, config in SERVICES_TO_MODIFY.items():
        print(f"Modification du service: {service_name}")
        old_content = content
        content = remove_build_section(content, service_name, config['image'])
        
        if content == old_content:
            print(f"  - Avertissement: Le service {service_name} n'a pas été trouvé ou modifié")
        else:
            print(f"  - Service {service_name} modifié avec succès")
    
    # Écrire le fichier de sortie
    if write_file(OUTPUT_FILE, content):
        print(f"Fichier {OUTPUT_FILE} généré avec succès")
        return True
    else:
        return False

def main():
    """Fonction principale"""
    print("Script de génération du docker-compose pour la production")
    print(f"Utilisateur Docker Hub: {DOCKERHUB_USERNAME}")
    print(f"Référence: {DOCKERHUB_REPOSITORY}")
    print(f"Version: {VERSION}")
    print()
    
    # Générer le fichier
    if generate_prod_compose():
        print("\n✅ Génération terminée avec succès!")
        print(f"Le fichier {OUTPUT_FILE} est prêt pour être utilisé en production.")
    else:
        print("\n❌ Échec de la génération")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())