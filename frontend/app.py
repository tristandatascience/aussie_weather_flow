import time
import streamlit as st
import requests
import pandas as pd

# URL de base de l'API FastAPI
BASE_URL = "http://fastapi:8000"

# -- Helpers d'état --
def init_state():
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("training_in_progress", False)
    st.session_state.setdefault("train_result_msg", None)
    st.session_state.setdefault("train_last_ok", None)
    st.session_state.setdefault("baseline_model_count", None)
    st.session_state.setdefault("polling_interval_s", 5)  # intervalle de polling pour /models
    st.session_state.setdefault("max_wait_s", 60 * 60)    # timeout max (1h)
    st.session_state.setdefault("loaded_model_version", None)

# Fonctions API
def get_stations():
    try:
        response = requests.get(f"{BASE_URL}/locations", timeout=30)
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

def predict(station_id):
    try:
        response = requests.get(f"{BASE_URL}/predict/{station_id}", timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to get prediction")
            return None
    except Exception as e:
        st.error(f"Error during prediction: {e}")
        return None

def predict_with_model(station_id, model_version):
    try:
        response = requests.get(f"{BASE_URL}/predict-with-model/{model_version}/{station_id}", timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to get prediction with custom model")
            return None
    except Exception as e:
        st.error(f"Error during prediction with custom model: {e}")
        return None

def login():
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="btn_login"):
        try:
            token_response = requests.post(
                f"{BASE_URL}/token",
                data={"username": user, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            if token_response.status_code == 200:
                token = token_response.json().get("access_token")
                st.session_state.token = token
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"Login failed: {e}")

    return False

def train():
    if "token" in st.session_state and st.session_state.token:
        try:
            response = requests.post(
                f"{BASE_URL}/admin/refresh",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                timeout=30  # requête courte: le backend déclenche et rend la main
            )
            if response.status_code == 200:
                # Le backend déclenche l'entraînement (asynchrone côté Airflow)
                return True, "Entraînement déclenché."
            elif response.status_code == 409:
                # Si tu ajoutes un verrou côté backend, tu peux gérer ce cas
                return True, "Un entraînement est déjà en cours. Suivi en cours…"
            else:
                return False, f"Lancement de l'entraînement refusé (code {response.status_code})"
        except Exception as e:
            return False, f"Lancement de l'entraînement impossible: {e}"
    else:
        return False, "Vous devez être connecté pour entraîner un modèle"

def get_all_model_versions():
    try:
        response = requests.get(f"{BASE_URL}/models", timeout=60)
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
        response = requests.post(f"{BASE_URL}/models/{version}/load", timeout=60)
        if response.status_code == 200:
            return True
        else:
            st.error("Échec du chargement du modèle")
            return False
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle : {e}")
        return False

def render_models_table(models):
    if not models:
        st.warning("Aucun modèle disponible.")
        return
    models_data = []
    for model in models:
        models_data.append({
            "Version": model["version"],
            "Date de création": model["creation_date"],
            "Statut": model["status"],
            "F1-Score": f"{model['metrics']['f1_score']:.3f}" if model.get("metrics") else "",
            "Précision": f"{model['metrics']['precision']:.3f}" if model.get("metrics") else "",
            "Rappel": f"{model['metrics']['recall']:.3f}" if model.get("metrics") else ""
        })
    df = pd.DataFrame(models_data)
    st.dataframe(df)

def admin_actions_count_based():
    st.subheader("Gestion des Modèles")
    models = get_all_model_versions()
    render_models_table(models)

    if models:
        selected_version = st.selectbox(
            "Sélectionner une version du modèle",
            options=[m["version"] for m in models],
            format_func=lambda x: f"Version {x}"
        )
        if st.button("Charger le modèle sélectionné", key="btn_load"):
            if load_model_version(selected_version):
                st.success(f"Modèle version {selected_version} chargé avec succès")
                
                # Stocker le modèle chargé dans session state
                st.session_state.loaded_model_version = selected_version
                st.rerun()

    st.subheader("Actions sur les Modèles")

    # Si entraînement en cours: spinner + polling avec mise à jour in-place
    if st.session_state.training_in_progress:
        with st.spinner("Entraînement en cours... Détection du nouveau modèle"):
            baseline_count = st.session_state.baseline_model_count or 0
            interval_s = st.session_state.polling_interval_s
            max_wait_s = st.session_state.max_wait_s
            waited = 0

            st.caption(
                f"Nombre de modèles de référence: {baseline_count} | cible: {baseline_count + 1}"
            )

            # Placeholder pour mise à jour sans duplication
            status_placeholder = st.empty()

            while True:
                current_models = get_all_model_versions()
                current_count = len(current_models)

                # Mettre à jour le même bloc, sans créer de nouvelles lignes
                status_placeholder.write(f"Modèles présents: {current_count} / objectif: {baseline_count + 1}")

                # Vérifier si on a au moins un modèle de plus qu'au départ
                if current_count > baseline_count:
                    st.session_state.train_last_ok = True
                    st.session_state.train_result_msg = f"Entraînement terminé: {current_count - baseline_count} nouveau(x) modèle(s) disponible(s)."
                    st.session_state.training_in_progress = False
                    st.rerun()

                time.sleep(interval_s)
                waited += interval_s
                if waited >= max_wait_s:
                    st.session_state.train_last_ok = False
                    st.session_state.train_result_msg = "Timeout: aucun nouveau modèle détecté."
                    st.session_state.training_in_progress = False
                    st.rerun()

    # Afficher message de résultat si dispo
    if st.session_state.train_result_msg:
        if st.session_state.train_last_ok:
            st.success(st.session_state.train_result_msg)
        else:
            st.error(st.session_state.train_result_msg)
        # Nettoyage pour éviter répétition
        st.session_state.train_result_msg = None

    # Bouton d’entraînement (désactivé si en cours)
    disabled = st.session_state.training_in_progress
    if st.button("Entraîner un nouveau modèle", key="btn_train", disabled=disabled):
        # Mémoriser la baseline (nombre de modèles actuel)
        baseline = len(models) if models else 0
        st.session_state.baseline_model_count = baseline

        # Déclencher l’entraînement
        ok, msg = train()
        if ok:
            st.info(msg or "Entraînement déclenché.")
            # Passer en mode polling et désactiver le bouton immédiatement
            st.session_state.training_in_progress = True
            st.rerun()
        else:
            st.error(msg or "Lancement de l'entraînement refusé")

# Fonction principale
def main():
    init_state()

    st.title("Weather App")

    page = st.sidebar.selectbox("Select a Page", ["Predict", "Admin"])

    if page == "Predict":
        st.subheader("Prediction Page")

        stations = get_stations()
        if stations:
            city = st.selectbox("Select a City", options=list(stations.keys()))
            
            # Vérifier si un modèle personnalisé est chargé
            model_mode = st.radio("Choisissez le modèle pour la prédiction",
                                ["Modèle de production", "Modèle chargé (seulement si un modèle a testé est chargé par Admin)"],
                                key="model_mode")
            
            if st.button("Predict", key="btn_predict"):
                station_id = stations[city]
                
                if model_mode == "Modèle chargé":
                    if "loaded_model_version" in st.session_state and st.session_state.loaded_model_version:
                        prediction = predict_with_model(station_id, st.session_state.loaded_model_version)
                        model_info = f" (Modèle version {st.session_state.loaded_model_version})"
                    else:
                        st.error("Aucun modèle personnalisé n'a été chargé. Veuillez d'abord charger un modèle dans la page Admin.")
                        return
                else:
                    prediction = predict(station_id)
                    model_info = ""
                
                if prediction:
                    # Extraire la prédiction - gérer à la fois les formats [0.0] et 0.0
                    prediction_data = prediction.get('prediction', [0])
                    if isinstance(prediction_data, list):
                        prediction_value = prediction_data[0]
                    else:
                        prediction_value = prediction_data
                    
                    # Déterminer s'il va pleuvoir
                    will_rain = prediction_value > 0.5
                    
                    # Créer un affichage joli
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"### 🌤️ Prédiction pour {city}{model_info}")
                        
                        if will_rain:
                            st.error(f"**Prévision de pluie** 🌧️")
                            st.write(f"Probabilité de pluie: {prediction_value:.1%}")
                        else:
                            st.success(f"**Pas de pluie prévue** ☀️")
                            st.write(f"Probabilité de pluie: {prediction_value:.1%}")
                    
                    with col2:
                        # Afficher une icône en fonction de la prédiction
                        if will_rain:
                            st.image("https://cdn-icons-png.flaticon.com/512/4150/4150904.png", width=100, caption="Pluie")
                        else:
                            st.image("https://cdn-icons-png.flaticon.com/512/979/979585.png", width=100, caption="Soleil")
                        
                        # Afficher les détails techniques
                        with st.expander("Détails techniques"):
                            st.write(f"**Location ID:** {prediction.get('location_id', 'N/A')}")
                            st.write(f"**Score de prédiction:** {prediction_value:.3f}")
        else:
            st.error("No stations available")

    elif page == "Admin":
        st.subheader("Page d'Administration")

        if st.session_state.token:
            st.success("Vous êtes connecté !")
            admin_actions_count_based()
        else:
            st.info("Veuillez vous connecter pour accéder aux fonctionnalités d'administration")
            login()

if __name__ == "__main__":
    main()