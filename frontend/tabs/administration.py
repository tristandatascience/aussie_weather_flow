"""
Administration Tab
"""

import streamlit as st

title = "Prédictions de données météorologiques en Australie"
sidebar_name = "Administration"


def run():

    st.title(title)

    st.divider()

    st.subheader("Objectif")

    st.markdown("Gérer l'entraînement du modèle.")

    st.divider()

    st.subheader("Accès")

    login = st.text_input(label="Utilisateur")
    password = st.text_input(label="Mot de passe",
                             type="password")
    st.write(login, password)

    st.divider()

    st.subheader("Formulaire")

    if st.button(label="Push me !"):
        st.write("Entraînement en cours !")
