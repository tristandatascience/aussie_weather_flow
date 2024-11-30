import numpy as np 
import pandas as pd 
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
import os
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, cohen_kappa_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import OneHotEncoder
from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.utils import resample

def starts_with_letter(x):
    return isinstance(x, str) and x[0].isalpha()

data = "./data/pandas/weatherAUS.csv"

def cleaning():
    df = pd.read_csv(data, header=0)
    print(df.info())
    # on parse la variable date en format datetime et on crée 3 variables
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    # on supprime Date
    df.drop('Date', axis=1, inplace = True)
    df['RainToday'].replace({'No': 0, 'Yes': 1}, inplace=True)
    df['RainTomorrow'].replace({'No': 0, 'Yes': 1}, inplace=True)


    yes = df[df['RainTomorrow'] == 1]
    no = df[df['RainTomorrow'] == 0]
    yes_oversampled = resample(yes, replace=True, n_samples=len(no), random_state=123)
    oversampled = pd.concat([no, yes_oversampled])
    df = pd.DataFrame(oversampled)
    categorical = [var for var in df.columns if df[var].dtype=='O']

    df['WindGustDir'] = df['WindGustDir'].fillna(df['WindGustDir'].mode()[0])
    df['WindDir9am'] = df['WindDir9am'].fillna(df['WindDir9am'].mode()[0])
    df['WindDir3pm'] = df['WindDir3pm'].fillna(df['WindDir3pm'].mode()[0])

    numerical = [var for var in df.columns if df[var].dtype!='O']

    df2 = pd.DataFrame(columns=df.columns)

    for ville in df['Location'].unique():
        df_ville = pd.DataFrame(df[df['Location'] == ville])
    
        ## pour les valeurs nulles restantes, on remplace par la médiane
        df_ville[numerical] = df_ville[numerical].fillna(df_ville[numerical].median())

        ## si la médiane est nulle, on remplace par 0
        df_ville[numerical] = df_ville[numerical].fillna(0)
        
        df_ville = df_ville.reset_index(drop=True)
        df2 = pd.concat([df2, df_ville])


    df = pd.DataFrame(df2)


    outliers = ['MinTemp', 'MaxTemp', 'Rainfall', 'Evaporation', 'WindGustSpeed',
            'WindSpeed9am', 'WindSpeed3pm', 'Humidity9am', 'Pressure9am', 
            'Pressure3pm', 'Temp9am', 'Temp3pm']



    mask = pd.Series([True] * len(df), index=df.index)
    for col in outliers:
        if col in df.columns:
            mask &= ~df[col].apply(starts_with_letter)

    df_cleaned = df[mask]
    print(f"Nombre de lignes supprimées : {len(df) - len(df_cleaned)}")
    print(df_cleaned.head())


    df = df_cleaned
    df.dropna(inplace=True)
    df[['WindSpeed3pm', 'WindSpeed9am']] = df[['WindSpeed3pm', 'WindSpeed9am']].astype(float)

    for feature in outliers:
        print(feature)
        q1 = df[feature].quantile(0.25)
        q3 = df[feature].quantile(0.75)
        IQR = q3-q1
        lower_limit = q1 - (IQR*1.5)
        upper_limit = q3 + (IQR*1.5)
        df.loc[df[feature]<lower_limit,feature] = lower_limit
        df.loc[df[feature]>upper_limit,feature] = upper_limit


    def get_location_mapping(df):
        # Obtenir les codes et les valeurs uniques pour Location
        codes, uniques = pd.factorize(df['Location'])
        
        # Créer le DataFrame de mapping
        location_mapping = pd.DataFrame({
            'Location_Name': uniques,
            'Location_Code': range(len(uniques))
        })
        
        return location_mapping

    # Créer d'abord le mapping des locations
    location_mapping = get_location_mapping(df)

    # Puis faire l'encodage normal
    def encode_data(feature_name):
        codes, uniques = pd.factorize(df[feature_name])
        mapping_dict = dict(zip(uniques, range(len(uniques))))
        return codes

    # Application sur toutes les colonnes catégorielles
    for col in categorical:
        df[col] = encode_data(col)

    # Afficher le mapping des locations
    print(location_mapping)
    df.to_csv('./data/w_clean.csv', index=False)
    location_mapping.to_csv('./data/location_mapping.csv', index=False)
    print('ok')
