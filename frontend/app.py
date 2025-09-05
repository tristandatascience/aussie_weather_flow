import streamlit as st
import requests
import pandas as pd
# URL de base de l'API FastAPI
BASE_URL = "http://fastapi:8000"

# Fonction pour récupérer les stations depuis l'API
def get_stations():
    try:
        response = requests.get(f"{BASE_URL}/locations")
        if response.status_code == 200:
            locations = response.json()
            stations = {location["Location_Name"]: location["Location_Code"] for location in locations}
            return stations
        else:
            st.error("Failed to fetch stations")
            return {}
    except Exception as e:
        st.error(f"Error fetching stations: {e}")
        return {}

# Fonction pour effectuer une prédiction avec le modèle de production
def predict(station_id):
    try:
        response = requests.get(f"{BASE_URL}/predict/{station_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to get prediction")
            return None
    except Exception as e:
        st.error(f"Error during prediction: {e}")
        return None

# Fonction pour effectuer une prédiction avec un modèle spécifique
def predict_with_model(station_id, version):
    try:
        response = requests.get(f"{BASE_URL}/predict-with-model/{version}?location_id={station_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to get prediction with specific model")
            return None
    except Exception as e:
        st.error(f"Error during prediction with specific model: {e}")
        return None

# Fonction pour se connecter (Admin page)
def login():
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            token_response = requests.post(
                f"{BASE_URL}/token",
                data={"username": user, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if token_response.status_code == 200:
                token = token_response.json().get("access_token")
                st.session_state.token = token
                st.success("Login successful")
                st.rerun()  # Utilisation de st.rerun() au lieu de st.experimental_rerun()
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"Login failed: {e}")
    
    return False

# Fonction pour entraîner le modèle (Admin page)
def train():
    if "token" in st.session_state:
        try:
            response = requests.post(
                f"{BASE_URL}/admin/refresh",
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            if response.status_code == 200:
                st.success("Latest data retrieval and training launched successfully")
            else:
                st.error("data retrieval and training failed")
        except Exception as e:
            st.error(f"data retrieval and training failed: {e}")
    else:
        st.error("You must be logged in to train the model")


def get_all_model_versions():
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            return response.json().get("models", [])
        else:
            st.error("Échec de la récupération des modèles")
            return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des modèles : {e}")
        return []

def load_model_version(version):
    try:
        response = requests.post(f"{BASE_URL}/models/{version}/load")
        if response.status_code == 200:
            return True
        else:
            st.error("Échec du chargement du modèle")
            return False
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {e}")
        return False


# Fonction principale
def main():
    st.title("Weather App")
    
    # Menu de navigation
    page = st.sidebar.selectbox(
        "Select a Page",
        ["Predict", "Admin"]
    )
    
    # Page "Predict"
    if page == "Predict":
        st.subheader("Prediction Page")
        
        stations = get_stations()
        if stations:
            city = st.selectbox("Select a City", options=list(stations.keys()))
            
            if st.button("Predict"):
                station_id = stations[city]
                prediction = predict(station_id)
                if prediction:
                    st.success(f"Prédiction pour {city}:")
                    st.write(f"- Prédiction: {'Pluie' if prediction['prediction'] == 1 else 'Pas de pluie'}")
                    st.write(f"- Version du modèle utilisée: Production")
        else:
            st.error("No stations available")

    # Page "Admin"
    elif page == "Admin":
        st.subheader("Page d'Administration")
        
        if "token" in st.session_state:
            st.success("Vous êtes connecté !")
            
            # Section des modèles
            st.subheader("Gestion des Modèles")
            
            models = get_all_model_versions()
            if not models:
                st.warning("Aucun modèle disponible.")
            else:
                # Création d'un DataFrame pour un affichage plus propre
                models_data = []
                for model in models:
                    models_data.append({
                        "Version": model["version"],
                        "Date de création": model["creation_date"],
                        "Statut": model["status"],
                        "F1-Score": f"{model['metrics']['f1_score']:.3f}",
                        "Précision": f"{model['metrics']['precision']:.3f}",
                        "Rappel": f"{model['metrics']['recall']:.3f}"
                    })
                
                df = pd.DataFrame(models_data)
                st.dataframe(df)
                
                # Sélection et chargement d'un modèle
                selected_version = st.selectbox(
                    "Sélectionner une version du modèle",
                    options=[m["version"] for m in models],
                    format_func=lambda x: f"Version {x}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Entraîner un nouveau modèle"):
                        train()
                
                # Section de prédiction avec le modèle sélectionné
                st.subheader("Prédiction avec le modèle sélectionné")
                stations = get_stations()
                if stations:
                    city = st.selectbox("Sélectionnez une ville pour la prédiction", options=list(stations.keys()))
                    
                    if st.button("Faire la prédiction avec ce modèle"):
                        station_id = stations[city]
                        prediction = predict_with_model(station_id, selected_version)
                        if prediction:
                            st.success(f"Prédiction pour {city} avec le modèle version {selected_version}:")
                            st.write(f"- Prédiction: {'Pluie' if prediction['prediction'] == 1 else 'Pas de pluie'}")
                            st.write(f"- Version du modèle utilisée: {prediction['model_version']}")
                            st.write(f"- Message: {prediction['message']}")
                else:
                    st.error("Aucune station disponible")

            
        else:
            st.info("Veuillez vous connecter pour accéder aux fonctionnalités d'administration")
            login()



if __name__ == "__main__":
    main()


