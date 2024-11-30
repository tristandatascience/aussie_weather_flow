# meteo_functions/model_functions.py

import numpy as np 
import pandas as pd 
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
import os
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, cohen_kappa_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import OneHotEncoder
from imblearn.ensemble import BalancedRandomForestClassifier
import joblib

# Chemin vers le modèle (ajustez le chemin si nécessaire)
MODEL_PATH = './models/model_gbc.joblib'
TEMP_PATH = './temp/'
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)


def load_df():
    try:
        file_path = os.path.join(TEMP_PATH, 'df.pkl')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
        df = pd.read_pickle(file_path)
        return df
    except (FileNotFoundError, pd.errors.PickleError) as e:  # Gérer les erreurs de fichier et de lecture pickle
        raise AirflowException(f"Erreur lors du chargement du DataFrame : {e}")


def save_model(trained_model):
    try:
        if not os.path.exists(MODEL_PATH):
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True) # create directory if it doesn't exist.
        joblib.dump(trained_model, MODEL_PATH)
        print('Modèle enregistré avec succès.')
    except (OSError, TypeError) as e:  # Gérer les erreurs d'écriture et de type incorrect
        raise AirflowException(f"Erreur lors de l'enregistrement du modèle : {e}")

def training_model(df):
    try:
        df.drop(columns=['MinTemp', 'Temp9am'], inplace=True)  # Drop unnecessary columns
        X = df.drop('RainTomorrow', axis=1)
        y = df['RainTomorrow']

        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

        model_rf = RandomForestClassifier(criterion='entropy', n_estimators=40)
        model_rf.fit(X_train, y_train)
        y_pred = model_rf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f'Initial Model Accuracy: {accuracy:.4f}')
        print(classification_report(y_test, y_pred))

        param_grid = {'n_estimators': [1, 5, 9, 13, 15, 19, 22]}
        grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
        grid_search.fit(X_train, y_train)
        print("Best Hyperparameters:", grid_search.best_params_)
        print("Best GridSearchCV Score:", grid_search.best_score_)

        best_rf = RandomForestClassifier(**grid_search.best_params_)
        best_rf.fit(X_train, y_train)
        y_pred = best_rf.predict(X_test)
        print(f'Final Model Classification Report:\n{classification_report(y_test, y_pred)}')
        print('\nTraining completed successfully!')
        return best_rf

    except Exception as e:
        print(f"An error occurred during training: {e}")

def train_and_save_model(**kwargs):
    #msg = kwargs['ti'].xcom_pull(task_ids='prepare_data', key='prepared_data')
    df = load_df()
    best_rf = training_model(df)
    save_model(best_rf)
    #kwargs['ti'].xcom_push(key='train_and_save_model', value=msg)