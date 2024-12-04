# meteo_functions/model_functions.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
import joblib
from airflow.exceptions import AirflowException
import pickle

# Define paths
MODEL_PATH = './models/model_rf.joblib'  # Changed model name to reflect RandomForest
TEMP_PATH = './temp/'
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

#def load_df():
#    """Loads the DataFrame from a pickle file."""
#    try:
#        file_path = os.path.join(TEMP_PATH, 'df.pkl')
#        if not os.path.exists(file_path):
#            raise FileNotFoundError(f"The file {file_path} does not exist.")
#        df = pd.read_pickle(file_path)
#        return df
#    except (FileNotFoundError, pd.errors.PickleError) as e:
#        raise AirflowException(f"Error loading DataFrame: {e}")


def load_df():
    """Loads the DataFrame from a pickle file using the pickle module."""
    try:
        file_path = os.path.join(TEMP_PATH, 'df.pkl')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'rb') as f:
            df = pickle.load(f)
        
        return df
    except (FileNotFoundError, pickle.PickleError) as e:
        raise AirflowException(f"Error loading DataFrame: {e}")



def save_model(trained_model, model_path=MODEL_PATH):  # Added model_path argument
    """Saves the trained model to a file."""
    try:
        joblib.dump(trained_model, model_path)  # Use model_path argument
        print(f'Model saved successfully to {model_path}')
    except (OSError, TypeError) as e:
        raise AirflowException(f"Error saving model: {e}")


def training_model(df):
    """Trains a RandomForest model and performs GridSearchCV."""
    try:
        df.drop(columns=['MinTemp', 'Temp9am'], inplace=True)
        X = df.drop('RainTomorrow', axis=1)
        y = df['RainTomorrow']
        print('dim', X.shape)
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

        # Initial model training (for baseline comparison)
        model_rf = RandomForestClassifier(criterion='entropy', n_estimators=40)
        model_rf.fit(X_train, y_train)
        y_pred = model_rf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f'Initial Model Accuracy: {accuracy:.4f}')
        print(classification_report(y_test, y_pred))


        param_grid = {'n_estimators': [1, 5, 9, 13, 15, 19, 22]}  # Example parameter grid
        grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
        grid_search.fit(X_train, y_train)

        print("Best Hyperparameters:", grid_search.best_params_)
        print("Best GridSearchCV Score:", grid_search.best_score_)

        best_rf = RandomForestClassifier(**grid_search.best_params_)
        best_rf.fit(X_train, y_train)
        return best_rf

    except Exception as e:
        raise AirflowException(f"An error occurred during training: {e}")

def predict_with_model(model, data):
    try:
        features = data.drop(columns='RainTomorrow') if 'RainTomorrow' in data.columns else data
        features = features.drop(columns=['ingestion_date'])
        
        if features.empty:
            raise ValueError("Input data is empty")
            
        predictions = model.predict(features)
        return list(predictions)
        
    except (ValueError, KeyError) as e:
        raise ValueError(f"Data validation error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Prediction error: {str(e)}")

def train_and_save_model():
    """Trains and saves the model."""
    df = load_df()
    best_rf = training_model(df)
    save_model(best_rf)