"""
Prediction Tab
"""

import streamlit as st

import os
import requests

# API address definition
api_address = os.getenv('API_ADDR', default='fastapi')
# API port
api_port = int(os.getenv('API_PORT', default='8000'))

title = "Prédictions de données météorologiques en Australie"
sidebar_name = "Prédiction"


def get_locations():
    """
    This function retrieves the locations.
    """
    try:
        url = 'http://{address}:{port}/locations'
        response = requests.get(url=url.format(address=api_address,
                                               port=api_port))
        if response.status_code == 200:
            locations_list = response.json()
            locations = {location["Location_Name"]: location["Location_Code"]
                         for location in locations_list}
            return locations
        else:
            st.error("Erreur HTTP lors de la récupération des localités : ",
                     f"{response.status_code}.")
            return None
    except Exception as e:
        st.error(f"Exception lors de la récupération des localités : {e}.")
        return None


def get_prediction(loc_id):
    """
    This function retrieves the prediction for the location.
    """
    try:
        url = 'http://{address}:{port}/predict/{location_id}'
        response = requests.get(url=url.format(address=api_address,
                                               port=api_port,
                                               location_id=loc_id))
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Erreur HTTP lors de la récupération de la prédiction : "
                     f"{response.status_code}.")
            return None
    except Exception as e:
        st.error(f"Exception lors de la récupération de la prédiction : {e}.")
        return None


def run():

    st.title(title)

    st.divider()

    st.subheader("Objectif")

    st.markdown("Pour le lendemain, prédire s'il pleuvra ou non.")

    st.divider()

    st.subheader("Formulaire")

    locations = get_locations()
    # st.write('Got :\n', locations)

    if locations is not None:
        location_name = \
            st.selectbox(label='Veuillez sélectionner une localité s.v.p.',
                         options=list(locations.keys()),
                         index=0,
                         key=1)

        if st.button("Prédire"):
            location_id = locations[location_name]
            prediction = get_prediction(location_id)

            if prediction is not None:
                st.divider()
                st.subheader("Résultat")
                prediction_value = prediction.get('prediction', [None])[0] 
                
                if prediction_value is not None:  
                    mapping = {0: "pas de pluie demain", 1: "pluie demain"}
                    mapped_prediction = mapping.get(int(prediction_value), "valeur inconnue") 
                    st.write(f"Prédiction pour {location_name} : {mapped_prediction}")
                else:
                    st.error("Impossible de lire la valeur de la prédiction.")