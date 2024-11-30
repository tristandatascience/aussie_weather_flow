"""
Project introduction Tab
"""

import streamlit as st

title = "Prédictions de données météorologiques en Australie"
sidebar_name = "Introduction"


def run():

    st.image(image="assets/climat_carte.png",
             use_container_width=True)

    st.title(title)

    st.markdown("---")

    st.markdown(
        """
        Etude menée par :

        - Shirley Gervolino
        - Tristan Lozahic
        - Prudence Amani
        - Stéphane Los

        Données gouvernementales collectées par 49 stations météorologiques
        réparties sur tout le territoire australien.

        Mesures quotidiennes sur la période 2008/2017.

        Données incluant les relevés de température, pression atmosphérique,
        pluviométrie, vents ou encore taux d'ensoleillement (16 features).

        Mise à jour par scrapping.
        """
    )

    st.subheader("Objectif")

    st.markdown("Pour le lendemain, prédire s'il pleuvra ou non.")
