"""
Prediction Tab
"""

import streamlit as st

import os
import requests

# API address definition
api_address = os.getenv('API_ADDR', default='localhost')
# API port
api_port = int(os.getenv('API_PORT', default='8000'))

title = "Prédictions de données météorologiques en Australie"
sidebar_name = "Prédiction"


def get_locations():
    url = 'http://{address}:{port}/locations'
    r = requests.get(url=url.format(address=api_address,
                                    port=api_port))
    # Request status
    status_code = r.status_code

    # Results check
    if status_code == 200:
        return r.json()
    return None


def get_prediction(loc_id):
    url = 'http://{address}:{port}/predict/{location_id}'
    r = requests.get(url=url.format(address=api_address,
                                    port=api_port,
                                    location_id=loc_id))
    # Request status
    status_code = r.status_code

    # Results check
    if status_code == 200:
        return r.json()
    return None


def run():

    st.title(title)

    st.divider()

    st.subheader("Objectif")

    st.markdown("Pour le lendemain, prédire s'il pleuvra ou non.")

    st.divider()

    """
    st.subheader("Accès")

    login = st.text_input(label="Utilisateur")
    password = st.text_input(label="Mot de passe",
                             type="password")

    st.divider()
    """

    st.subheader("Formulaire")

    locations = get_locations()
    # st.write('Got :\n', locations)

    locations_names = []
    locations_ids = []
    for item in locations:
        locations_names.append(item['Location_Name'])
        locations_ids.append(item['Location_Code'])

    location_name = \
        st.selectbox(label='Veuillez sélectionner une localité s.v.p.',
                     options=locations_names,
                     index=0,
                     key=1)

    location_id = 0
    for loc_name, loc_id in zip(locations_names, locations_ids):
        if loc_name == location_name:
            location_id = loc_id
            break

    st.write('Vous avez sélectionné : {}, {}'.format(location_name,
                                                     location_id))

    st.divider()

    st.subheader("Résultat")

    rain_tomorrow = get_prediction(location_id)
    # st.write("rain_tomorrow : ", rain_tomorrow)

    if rain_tomorrow:
        st.write("Il pleuvra sans doute demain.")
    else:
        st.write("Il ne pleuvra peut-être pas demain.")
