"""
Administration Tab
"""

import streamlit as st

import os
import requests

# API address definition
api_address = os.getenv('API_ADDR', default='fastapi')
#api_address = 'fastapi'
# API port
api_port = int(os.getenv('API_PORT', default='8000'))
#api_port = '8000'

title = "Prédictions de données météorologiques en Australie"
sidebar_name = "Administration"


def login():
    """
    This function manages administrator login.
    """
    user = st.text_input("Utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Login"):
        try:
            url = 'http://{address}:{port}/token'
            response = requests.post(
                url=url.format(address=api_address, port=api_port),
                data={"username": user, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                st.session_state.token = token
                st.success("Accès accordé !")
                # Utilisation de st.rerun() au lieu de st.experimental_rerun()
                st.rerun()
            else:
                st.error("Utilisateur ou mot de passe invalide.")
        except Exception as e:
            st.error(f"Exception lors du Login : {e}.")

    return False


def train():
    """
    This function trains the model.
    """
    if "token" in st.session_state:
        try:
            url = 'http://{address}:{port}/admin/refresh'
            response = requests.post(
                url=url.format(address=api_address, port=api_port),
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            if response.status_code == 200:
                st.success("Récupération des dernières données "
                           "et entraînement démarré !")
            else:
                st.error("L'opération a échoué :-(")
        except Exception as e:
            st.error(f"Exception durant l'opération : {e}")
    else:
        st.error("Vous devez être identifié pour lancer l'opération.")


def run():

    st.title(title)

    st.divider()

    st.subheader("Objectif")

    st.markdown("Gérer l'entraînement du modèle.")

    st.divider()

    st.subheader("Formulaire")

    if "token" in st.session_state:
        st.success("Vous êtes identifié !")

        if st.button("Entraîner le modèle"):
            train()
    else:
        st.info("Veuillez vous indentifier pour accèder "
                "à la fonctionnalité d'administrateur.")
        login()
