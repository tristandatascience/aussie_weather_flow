import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV
import pytest

@pytest.fixture
def load_data():
    df = pd.read_csv("../../data/w_clean.csv", header=0, index_col=0)
    return df

def test_load_data(load_data):
    df = load_data
    assert not df.empty, "Le DataFrame ne doit pas être vide"


def test_drop_columns(load_data):
    df = load_data
    df.drop(columns=['MinTemp', 'Temp9am'], inplace=True)
    assert 'MinTemp' not in df.columns, "La colonne 'MinTemp' doit être supprimée"
    assert 'Temp9am' not in df.columns, "La colonne 'Temp9am' doit être supprimée"


def test_random_forest_model(load_data):
    df = load_data
    X = df.drop(['RainTomorrow'], axis=1)
    y = df['RainTomorrow']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model_rf = RandomForestClassifier(criterion='entropy', n_estimators=40)
    model_rf.fit(X_train, y_train)
    y_pred = model_rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    assert accuracy >= 0, "L'accuracy doit être supérieure ou égale à 0"

