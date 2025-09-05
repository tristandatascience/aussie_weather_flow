from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict
import httpx
from datetime import timedelta
import os , sys
import joblib
import httpx
from fastapi import FastAPI, HTTPException
import aiohttp
from pydantic import BaseModel
from typing import List
import os
import asyncio
import base64
import uuid
from weather_utils.model_functions import load_df, predict_with_model
from weather_utils.mlflow_functions import get_all_model_versions, load_specific_model_version
from auth import (
    create_access_token,
    get_current_user,
    verify_password,
    users_db
)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token",scheme_name="JWT")

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
AIRFLOW_API_URL = os.getenv("AIRFLOW_API_URL")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MODEL_PATH = os.getenv("MODEL_PATH")
TEMP_PATH = os.getenv("TEMP_PATH")



import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = users_db.get(form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/predict/{location_id}")
async def predict(location_id: int):
    try:
        # Charger le modèle depuis MLflow (version Production)
        from weather_utils.mlflow_functions import get_production_model
        model = get_production_model()
        
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No production model available in MLflow"
            )
        
        # Charger les données
        df = load_df()
        location_mapping = pd.read_csv('./data/location_mapping.csv')
        
        # Filtrer les données pour la location spécifique
        location_data = df[df.Location == location_id][:1]
        
        if location_data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location ID {location_id} not found"
            )
        
        # Faire la prédiction
        prediction = predict_with_model(model, location_data)
        return {"location_id": location_id, "prediction": prediction}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/predict-with-model/{version}")
async def predict_with_model_version(location_id: int, version: str):
    """
    Fait une prédiction en utilisant un modèle spécifique chargé depuis MLflow
    """
    try:
        # Charger le modèle spécifique depuis MLflow
        from weather_utils.mlflow_functions import load_specific_model_version
        model = load_specific_model_version(version)
        
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modèle version {version} non trouvé"
            )
        
        # Charger les données
        df = load_df()
        location_mapping = pd.read_csv('./data/location_mapping.csv')
        
        # Filtrer les données pour la location spécifique
        location_data = df[df.Location == location_id][:1]
        
        if location_data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location ID {location_id} not found"
            )
        
        # Faire la prédiction avec le modèle spécifique
        predictions = predict_with_model(model, location_data)
        return {
            "location_id": location_id,
            "prediction": predictions[0],
            "model_version": version,
            "message": "Prédiction effectuée avec le modèle spécifique"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



from typing import List, Dict, Union
import pandas as pd
@app.get("/locations", response_model=List[Dict[str, Union[int, str]]])
async def get_locations():
    try:
        location_mapping = pd.read_csv('./data/location_mapping.csv')
        locations = location_mapping.to_dict('records')
        return locations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



auth = f"{AIRFLOW_USERNAME}:{AIRFLOW_PASSWORD}".encode("utf-8")
AIRFLOW_TOKEN = base64.b64encode(auth).decode("utf-8")

print(f"Basic {AIRFLOW_TOKEN}")

class DagTriggerResponse(BaseModel):
    dags: List[str]
    status: str

async def trigger_dag(dag_id: str):
    # Base configuration
    auth = f"{AIRFLOW_USERNAME}:{AIRFLOW_PASSWORD}".encode("utf-8")
    token = base64.b64encode(auth).decode("utf-8")
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # First, unpause the DAG
        unpause_url = f"{AIRFLOW_API_URL}/dags/{dag_id}"
        unpause_data = {"is_paused": False}
        
        async with session.patch(unpause_url, headers=headers, json=unpause_data) as unpause_response:
            if unpause_response.status not in [200, 204]:
                raise HTTPException(
                    status_code=unpause_response.status, 
                    detail=f"Failed to unpause DAG: {await unpause_response.text()}"
                )

        # Then trigger the DAG
        trigger_url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"
        dag_run_id = f"triggered_via_fastapi_{uuid.uuid4()}"
        trigger_data = {
            "conf": {},
            "dag_run_id": f"triggered_via_fastapi_{dag_run_id}"
        }
        
        async with session.post(trigger_url, headers=headers, json=trigger_data) as trigger_response:
            if trigger_response.status != 200:
                raise HTTPException(
                    status_code=trigger_response.status, 
                    detail=f"Failed to trigger DAG: {await trigger_response.text()}"
                )
            return await trigger_response.json()

@app.post("/admin/refresh", response_model=DagTriggerResponse)
async def refresh_dags(auth_token: str = Depends(oauth2_scheme)):
    final_token = auth_token
    if not final_token:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Not authenticated in fastapi"
      )
    current_user = get_current_user(final_token)
    print(f"Current user: {current_user}") 
    dags_to_trigger = ["data_ingest_and_train_dag"]
    tasks = [trigger_dag(dag_id) for dag_id in dags_to_trigger]
    results = await asyncio.gather(*tasks)
    return DagTriggerResponse(
        dags=[f"{dag_id} - {result['dag_run_id']}" for dag_id, result in zip(dags_to_trigger, results)],
        status="success"
    )


#import logging
#import mlflow
#from mlflow.tracking import MlflowClient
#from fastapi import FastAPI, HTTPException, Depends, status, Security
# ... autres imports ...

# Configuration du logger
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

# Configuration de MLflow (à ajouter après la création de l'app)
#mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

@app.get("/models")
def list_models():
    try:
        models = get_all_model_versions()
        logger.debug(f"Modèles récupérés: {models}")
        
        if not models:
            return {
                "message": "Aucun modèle n'est actuellement enregistré dans MLflow",
                "models": [],
                "status": "success"
            }
        return {
            "message": f"{len(models)} modèle(s) trouvé(s)",
            "models": models,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la communication avec MLflow : {str(e)}"
        )

@app.get("/models/{version}")
def get_model_info(version: str):
    models = get_all_model_versions()
    model_info = next((m for m in models if m['version'] == version), None)
    if model_info is None:
        raise HTTPException(status_code=404, detail="Version du modèle non trouvée")
    return model_info


@app.post("/models/{version}/load")
def load_model(version: str):
    """
    Charge une version spécifique du modèle depuis MLflow
    """
    try:
        # Charger le modèle spécifique depuis MLflow
        model = load_specific_model_version(version)
        if model is None:
            raise HTTPException(status_code=404, detail=f"Impossible de charger la version {version} du modèle")
        
        return {
            "message": f"Modèle version {version} chargé avec succès depuis MLflow",
            "source": "MLflow",
            "version": version,
            "model_name": "RandomForestClassifier",
            "note": "Le modèle est géré par MLflow, pas de sauvegarde locale nécessaire"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du chargement du modèle: {str(e)}"
        )