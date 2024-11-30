# tests/test_model_functions.py

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from weather_utils.model_functions import predict_with_model, training_model, train_and_save_model,  save_model, MODEL_PATH, TEMP_PATH
import os
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import joblib
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


@pytest.fixture
def mock_data():
  """Fixture pour créer un DataFrame mock avec les colonnes nécessaires."""
  data = {
      'Location': [0] * 10,
      'MinTemp': [17.0, 21.8, 16.3, 15.3, 19.3, 22.0, 23.8, 27.6, 28.9, 20.9],
      'MaxTemp': [17.0, 21.8, 16.3, 15.3, 19.3, 22.0, 23.8, 27.6, 28.9, 20.9],
      'Rainfall': [0.0, 0.0, 1.4, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      'Evaporation': [0.0] * 10,
      'Sunshine': [0.0] * 10,
      'WindGustDir': [0, 1, 1, 2, 3, 4, 5, 5, 6, 2],
      'WindGustSpeed': [20.0, 26.0, 46.0, 24.0, 20.0, 26.0, 26.0, 22.0, 57.0, 24.0],
      'WindDir9am': [0, 1, 2, 3, 4, 3, 1, 1, 3, 4],
      'WindDir3pm': [0, 1, 1, 2, 2, 0, 3, 0, 4, 5],
      'WindSpeed9am': [0, 1, 2, 3, 3, 1, 1, 4, 5, 0],
      'WindSpeed3pm': [0, 1, 1, 2, 2, 3, 2, 3, 4, 5],
      'Humidity9am': [75.0, 61.0, 51.0, 70.0, 69.0, 54.0, 38.0, 42.0, 23.5, 73.0],
      'Humidity3pm': [63.0, 37.0, 43.0, 53.0, 53.0, 37.0, 30.0, 22.0, 14.0, 48.0],
      'Pressure9am': [1027.4, 1021.2, 1018.0, 1033.3, 1034.6, 1033.3, 1031.6, 1028.8, 1021.9, 1023.7],
      'Pressure3pm': [1023.2, 1017.1, 1018.4, 1031.2, 1031.3, 1030.5, 1028.5, 1024.8, 1015.5, 1021.4],
      'Cloud9am': [0.0] * 10,
      'Cloud3pm': [0.0] * 10,
      'Temp9am': [16.3, 21.2, 15.8, 14.5, 17.2, 21.7, 23.5, 26.8, 28.7, 20.8],
      'Temp3pm': [16.3, 21.2, 15.8, 14.5, 17.2, 21.7, 23.5, 26.8, 28.7, 20.8],
      'RainToday': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
      'RainTomorrow': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      'Year': [2023] * 10,
      'Month': [9] * 10,
      'Day': list(range(1, 11))
  }
  return pd.DataFrame(data)


import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def test_training_model(mock_data):
    model = training_model(mock_data)
    
    assert isinstance(model, RandomForestClassifier), "Le modèle retourné n'est pas un RandomForestClassifier"
    assert hasattr(model, 'feature_importances_'), "Le modèle ne semble pas avoir été entraîné"
    assert len(model.feature_importances_) > 0, "Les feature_importances_ sont vides"
    

def test_save_model():
  """Test pour la fonction save_model."""
  mock_model = MagicMock()
  with patch('weather_utils.model_functions.joblib.dump') as mock_joblib_dump:
      save_model(mock_model)

      mock_joblib_dump.assert_called_once_with(mock_model, MODEL_PATH)


def test_predict_with_model(mock_data):
    """Test for the predict_with_model function."""
    test_data = mock_data.copy()
    test_data.drop(columns=['MinTemp', 'Temp9am', 'RainTomorrow'], inplace=True)
    test_model = training_model(mock_data)
    predictions = predict_with_model(test_model,test_data[:1] )
    
    assert len(predictions) > 0, "Le modèle ne produit pas de prédictions"
    assert predictions[0] in [0, 1], "Les prédictions ne sont pas binaires (0 ou 1)"