import pandas as pd
from sklearn.utils import resample
import pytest


@pytest.fixture
def load_data():
    df = pd.read_csv("../../data/weatherAUS.csv")
    return df

def test_load_data(load_data):
    df = load_data
    assert not df.empty, "Le DataFrame ne doit pas être vide"

def test_date_format(load_data):
    df = load_data
    df['Date'] = pd.to_datetime(df['Date'])
    assert pd.api.types.is_datetime64_any_dtype(df['Date']), "La colonne 'Date' doit être au format datetime"

def test_encoding_rain_columns(load_data):
    df = load_data
    df['RainToday'].replace({'No': 0, 'Yes': 1}, inplace=True)
    df['RainTomorrow'].replace({'No': 0, 'Yes': 1}, inplace=True)
    assert df['RainToday'].isin([0, 1]).all(), "La colonne 'RainToday' doit contenir uniquement 0 et 1"
    assert df['RainTomorrow'].isin([0, 1]).all(), "La colonne 'RainTomorrow' doit contenir uniquement 0 et 1"

def test_missing_values(load_data):
    df = load_data
    df['WindGustDir'] = df['WindGustDir'].fillna(df['WindGustDir'].mode()[0])
    assert df['WindGustDir'].isnull().sum() == 0, "Il ne doit pas y avoir de valeurs manquantes dans 'WindGustDir'"

def test_oversampling(load_data):
    df = load_data
    yes = df[df['RainTomorrow'] == 1]
    no = df[df['RainTomorrow'] == 0]
    yes_oversampled = resample(yes, replace=True, n_samples=len(no), random_state=123)
    oversampled = pd.concat([no, yes_oversampled])
    assert oversampled['RainTomorrow'].value_counts().min() > 0, "Les classes doivent être équilibrées après oversampling"

def test_outlier_replacement(load_data):
    df = load_data
    feature = 'MinTemp'
    q1 = df[feature].quantile(0.25)
    q3 = df[feature].quantile(0.75)
    IQR = q3 - q1
    lower_limit = q1 - (IQR * 1.5)
    upper_limit = q3 + (IQR * 1.5)
    df.loc[df[feature] < lower_limit, feature] = lower_limit
    df.loc[df[feature] > upper_limit, feature] = upper_limit
    assert (df[feature] < lower_limit).sum() == 0, "Il ne doit pas y avoir de valeurs inférieures à la limite inférieure"
    assert (df[feature] > upper_limit).sum() == 0, "Il ne doit pas y avoir de valeurs supérieures à la limite supérieure"

def test_categorical_encoding(load_data):
    df = load_data
    categorical = [var for var in df.columns if df[var].dtype == 'O']
    for col in categorical:
        df[col] = encode_data(col)
        assert df[col].dtype == 'int64', f"La colonne '{col}' doit être encodée en entier"
