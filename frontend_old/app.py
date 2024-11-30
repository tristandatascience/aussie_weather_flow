import streamlit as st
import requests

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

# Fonction pour effectuer une prédiction
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
                    st.write(f"Prediction for {city}: {prediction}")
        else:
            st.error("No stations available")

    # Page "Admin"
    elif page == "Admin":
        st.subheader("Admin Page")
        
        if "token" in st.session_state:
            st.success("You are logged in!")
            
            if st.button("Train Model"):
                train()
        else:
            st.info("Please log in to access admin functionalities")
            login()

if __name__ == "__main__":
    main()