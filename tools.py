import streamlit as st
import importlib
from boomdiagram import teken_boomdiagram, teken_kansboom
import tempfile
import os

st.set_page_config(layout="wide")

st.title("Boomdiagram maker (telproblemen)")

tool = st.sidebar.radio(
    "Kies een tool:",
    ["Boomdiagram (telproblemen)", "Boomdiagram (kansboom)"]
)

# ================= BOOMDIAGRAM TOOL =================
if tool == "Boomdiagram (telproblemen)":

    st.markdown("""
    **Deze tool maakt een boomdiagram afbeelding op basis van de keuzes die je opgeeft per stap.**
    Maak hiermee snel een professionele afbeelding voor op een toets of taak.
    """)

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

    st.markdown("""
    Pas de volgende schuifknoppen aan als de takken te dicht of te ver opeen staan.
    """)

    # Toegevoegde slider voor bundel_hoogte
    bundel_hoogte = st.slider("Verticale ruimte tussen takken van verschillende bundels", min_value=0.0, max_value=6.0, value=1.0, step=0.2)

    # Toegevoegde slider voor verticale spreiding binnen de bundel
    verticale_spreiding = st.slider("Verticale spreiding tussen takken binnenin een bundel", min_value=0.0, max_value=6.0, value=0.4, step=0.2)

    if st.button("Genereer boomdiagram"):

        stappen = [
            [x.strip() for x in deel.split(",")]
            for deel in stappen_tekst.split("|")
        ]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            pad = tmp.name

        plt_obj = teken_boomdiagram(
            keuzes=stappen,
            bundel_hoogte=bundel_hoogte,  # Gebruik de sliderwaarde voor de ruimte binnen bundels
            spreiding=verticale_spreiding,  # Gebruik de sliderwaarde voor verticale spreiding
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

# ================= KANSBOOM TOOL =================
if tool == "Boomdiagram (kansboom)":

    st.markdown("""
    **Deze tool maakt een kansboom afbeelding op basis van de keuzes die je opgeeft per stap.**
    Maak hiermee snel een professionele afbeelding voor op een toets of taak.
    """)

    st.markdown("""
    **Geef de keuzes stap per stap en bijbehorende kansen** 
    - Scheid de stappen met een `|` (verticale streep)
    - Scheid keuzes met een `,` (komma)
    - Geef de kansen per stap in dezelfde volgorde en structuur als de keuzes
    - Bijvoorbeeld:  
      Keuzes: `S,L | V,K | I,C`  
      Kansen:  `0.5,0.5 | 0.4,0.6 | 0.3,0.7`
    """)

    stappen_tekst = st.text_area(
        "Keuzes per stap",
        "S,L | V,K | I,C"
    )

    kansen_tekst = st.text_area(
        "Kansen per stap",
        "0.5,0.5 | 0.4,0.6 | 0.3,0.7"
    )

    toon_breuken = st.checkbox("Toon kansen als breuken", value=False)

    # Toegevoegde checkbox voor het tonen van de kans aan het einde
    toon_eindkans = st.checkbox("Toon de kans van de tak achteraan de tak", value=True)

    st.markdown("""
    Pas de volgende schuifknoppen aan als de takken te dicht of te ver opeen staan.
    """)

    # Toegevoegde slider voor bundel_hoogte
    bundel_hoogte = st.slider("Verticale ruimte tussen takken van verschillende bundels", min_value=0.0, max_value=6.0, value=1.0, step=0.2)

    # Toegevoegde slider voor verticale spreiding binnen de bundel
    verticale_spreiding = st.slider("Verticale spreiding tussen takken binnenin een bundel", min_value=0.0, max_value=6.0, value=0.4, step=0.2)

    if st.button("Genereer kansboom"):

        keuzes = [
            [x.strip() for x in deel.split(",")]
            for deel in stappen_tekst.split("|")
        ]

        kansen = [
            [float(x.strip()) for x in deel.split(",")]
            for deel in kansen_tekst.split("|")
        ]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            pad = tmp.name

        try:
            teken_kansboom(
                keuzes=keuzes,
                kansen=kansen,
                bundel_hoogte=bundel_hoogte,  # Gebruik de sliderwaarde voor de ruimte binnen bundels
                spreiding=verticale_spreiding,  # Gebruik de sliderwaarde voor verticale spreiding
                save_path=pad,
                toon_breuken=toon_breuken,
                toon_eindkans = toon_eindkans  # Toon kans aan het einde van de takken
            )

            st.image(pad)

            with open(pad, "rb") as f:
                st.download_button(
                    "Download kansboom",
                    f,
                    file_name="kansboom.png"
                )

        except Exception as e:
            st.error(f"Fout in invoer: {e}")

        os.remove(pad)
