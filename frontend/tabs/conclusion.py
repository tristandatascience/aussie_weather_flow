"""
Conclusion Tab
"""

import streamlit as st

title = "Prédictions de données météorologiques en Australie"
sidebar_name = "Conclusion"


def run():

    st.title(title)

    st.divider()

    st.subheader("Conclusion")

    st.markdown(
        """
        Evolutions envisagées :

        - Sécuriser le système avec la mise en oeuvre de SSL/TLS.
        - Mettre des liens vers les différentes interfaces web des outils  
          MLflow, Airflow, Prometheus, Grafana.
        - Utiliser plusieurs modèles différents et sélectionner
          automatiquement le meilleur.
        - Intégrer les métriques pour surveiller la performance des modèles.
        - Intégrer l'application de prédiction météo aux autres systèmes
          de l'Hôpital via l'API fournie.
        - ...
        """
    )

