from datetime import datetime
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
import numpy as np
import json

# Import functions from meteo_functions
from weather_utils.model_functions import load_df


# Les chemins d'export local ont été supprimés car MLflow gère maintenant tout


# Function to prepare data
def prepare_data(df):
    if df is not None and not df.empty:
        X = df.drop(columns=["RainTomorrow", "ingestion_date"])
        y = df["RainTomorrow"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        return X_train, X_test, y_train, y_test
    else:
        raise ValueError("Le DataFrame est vide ou None")


def get_input_output_schema(df, target_column='RainTomorrow'):
    input_df = df.drop(columns=target_column)
    input_schema = input_df.dtypes.apply(lambda x: x.name).to_dict()
    output_schema = {target_column: df[target_column].dtype.name}
    return input_schema, output_schema

def train_model():
    """
    Train a Random Forest Classifier and track with MLflow
    Returns:
        bool: True if training successful and new model is better, False otherwise
    """
    try:
        # Load and prepare data
        try:
            df = load_df()
            input_schema, output_schema = get_input_output_schema(df)
            print("Input Schema:", input_schema)
            print("Output Schema:", output_schema)

            X_train, X_test, y_train, y_test = prepare_data(df)
        except Exception as e:
            raise Exception(f"Error in data preparation: {str(e)}")

        # Model parameters
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "random_state": 42,
        }

        # Train new model
        try:
            new_model = RandomForestClassifier(**params)
            new_model.fit(X_train, y_train)
        except Exception as e:
            raise Exception(f"Error in model training: {str(e)}")

        # Calculate metrics for new model
        try:
            new_predictions = new_model.predict(X_test)
            new_accuracy = accuracy_score(y_test, new_predictions)
            new_precision = precision_score(y_test, new_predictions, average='weighted')
            new_recall = recall_score(y_test, new_predictions, average='weighted')
            new_f1 = f1_score(y_test, new_predictions, average='weighted')
            
            new_metrics = {
                "accuracy": new_accuracy,
                "precision": new_precision,
                "recall": new_recall,
                "f1_score": new_f1
            }
            print("New model metrics:", new_metrics)
        except Exception as e:
            raise Exception(f"Error in metrics calculation: {str(e)}")

        # Get previous best model from MLflow
        try:
            client = mlflow.tracking.MlflowClient()
            registered_model = client.get_registered_model("RandomForestClassifier")
            latest_versions = client.get_latest_versions(
                "RandomForestClassifier", stages=["Production"]
            )

            if latest_versions:
                previous_model = mlflow.sklearn.load_model(
                    f"models:/RandomForestClassifier/Production"
                )
                previous_predictions = previous_model.predict(X_test)
                previous_f1 = f1_score(y_test, previous_predictions, average='weighted')

                # Compare models based on F1 score
                improvement_threshold = 0.01
                relative_improvement = (new_f1 - previous_f1) / previous_f1
                should_promote = relative_improvement > improvement_threshold
            else:
                should_promote = True
                relative_improvement = None
                previous_f1 = None

        except Exception as e:
            print(f"Warning: Could not evaluate previous model: {str(e)}")
            should_promote = True
            relative_improvement = None
            previous_f1 = None

        # MLflow tracking
        try:
            experiment = mlflow.set_experiment("Training Random Forest")
            run_name = f"rf_{datetime.utcnow()}"

            with mlflow.start_run(run_name=run_name) as run:
                # Log parameters and metrics
                mlflow.log_params(params)
                mlflow.log_metrics(new_metrics)

                # Log input and output schemas as artifacts
                with open("input_schema.json", "w") as f:
                    json.dump(input_schema, f)
                with open("output_schema.json", "w") as f:
                    json.dump(output_schema, f)
                mlflow.log_artifact("input_schema.json")
                mlflow.log_artifact("output_schema.json")

                if previous_f1 is not None:
                    mlflow.log_metrics(
                        {
                            "previous_f1": previous_f1,
                            "improvement": relative_improvement,
                        }
                    )

                # Log model
                mlflow.sklearn.log_model(
                    sk_model=new_model,
                    artifact_path="rf_training",
                    registered_model_name="RandomForestClassifier",
                )

                # Transition to production if better
                if should_promote:
                    client = mlflow.tracking.MlflowClient()
                    latest_version = client.get_latest_versions(
                        "RandomForestClassifier", stages=["None"]
                    )[0]
                    client.transition_model_version_stage(
                        name="RandomForestClassifier",
                        version=latest_version.version,
                        stage="Production",
                        archive_existing_versions=True,
                    )
                    print("New model promoted to production")
                else:
                    print(
                        "Keeping current production model - new model did not show significant improvement"
                    )

        except Exception as e:
            raise Exception(f"Error in MLflow logging: {str(e)}")

        return should_promote

    except Exception as e:
        print(f"Error in train_model: {str(e)}")
        if mlflow.active_run():
            mlflow.log_param("error", str(e))
            mlflow.end_run(status="FAILED")
        return False

    finally:
        if mlflow.active_run():
            mlflow.end_run()



def get_production_model():
    """
    Get the current production model from MLflow
    """
    try:
        return mlflow.sklearn.load_model(f"models:/RandomForestClassifier/Production")
    except Exception as e:
        print(f"Error loading production model: {str(e)}")
        return None


def get_latest_model():
    """
    Get the latest model from MLflow regardless of stage
    """
    try:
        client = mlflow.tracking.MlflowClient()
        latest_versions = client.get_latest_versions("RandomForestClassifier")
        if latest_versions:
            return mlflow.sklearn.load_model(
                f"runs:/{latest_versions[0].run_id}/rf_training"
            )
        return None
    except Exception as e:
        print(f"Error loading latest model: {str(e)}")
        return None

def get_best_model():
    """
    Get the best performing model from MLflow based on F1-score
    Returns:
        tuple: (best_model, metrics_dict) or (None, None) if no models found
    """
    try:
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name("Training Random Forest")

        if experiment is None:
            print("No experiment found")
            return None, None

        # Rechercher tous les runs et les trier par F1-score
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["metrics.f1_score DESC"],
            max_results=1000  # Augmenter pour être sûr d'avoir tous les runs
        )

        best_f1 = -1
        best_run = None

        # Parcourir tous les runs pour trouver celui avec le meilleur F1-score
        for run in runs:
            if 'f1_score' in run.data.metrics:
                current_f1 = run.data.metrics['f1_score']
                if current_f1 > best_f1:
                    best_f1 = current_f1
                    best_run = run

        if best_run is None:
            print("Aucun run trouvé avec un score F1")
            return None, None

        # Charger le modèle du meilleur run
        best_model = mlflow.sklearn.load_model(
            f"runs:/{best_run.info.run_id}/rf_training"
        )

        metrics_dict = {
            'accuracy': best_run.data.metrics.get("accuracy"),
            'precision': best_run.data.metrics.get("precision"),
            'recall': best_run.data.metrics.get("recall"),
            'f1_score': best_run.data.metrics.get("f1_score")
        }

        print(f"Meilleur modèle trouvé avec F1-score: {best_f1}")
        return best_model, metrics_dict

    except Exception as e:
        print(f"Error in export_best_model: {str(e)}")
        print("Detailed error info:")
        import traceback
        traceback.print_exc()
        return False

# Les fonctions d'export local ont été supprimées car MLflow gère déjà le versioning et les métadonnées

def check_mlflow_state():
    """
    Fonction de diagnostic pour vérifier l'état de MLflow
    """
    try:
        print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")

        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name("Training Random Forest")

        if experiment is None:
            print("No experiment found named 'Training Random Forest'")
            print("Available experiments:")
            for exp in client.search_experiments():
                print(f"- {exp.name}")
            return False

        print(f"Found experiment: {experiment.name} (ID: {experiment.experiment_id})")

        runs = client.search_runs([experiment.experiment_id])
        print(f"Number of runs found: {len(runs)}")

        for run in runs:
            print(f"\nRun ID: {run.info.run_id}")
            print(f"Status: {run.info.status}")
            print("Metrics:")
            for metric_name, metric_value in run.data.metrics.items():
                print(f"- {metric_name}: {metric_value}")

        return True

    except Exception as e:
        print(f"Error checking MLflow state: {str(e)}")
        print("Detailed error info:")
        import traceback
        traceback.print_exc()
        return False



import mlflow
from mlflow.tracking import MlflowClient
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime

def get_all_model_versions():
    try:
        client = MlflowClient()
        registered_models = client.search_registered_models()
        
        models_info = []
        for rm in registered_models:
            versions = client.get_latest_versions(rm.name)
            for version in versions:
                # Récupérer les métriques pour cette version
                run = client.get_run(version.run_id)
                metrics = run.data.metrics
                
                # Formater la date de création
                creation_timestamp = datetime.fromtimestamp(version.creation_timestamp / 1000.0)
                formatted_date = creation_timestamp.strftime("%d-%m-%Y %H:%M:%S")
                
                model_info = {
                    "name": rm.name,
                    "version": version.version,
                    "status": version.status,
                    "creation_date": formatted_date,
                    "metrics": {
                        "accuracy": metrics.get("accuracy", None),
                        "precision": metrics.get("precision", None),
                        "recall": metrics.get("recall", None),
                        "f1_score": metrics.get("f1_score", None),
                        "mae": metrics.get("mae", None),
                        "mse": metrics.get("mse", None),
                        "rmse": metrics.get("rmse", None)
                    }
                }
                models_info.append(model_info)
        
        return models_info
    except Exception as e:
        print(f"Erreur lors de la récupération des modèles : {str(e)}")
        return []


def load_specific_model_version(version):
    """
    Charge une version spécifique du modèle depuis MLflow
    Args:
        version (str): Numéro de version du modèle à charger
    Returns:
        model: Le modèle chargé ou None en cas d'erreur
    """
    try:
        model_name = "RandomForestClassifier"
        model = mlflow.sklearn.load_model(
            f"models:/{model_name}/{version}"
        )
        return model
    except Exception as e:
        print(f"Erreur lors du chargement du modèle version {version}: {str(e)}")
        return None