# Projet Prévision Météo en Australie - MLOps Juillet 2024 ☀️🌧️

Ce projet déploie un modèle **Random Forest** 🌲 dans une application de prévision de pluie à J+1 sur une ville donnée en Australie 🇦🇺. Le projet intègre des outils MLOps tels que **Airflow** 🏗️, **MLflow** 🚀 pour la pipeline data-model, **Prometheus** 📈 et **Grafana** 📊 pour le monitoring des ressources machines, ainsi que **FastAPI** ⚡ et **Streamlit** 🎨 pour l'inférence.

## Table des matières 📚

- [Description du projet](#description-du-projet-)
- [Architecture du projet](#architecture-du-projet-)
- [Les DAGs Airflow](#les-dags-airflow-)
- [Outils utilisés](#outils-utilisés-)
- [Installation et utilisation](#installation-et-utilisation-)
  - [Version de production](#version-de-production-)
  - [Version de développement](#version-de-développement-)
  - [Accès aux services](#accès-aux-services-)
- [CI/CD](#cicd-)
- [Monitoring](#monitoring-)
- [Licence](#licence-)
- [Équipe du projet](#équipe-du-projet-)

---

## Description du projet 📝

Le projet vise à prédire la probabilité de pluie le lendemain pour une ville spécifique en Australie. Il s'appuie sur un modèle **Random Forest** 🌲 entraîné sur des données météorologiques actualisées quotidiennement. Les principaux composants du projet sont :

- **Airflow** 🏗️ pour orchestrer les pipelines de données (ETL) et l'entraînement du modèle.
- **MLflow** 🚀 pour gérer les expériences de machine learning et suivre les performances des modèles.
- **FastAPI** ⚡ et **Streamlit** 🎨 pour fournir une interface utilisateur pour les prédictions et une interface administrateur pour gérer les mises à jour et les entraînements.
- **Prometheus** 📈 et **Grafana** 📊 pour le monitoring des ressources serveurs et la visualisation des métriques.
- Utilisation de **Docker** 🐳 pour la containerisation et de **Docker Hub** 🐳 pour le déploiement des images.
- **GitHub Actions** ⚙️ pour l'intégration continue et le déploiement continu (CI/CD).

---

## Architecture du projet 🏛️

![Architecture du Projet][] <!-- Assurez-vous d'inclure une image représentant l'architecture de votre projet -->

Le projet est entièrement containerisé, ce qui facilite le déploiement et la scalabilité. L'architecture se compose des éléments suivants :

- **Scraping des données** 🕸️ : Récupération quotidienne des relevés météorologiques via des scripts Python.
- **Pipeline ETL avec Airflow** 🏗️ : Extraction, transformation et chargement des données dans une base de données PostgreSQL.
- **Entraînement du modèle avec MLflow** 🚀 : Entraînement hebdomadaire du modèle Random Forest, comparaison avec le modèle précédent selon le F1-score, et déploiement du meilleur modèle.
- **API d'inférence avec FastAPI** ⚡ : Fournit des prédictions basées sur le modèle déployé.
- **Interface utilisateur avec Streamlit** 🎨 : Permet aux utilisateurs de faire des prédictions et aux administrateurs de lancer manuellement une récupération des données du jour et un entraînement avec sélection du meilleur modèle.
- **Monitoring avec Prometheus** 📈 et **Grafana** 📊 : Collecte et visualisation des métriques du système et des performances du modèle.
- **CI/CD avec GitHub Actions** ⚙️ : Tests automatisés et déploiement continu sur Docker Hub.

---

## Les DAGs Airflow 📅

- **DAG de collecte des données (quotidien)**
  - **Tâches** :
    - Scraping du site météorologique pour obtenir les relevés journaliers. 🌦️
    - Nettoyage et préparation des données. 🧹
    - Insertion des données dans la base de données PostgreSQL. 🗄️
- **DAG d'entraînement du modèle (hebdomadaire)**
  - **Tâches** :
    - Chargement des données depuis la base de données. 📥
    - Entraînement du modèle Random Forest avec MLflow. 🚀
    - Comparaison avec le modèle précédent en utilisant le F1-score. 📊
    - Enregistrement du meilleur modèle pour l'inférence. 💾
- **DAG combiné (exécution manuelle)**
  - **Tâches** :
    - Exécution des tâches de collecte des données. 🌐
    - Entraînement du modèle et sélection du meilleur. 🏆
  - **Utilisation** :
    - Peut être déclenché depuis le panneau administrateur de l'application Streamlit pour forcer une mise à jour du modèle.
- **DAG de tests unitaires**
  - **Tâches** :
    - Exécution de la suite de tests pour valider le bon fonctionnement des pipelines et du modèle. ✅

---

## Outils utilisés 🛠️

- **Langage** : Python 3.8+ 🐍
- **Outils MLOps** :
  - **Apache Airflow** 🏗️ : Orchestration des pipelines ETL et des entraînements.
  - **MLflow** 🚀 : Gestion des expériences de machine learning et suivi des modèles.
- **Développement Web** :
  - **FastAPI** ⚡ : Création de l'API d'inférence.
  - **Streamlit** 🎨 : Interface utilisateur pour les prédictions et les actions administratives.
- **Monitoring** :
  - **Prometheus** 📈 : Collecte des métriques système.
  - **Grafana** 📊 : Visualisation des métriques via des tableaux de bord.
- **Gestion des données** :
  - **PostgreSQL** 🗄️ : Base de données pour stocker les données préparées.
- **Containerisation et Déploiement** :
  - **Docker** 🐳 et **Docker Compose** 📦 : Containerisation des services.
  - **Docker Hub** 🐳 : Stockage et distribution des images Docker.
  - **GitHub Actions** ⚙️ : Intégration continue et déploiement continu (CI/CD).

---

## Installation et utilisation 🚀

### Pré-requis 📋

- **Docker** 🐳 et **Docker Compose** 📦 installés sur votre machine.
- **Make** installé pour utiliser les Makefiles.

### Version de production 🏭

1. **Initialiser Airflow** :

   ```bash
   make -f Makefile.prod init-airflow
   ```

2. **Démarrer les services** :

   ```bash
   make -f Makefile.prod start
   ```

### Version de développement 🧑‍💻

1. **Initialiser Airflow** :

   ```bash
   make -f Makefile.dev init-airflow
   ```

2. **Démarrer les services** :

   ```bash
   make -f Makefile.dev start
   ```

### Accès aux services 🌐

Après avoir démarré les services, vous pouvez accéder aux différentes interfaces via les ports suivants :

- **Airflow** 🏗️ : [http://localhost:8080](http://localhost:8080)
  - **Port** : `8080`
  - Interface Web pour superviser les DAGs et les tâches.
- **MLflow** 🚀 : [http://localhost:5000](http://localhost:5000)
  - **Port** : `5000`
  - Interface pour visualiser les expériences de machine learning et les paramètres des modèles.
- **FastAPI** ⚡ (API d'inférence) : [http://localhost:8000/docs](http://localhost:8000/docs)
  - **Port** : `8000`
  - Documentation interactive de l'API via Swagger UI.
- **Streamlit** 🎨 : [http://localhost:8501](http://localhost:8501)
  - **Port** : `8501`
  - Interface utilisateur pour effectuer des prédictions et accéder au panneau administrateur.

---

## Monitoring 📈

**Prometheus** 📈 collecte les métriques système, telles que l'utilisation du CPU, de la mémoire et des ressources réseau. **Grafana** 📊 est utilisé pour visualiser ces métriques à travers des tableaux de bord personnalisables.

- **Accéder à Grafana** :

  Rendez-vous sur [http://localhost:3000](http://localhost:3000) (port `3000`) et connectez-vous avec les identifiants par défaut (configurés dans le docker-compose).

- **Dashboards permettant de visualiser entre autres** :

  - Utilisation du CPU. 🖥️
  - Utilisation de la mémoire. 🧠
  - Utilisation du disque. 💾
  - Utilisation du réseau. 🌐
  - Performances des services Docker. 🐳

---

## CI/CD ⚙️

Le projet utilise **GitHub Actions** ⚙️ pour l'intégration continue et le déploiement continu :

- **Tests automatisés** 🧪 : À chaque push ou pull request, les tests unitaires sont exécutés pour s'assurer que le code est fonctionnel.
- **Build des images Docker** 🐳 : Les images Docker sont construites et testées.
- **Déploiement sur Docker Hub** 🐳 : Si les tests réussissent, les images sont poussées sur Docker Hub avec un nouveau tag de version.


---

## Licence 📄

Ce projet est sous licence MIT - voir le fichier [LICENSE](./LICENSE) pour plus de détails.

---

## Équipe du projet 👥

Ce projet a été développé par l'équipe suivante :

- **Shirley GERVOLINO** [![GitHub][]](https://github.com/Shirley687) / [![LinkedIn][]](https://www.linkedin.com/in/)
- **Tristan** [![GitHub][]](https://github.com/tristandatascience) / [![LinkedIn][]](https://www.linkedin.com/in/)
- **Prudence Amani** [![GitHub][]](https://github.com/) / [![LinkedIn][]](https://www.linkedin.com/in/)
- **Stéphane LOS** [![GitHub][]](https://github.com/hil-slos) / [![LinkedIn][]](https://fr.linkedin.com/in/losstephane/)

---

*Ce projet a été réalisé dans le cadre du programme MLOps de Juillet 2024.*

---

**Note** : Assurez-vous de remplacer les liens manquants ou incomplets vers les profils LinkedIn par les liens corrects.

---

# Liens utiles 🔗

- [Documentation du projet](Lien_vers_votre_documentation)
- [Docker Hub](https://hub.docker.com/u/votre_nom_utilisateur)
- [Issues](Lien_vers_votre_projet_GitHub/issues)

---

Les badges sont générés via [Shields.io](https://shields.io/) 
