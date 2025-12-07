import streamlit as st
import importlib
from boomdiagram import teken_boomdiagram

import tempfile
import os

st.set_page_config(layout="wide")

st.title("Boomdiagram maker (telproblemen)")

tool = st.sidebar.radio(
    "Kies een tool:",
    ["Boomdiagram"]
)

# ================= BOOMDIAGRAM TOOL =================
if tool == "Boomdiagram":
    st.markdown("""
    **Deze tool maakt een boomdiagram op basis van de keuzes die je opgeeft per stap.**
    """)

    #st.subheader("Stappen en keuzes")

    st.markdown("""
    **Geef de keuzes stap per stap**
    
    - Scheid de stappen met een `|` (verticale streep)
    - Scheid keuzes met een `,` (komma)
    - Voorbeeld: een restaurant met voorgerecht S of L, hoofdgerecht V of K, en nagerecht I of C:
    `S,L | V,K | I,C`  
    """)

    stappen_tekst = st.text_area(
        "Invoer",
        "S,L | V,K | I,C"
    )


    if st.button("Genereer boomdiagram"):

        stappen = [
            [x.strip() for x in deel.split(",")]
            for deel in stappen_tekst.split("|")
        ]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            pad = tmp.name

        plt_obj = teken_boomdiagram(
            keuzes=stappen,
            save_path=pad
        )

        st.image(pad)

        with open(pad, "rb") as f:
            st.download_button(
                "Download als afbeelding",
                f,
                file_name="boomdiagram.png"
            )

        os.remove(pad)