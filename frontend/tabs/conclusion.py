"""
Conclusion Tab
"""

import streamlit as st

title = "Prédictions de données météorologiques en Australie"
sidebar_name = "Conclusion"


def run():

    st.title(title)

    st.markdown("---")

    st.markdown(
        """
        Onglet Conclusion
        """
    )

    st.subheader("Objectif")

    st.markdown("Pour le lendemain, prédire s'il pleuvra ou non.")
