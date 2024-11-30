from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

# Import functions from meteo_functions
from weather_utils.model_functions import train_and_save_model
from weather_utils.csv_to_postgres import load_csv_to_postgres
from weather_utils.convert_to_one_csv import convert
from weather_utils.sql_to_df import load_sql_to_df

import joblib
from sklearn.metrics import mean_absolute_error, r2_score
import os
import datetime
import numpy as np

# Define paths
MODEL_PATH = "/opt/airflow/models/"
BEST_MODEL_PATH = os.path.join(MODEL_PATH, "best_model.joblib")
LAST_MODEL_PATH = os.path.join(MODEL_PATH, "last_model.joblib")


# Function to load data
def load_data():
  df = load_sql_to_df()
  return df

# Function to prepare data
def prepare_data(df):
  X = df.drop(columns='RainTomorrow')
  y = df['RainTomorrow']
  return train_test_split(X, y, test_size=0.2)


def train_model():
  """
  Train a Random Forest model and compare with previous version
  Returns:
      bool: True if training successful and new model is better, False otherwise
  """
  try:
      # Load and prepare data
      try:
          df = load_data()
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
          new_model = RandomForestRegressor(**params)
          new_model.fit(X_train, y_train)
      except Exception as e:
          raise Exception(f"Error in model training: {str(e)}")

      # Calculate metrics for new model
      try:
          new_predictions = new_model.predict(X_test)
          new_mse = mean_squared_error(y_test, new_predictions)
          new_rmse = np.sqrt(new_mse)
          new_r2 = r2_score(y_test, new_predictions)
          new_metrics = {"mse": new_mse, "rmse": new_rmse, "r2": new_r2}
          print("New model metrics:", new_metrics)
      except Exception as e:
          raise Exception(f"Error in metrics calculation: {str(e)}")

      # Load and evaluate previous best model if exists
      previous_metrics = None
      if os.path.exists(BEST_MODEL_PATH):
          try:
              previous_model = joblib.load(BEST_MODEL_PATH)
              previous_predictions = previous_model.predict(X_test)
              previous_mse = mean_squared_error(y_test, previous_predictions)
              previous_rmse = np.sqrt(previous_mse)
              previous_r2 = r2_score(y_test, previous_predictions)
              previous_metrics = {"mse": previous_mse, "rmse": previous_rmse, "r2": previous_r2}
              print("Previous best model metrics:", previous_metrics)
          except Exception as e:
              print(f"Warning: Could not evaluate previous model: {str(e)}")

      # Compare models
      should_update_best = True
      if previous_metrics:
          # Define improvement threshold (e.g., 1% better RMSE)
          improvement_threshold = 0.01
          relative_improvement = (previous_metrics['rmse'] - new_metrics['rmse']) / previous_metrics['rmse']
          
          should_update_best = relative_improvement > improvement_threshold
          comparison_results = {
              "relative_improvement": relative_improvement,
              "threshold_met": should_update_best
          }
          print(f"Model comparison results: {comparison_results}")

      # MLflow tracking
      try:
          experiment = mlflow.set_experiment("Training Random Forest")
          run_name = f"rf_{datetime.datetime.utcnow()}"
          artifact_path = "rf_training"

          with mlflow.start_run(run_name=run_name) as run:
              mlflow.log_params(params)
              mlflow.log_metrics(new_metrics)
              
              if previous_metrics:
                  mlflow.log_metrics({
                      "previous_rmse": previous_metrics['rmse'],
                      "improvement": relative_improvement
                  })
                  mlflow.log_param("model_updated", should_update_best)

              mlflow.sklearn.log_model(
                  sk_model=new_model,
                  input_example=X_test[:2],
                  artifact_path=artifact_path
              )
      except Exception as e:
          raise Exception(f"Error in MLflow logging: {str(e)}")

      # Save models
      try:
          os.makedirs(MODEL_PATH, exist_ok=True)
          
          # Always save as last_model
          joblib.dump(new_model, LAST_MODEL_PATH)
          print('New model saved as last_model.joblib')
          
          # Save as best_model only if it's better
          if should_update_best:
              joblib.dump(new_model, BEST_MODEL_PATH)
              print('New model saved as best_model.joblib - performance improvement confirmed')
          else:
              print('Keeping previous best_model.joblib - new model did not show significant improvement')
              
      except Exception as e:
          raise Exception(f"Error saving model: {str(e)}")

      return should_update_best

  except Exception as e:
      print(f"Error in train_model: {str(e)}")
      try:
          if mlflow.active_run():
              mlflow.log_param("error", str(e))
              mlflow.end_run(status="FAILED")
      except:
          pass
      return False

  finally:
      try:
          if mlflow.active_run():
              mlflow.end_run()
      except:
          pass