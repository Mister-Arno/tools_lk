import streamlit as st
import importlib
from boomdiagram import teken_boom
from veeltermen import derdegraad_benadering, vierdegraad_benadering
import tempfile
import os
import urllib.parse
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Tools voor leerkrachten")

tool = st.sidebar.radio(
    "Kies een tool:",
    ["Boomdiagram (telproblemen)", "Boomdiagram (kansboom)", "Functie met gehele extrema generator"]
)

# ================= BOOMDIAGRAM TOOL =================
if tool == "Boomdiagram (telproblemen)":
    st.subheader("Boomdiagram generator voor telproblemen")

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

        plt_obj = teken_boom(
            keuzes=stappen,
            bundel_hoogte=bundel_hoogte,  # Gebruik de sliderwaarde voor de ruimte binnen bundels
            spreiding=verticale_spreiding,  # Gebruik de sliderwaarde voor verticale spreiding
            save_path=pad,
            toon_eindkans=False
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
    st.subheader("Kansboom generator")
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

            teken_boom(
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

if tool == "Functie met gehele extrema generator":
    st.subheader("De grafiek van een veelterm met gehele coördinaten")

    st.markdown("""
    **Zelf een voorschrift zoeken van een veeltermfunctie met gehele extrema EN nulpunten is lastig.
    Deze tool benadert dit probleem door zo'n grafiek na te bootsen met meerdere parabolen.**
    """)

    # 1) Graadkeuze
    graad = st.radio(
        "Kies de graad van de functie (enkel gelijkenis qua aantal kronkels)",
        [3, 4],
        horizontal=True
    )

    # 2) Aantal voorschriften
    aantal = st.number_input(
        "Aantal functies dat gegenereerd moet worden",
        min_value=1,
        max_value=50,
        value=10,
        step=1
    )

    x_window = st.number_input(
        "De grenzen van x waartussen alle nulpunten en extrema liggen",
        min_value=5,
        max_value=50,
        value=10,
        step=1
    )

    y_window = st.number_input(
        "De grenzen van y waartussen alle nulpunten en extrema liggen",
        min_value=5,
        max_value=50,
        value=10,
        step=1
    )

    samenvallend = None
    if graad == 3:
        samenvallend = st.checkbox(
            "Asymmetrie (y-waarden van de extrema niet tegengesteld)",
            value=True
        )
    else:
        assert graad == 4
        st.markdown("""
        De functie zal niet de symmetrie hebben van een vierdegraadsfunctie.
        """)

    if st.button("Genereer stuksgewijze voorschriften"):
        resultaten = []

        for _ in range(aantal):
            try:
                if graad == 3:
                    res = derdegraad_benadering(
                        extrema_y_symmetry= not samenvallend,
                        x_bound=x_window,
                        y_bound=y_window
                    )
                else:
                    assert graad == 4
                    res = vierdegraad_benadering(x_bound=x_window,
                                                 y_bound=y_window)

                resultaten.append(res["rule"])
            except:
                pass

        if len(resultaten) == 0:
            st.error("Er konden geen geldige functies gegenereerd worden.")
        else:
            st.success(f"{len(resultaten)} functies gegenereerd.")

            st.markdown("### GeoGebra-voorschriften:")
            st.markdown("""
            **De functie is stuksgewijs gedefinieerd als een aantal parabolen. Klik op de knop om te openen in Geogebra of kopieer het voorschrift.**
            """)

            style_cmds = [
                "SetColor(f,0,0,0)",
                "SetLineThickness(f,7)",
                "SetAxesLabelStyle(1)",
                "SetFontSize(32)",
                "SetGrid(true)",
                "SetGridType(2)"
            ]

            for i, regel in enumerate(resultaten, start=1):
                regel2 = regel + ";" + ";".join(style_cmds)


                encoded = urllib.parse.quote(regel2)
                geogebra_url = f"https://www.geogebra.org/graphing?command={encoded}"

                col_knop, col_tekst = st.columns([0.5, 9.5])
                with col_knop:
                    st.markdown(
                        f"[▶ Open]({geogebra_url})",
                        unsafe_allow_html=True
                    )
                with col_tekst:
                    st.code(f"{i}. {regel}")

            # Optioneel: alles in één kopieerbaar tekstblok
            alles = "\n".join(resultaten)

            st.download_button(
                "Download als tekstbestand",
                alles,
                file_name="stuksgewijze_functies.txt"
            )

