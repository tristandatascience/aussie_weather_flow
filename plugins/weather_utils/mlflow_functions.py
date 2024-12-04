from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os
import datetime
import numpy as np
import json

# Import functions from meteo_functions
from weather_utils.model_functions import train_and_save_model
from weather_utils.csv_to_postgres import load_csv_to_postgres
from weather_utils.convert_to_one_csv import convert
from weather_utils.sql_to_df import load_sql_to_df
from weather_utils.model_functions import load_df


# Define paths
MODEL_PATH = "/opt/airflow/models/"
BEST_MODEL_PATH = os.path.join(MODEL_PATH, "best_model.joblib")


# Function to prepare data
def prepare_data(df):
    if df is not None and not df.empty:
        X = df.drop(columns="RainTomorrow")
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
            run_name = f"rf_{datetime.datetime.utcnow()}"

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

        # Search for all runs
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id], 
            order_by=["metrics.f1_score DESC"]  # Changed to f1_score and DESC
        )

        # Filter runs that have all required metrics
        required_metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        valid_runs = [run for run in runs if all(metric in run.data.metrics for metric in required_metrics)]

        if not valid_runs:
            print("No runs found with all required metrics")
            return None, None

        # Get the run with the highest F1-score
        best_run = valid_runs[0]
        metrics_dict = {
            'accuracy': best_run.data.metrics["accuracy"],
            'precision': best_run.data.metrics["precision"],
            'recall': best_run.data.metrics["recall"],
            'f1_score': best_run.data.metrics["f1_score"]
        }

        # Load the model from the best run
        best_model = mlflow.sklearn.load_model(
            f"runs:/{best_run.info.run_id}/rf_training"
        )

        print(f"Best model found with metrics:")
        for metric, value in metrics_dict.items():
            print(f"{metric}: {value}")
        
        return best_model, metrics_dict

    except Exception as e:
        print(f"Error getting best model: {str(e)}")
        print("Detailed error info:")
        import traceback
        traceback.print_exc()
        return None, None

def export_best_model():
    """Export best model to a shared volume"""
    try:
        print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")

        best_model, metrics_dict = get_best_model()
        if best_model is not None:
            # Créer le dossier models s'il n'existe pas
            os.makedirs("/opt/airflow/models", exist_ok=True)

            # Sauvegarder le modèle
            model_path = "/opt/airflow/models/best_model.joblib"
            joblib.dump(best_model, model_path)

            # Sauvegarder les métadonnées
            metadata = {
                **metrics_dict,  # Include all metrics
                'export_date': datetime.datetime.now().isoformat(),
                'model_type': 'RandomForestClassifier',
            }

            metadata_path = "/opt/airflow/models/best_model_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f)

            print(f"Model exported successfully to {model_path}")
            print(f"Metadata saved to {metadata_path}")
            return True

    except Exception as e:
        print(f"Error in export_best_model: {str(e)}")
        print("Detailed error info:")
        import traceback
        traceback.print_exc()
        return False


def export_last_model():
    """Export best model to a shared volume"""
    try:
        print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")

        last_model = get_latest_model()
        if last_model is not None:
            # Créer le dossier models s'il n'existe pas
            os.makedirs("/opt/airflow/models", exist_ok=True)

            # Sauvegarder le modèle
            model_path = "/opt/airflow/models/best_model.joblib"
            joblib.dump(last_model, model_path)

            # Sauvegarder les métadonnées
            metadata = {
                'export_date': datetime.datetime.now().isoformat(),
                'model_type': 'RandomForestClassifier',
            }

            metadata_path = "/opt/airflow/models/best_model_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f)

            print(f"Model exported successfully to {model_path}")
            print(f"Metadata saved to {metadata_path}")
            return True

    except Exception as e:
        print(f"Error in export_last_model: {str(e)}")
        print("Detailed error info:")
        import traceback
        traceback.print_exc()
        return False

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