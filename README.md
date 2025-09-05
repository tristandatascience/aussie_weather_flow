# AussieWeatherFlow

**Pipeline automatisé de prévision météo (pluie à J+1) en Australie, avec déploiement et monitoring MLOps.**

---

## Table des matières

- [Description](#description)
- [Architecture du projet](#architecture-du-projet)
- [Flux Airflow (DAGs)](#flux-airflow-dags)
- [Technologies utilisées](#technologies-utilisées)
- [Installation & Utilisation](#installation--utilisation)
- [Accès aux services](#accès-aux-services)
- [CI/CD](#cicd)
- [Monitoring](#monitoring)
- [Licence](#licence)

---

## Description

Ce projet prédit la probabilité de pluie le lendemain pour une ville australienne, en automatisant tout le cycle de Machine Learning :
- **Collecte** et **ETL** des données météo.
- Entraînement et sélection automatique du meilleur modèle (Random Forest).
- Déploiement continu (API, dashboards, monitoring).
- **Portabilité** et reproductibilité garanties via Docker.

---

## Architecture du projet

![Schéma d'architecture AussieWeatherFlow](./doc/images/architecture_aussieweatherflow.png)

*(Ce schéma met en avant la chaîne complète : Scraping ➔ ETL/Airflow ➔ BDD PostgreSQL ➔ MLflow (Entraînement/Suivi modèles) ➔ Service d’inférence via API FastAPI ➔ Dashboard Streamlit ➔ Monitoring Prometheus/Grafana. À générer vous-même via draw.io/diagrams.net ou outils similaires.)*

---

## Flux Airflow (DAGs)

- **DAG Collecte quotidienne** : Scraping, nettoyage, insertion en BDD.
- **DAG Entraînement hebdomadaire** : Chargement depuis la base, entraînement Random Forest, comparaison au modèle précédent (F1-score), déploiement du meilleur modèle.
- **DAG unifié (manuel)** : Lancements combinés pour update “one-click” via Streamlit.
- **DAGs tests** : Validation du fonctionnement des pipelines et du modèle.

---

## Technologies utilisées

- **Python 3.8+**
- **Airflow** (orchestration, ETL, scheduling)
- **MLflow** (suivi, gestion des modèles)
- **FastAPI** (API d'inférence REST)
- **Streamlit** (interface utilisateur/admin)
- **PostgreSQL** (stockage des data préparées)
- **Prometheus & Grafana** (monitoring, dashboards)
- **Docker & Docker Compose** (containerisation)
- **GitHub Actions** (CI/CD, build, tests, déploiement continu)

---

## Installation & Utilisation

**Pré-requis**
- Docker / Docker Compose
- GNU Make

**Installation (mode production)**
```
make -f Makefile.prod init-airflow
make -f Makefile.prod start
```
**Installation (mode développement)**
```
make -f Makefile.dev init-airflow
make -f Makefile.dev start
```

---

## Accès aux services

| Service    | Port               | Usage                                                             |
|------------|--------------------|-------------------------------------------------------------------|
| Airflow    | localhost:8080     | Orchestration et supervision des pipelines                        |
| MLflow     | localhost:5000     | Visualisation, gestion des modèles ML                             |
| FastAPI    | localhost:8000/docs| Documentation interactive et test de l’API d’inférence            |
| Streamlit  | localhost:8501     | Interface utilisateur/prédiction et panneau admin                 |
| Grafana    | localhost:3000     | Dashboards de monitoring système et application                   |

---

## CI/CD

Le projet intègre un pipeline **GitHub Actions** qui :
- Exécute tous les tests unitaires à chaque push/PR,
- Construit puis pousse les images Docker sur Docker Hub si les tests sont validés.

---

## Monitoring

- **Prometheus** collecte toutes les métriques sur les services et la plateforme.
- **Grafana** permet de visualiser et d’alerter sur l’état du système et des performances modèles/services.
- Accès principal à Grafana via [http://localhost:3000](http://localhost:3000)

---

## Licence

Projet sous licence MIT (voir fichier LICENSE).

---

Projet réalisé par Tristan Lozahic.
