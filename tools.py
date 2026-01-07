import streamlit as st

from Leerkracht.tools_lk.boomdiagram import teken_boom_permutatie
from boomdiagram import teken_boom
from veeltermen import derdegraad_benadering, vierdegraad_benadering
import tempfile
import os
import urllib.parse
from collections import defaultdict, Counter
from klasplaatsen2 import SeatingGenerator, map_to_layout2
import random
import argparse
import streamlit.components.v1 as components

if os.getenv("ENV", "").lower() == "local":
    base_url = 'http://localhost:8501/'
else:
    base_url = "https://toolslk-nujuxf6gqh9jqe89efkmip.streamlit.app/"

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; font-size: 40px; color: #555;'>"
    "🔧 Tools voor leerkrachten"
    "</div>",
    unsafe_allow_html=True
)


# ---- breid de radioknop uit (eerste voorkomen in je script) ------------
# --- Tools en structuur ---
# --- Tools en structuur ---
# ================= TOOL SELECTIE (STABIEL) =================

tool_dict = {
    "Klasbeheer": ["Klasplaatsen generator"],
    "Boomdiagrammen": ["Boomdiagram (telproblemen)", "Boomdiagram permutatie(telproblemen)", "Boomdiagram (kansboom)"],
    "Functies": ["Functie met gehele extrema generator"],
}

# URL-params (optioneel, veilig)
params = st.query_params
cat_param = params.get("categorie")
tool_param = params.get("tool")

# --- CATEGORIE ---
categorieën = list(tool_dict.keys())
if cat_param in tool_dict:
    categorie = st.sidebar.selectbox(
        "Categorie",
        categorieën,
        index=categorieën.index(cat_param)
    )
else:
    categorie = st.sidebar.selectbox("Categorie", categorieën)

# --- TOOL ---
tools_in_cat = tool_dict[categorie]

if tool_param in tools_in_cat:
    tool = st.sidebar.radio(
        "Tool",
        tools_in_cat,
        index=tools_in_cat.index(tool_param)
    )
else:
    tool = st.sidebar.radio("Tool", tools_in_cat)


# Bouw zelf de URL op
categorie_encoded = urllib.parse.quote(categorie)
tool_encoded = urllib.parse.quote(tool)

# ================= BOOMDIAGRAM TOOL =================
if tool == "Boomdiagram (telproblemen)":
    st.subheader("Boomdiagram generator voor telproblemen")
    deelbare_link = f"{base_url}?categorie=Boomdiagrammen&tool=Boomdiagram%20(telproblemen)"
    st.markdown(f"**Link om te delen:** [`{deelbare_link}`]({deelbare_link})")


    st.markdown("""
    **Deze tool maakt een boomdiagram afbeelding op basis van de keuzes die je opgeeft per stap.**
    Maak hiermee snel een professionele afbeelding voor op een toets of taak.
    """)

    st.markdown("""
    **Geef de keuzes stap per stap**
    - **Elke regel** is één stap in het boomdiagram
    - Scheid keuzes binnen een stap met een komma
    """)

    stappen_tekst = st.text_area(
        "Keuzes per stap",
        "S, L\nV, K\nI, C"
    )

    st.markdown("""
    Pas de volgende schuifknoppen aan als de takken te dicht of te ver opeen staan.
    """)

    # Toegevoegde slider voor bundel_hoogte
    bundel_hoogte = st.slider("Verticale ruimte tussen takken van verschillende bundels", min_value=0.0, max_value=6.0, value=1.0, step=0.2)

    # Toegevoegde slider voor verticale spreiding binnen de bundel
    verticale_spreiding = st.slider("Verticale spreiding tussen takken binnenin een bundel", min_value=0.0, max_value=6.0, value=0.4, step=0.2)

    if st.button("Genereer boomdiagram"):
        st.info(f"Diagram wordt hieronder getoond")
        stappen = [
            [x.strip() for x in lijn.split(",")]
            for lijn in stappen_tekst.strip().splitlines()
            if lijn.strip()
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

if tool == "Boomdiagram permutatie(telproblemen)":
    st.subheader("Boomdiagram generator voor permutatie(telproblemen)")
    deelbare_link = f"{base_url}?categorie=Boomdiagrammen&tool=Boomdiagram%20permutatie(telproblemen)"
    st.markdown(f"**Link om te delen:** [`{deelbare_link}`]({deelbare_link})")
    st.markdown("""
    **Deze tool maakt een boomdiagram afbeelding op basis van de keuzes die je opgeeft per stap, met permutaties.**
    Maak hiermee snel een professionele afbeelding voor op een toets of taak.
    """)

    st.markdown("""
    **Geef de keuzes die gepermuteerd moeten worden.**
    - Scheid keuzes met een komma
    """)
    stappen_tekst = st.text_input(
        "Keuzes om te permuteren. Geen duplicaten toegestaan.",
        "A, B, C"
    )

    st.markdown("""
    Pas de volgende schuifknoppen aan als de takken te dicht of te ver opeen staan.
    """)

    # Toegevoegde slider voor bundel_hoogte
    bundel_hoogte = st.slider("Verticale ruimte tussen takken van verschillende bundels", min_value=0.0, max_value=6.0, value=1.0, step=0.2)

    # Toegevoegde slider voor verticale spreiding binnen de bundel
    verticale_spreiding = st.slider("Verticale spreiding tussen takken binnenin een bundel", min_value=0.0, max_value=6.0, value=0.4, step=0.2)

    if st.button("Genereer boomdiagram"):
        st.info(f"Diagram wordt hieronder getoond")
        keuzes = [x.strip() for x in stappen_tekst.strip().split(",") if x.strip()]
        n = len(keuzes)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            pad = tmp.name

        plt_obj = teken_boom_permutatie(
            keuzes=keuzes,
            r=n,
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
    st.subheader("Kansboom generator")
    deelbare_link = f"{base_url}?categorie=Boomdiagrammen&tool=Boomdiagram%20(kansboom)"
    st.markdown(f"**Link om te delen:** [`{deelbare_link}`]({deelbare_link})")

    st.markdown("""
    **Deze tool maakt een kansboom afbeelding op basis van de keuzes die je opgeeft per stap.**
    Maak hiermee snel een professionele afbeelding voor op een toets of taak.
    """)

    st.markdown("""
    **Geef de keuzes stap per stap**
    - **Elke regel** is één stap in het boomdiagram
    - Scheid keuzes binnen een stap met een komma
    """)

    stappen_tekst = st.text_area(
        "Keuzes per stap",
        "S, L\nV, K\nI, C"
    )

    st.markdown("""
    **Geef de kansen stap per stap**
    - Moet exact dezelfde structuur hebben als je hierboven hebt geschreven, maar met getallen ipv tekst.
    - Bij het getal zelf moet je een punt gebruiken ipv een komma
    """)
    kansen_tekst = st.text_area(
        "Kansen per stap",
        "0.5, 0.5\n0.4, 0.6\n0.3, 0.7"
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
        st.info(f"Diagram wordt hieronder getoond")

        keuzes = [
            [x.strip() for x in lijn.split(",")]
            for lijn in stappen_tekst.strip().splitlines()
            if lijn.strip()
        ]

        kansen = [
            [float(x.strip()) for x in lijn.split(",")]
            for lijn in kansen_tekst.strip().splitlines()
            if lijn.strip()
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
                toon_eindkans=toon_eindkans  # Toon kans aan het einde van de takken
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
    deelbare_link = f"{base_url}?categorie=Functies&tool=Functie%20met%20gehele%20extrema%20generator"
    st.markdown(f"**Link om te delen:** [`{deelbare_link}`]({deelbare_link})")


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
        st.info(f"Resultaten worden hieronder getoond")
        resultaten = []

        for _ in range(aantal):
            try:
                if graad == 3:
                    res = derdegraad_benadering(
                        extrema_y_symmetry=not samenvallend,
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

# ================= ZITPLAN-GENERATOR TOOL ===============================
if tool == "Klasplaatsen generator":
    st.subheader("Klasopstellingen generator")
    deelbare_link = f"{base_url}?categorie=Klasbeheer&tool=Klasplaatsen%20generator"
    st.markdown(f"**Link om te delen:** [`{deelbare_link}`]({deelbare_link})")


    st.markdown("### Invoer laden of handmatig invullen")

    invoermethode = st.radio("Kies invoermethode:", ["Zelf invullen", "Uploaden vanuit txt"])

    # Voor-initialisatie
    jongens_txt = meisjes_txt = verboden_txt = solo_txt = back_txt = front_txt = ""

    if invoermethode == "Uploaden vanuit txt":
        uploaded_file = st.file_uploader("Laad een eerder opgeslagen configuratiebestand (.txt)", type=["txt"])

        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
            try:
                blokken = dict(line.split(":", 1) for line in content.splitlines() if ":" in line)
                jongens_txt = blokken.get("jongens", "")
                meisjes_txt = blokken.get("meisjes", "")
                verboden_txt = blokken.get("verboden", "")
                solo_txt = blokken.get("solo", "")
                back_txt = blokken.get("back", "")
                front_txt = blokken.get("front", "")
                st.success("Invoerbestand succesvol geladen.")
            except Exception as e:
                st.error(f"Fout bij inlezen bestand: {e}")
        else:
            st.stop()  # wacht tot er een bestand is

    else:
        # Standaarddata (enkel bij zelf invullen)
        leerlingen = [
            "Lina", "Azra", "Berat", "Marouane", "Marouan",
            "Israe", "Fatimazahra", "Inaya", "Diestelle", "Jérémie",
            "Andy", "Farhad", "Zuzanna", "Arsela", "Mahdi",
        ]
        jongens_std = [n for n in leerlingen if n in {"Berat", "Marouane", "Marouan", "Mahdi", "Jérémie", "Andy", "Farhad"}]
        meisjes_std = [n for n in leerlingen if n not in jongens_std]
        verboden_std = "Marouan, Marouane, Berat\nLina, Diestelle\nFatimazahra, Zuzanna\nAndy, Jérémie"
        solo_std = "Marouan, Israe"
        back_std = "Mahdi"
        front_std = "Marouan, Israe"

        col1, col2 = st.columns(2)
        with col1:
            jongens_txt = st.text_area("Namen ALLE jongens (scheiden met komma)", ", ".join(jongens_std))
        with col2:
            meisjes_txt = st.text_area("Namen ALLE meisjes (scheiden met komma)", ", ".join(meisjes_std))

        verboden_txt = st.text_area(
            "Groepjes leerlingen die niet bij elkaar mogen.\nScheid leerlingen per groepje met komma's en gebruik voor elk groepje een nieuwe lijn.",
            verboden_std
        )
        solo_txt = st.text_input("(optioneel) Namen die bij voorkeur alleen zitten (scheiden met komma)", solo_std)
        back_txt = st.text_input("(optioneel) Namen die bij voorkeur achteraan zitten (scheiden met komma)", back_std)
        front_txt = st.text_input("(optioneel) Namen die bij voorkeur vooraan zitten (scheiden met komma)", front_std)

        # Voor beide methodes:
        avoid_mixed = st.checkbox("Vermijd duo’s jongen + meisje", value=False)
        n_layouts = 15
        seed = random.randint(1, 10000)
        aantal_pogingen = st.number_input("Aantal combinaties om te proberen (minstens 10000)", min_value=10000, max_value=1000000, value=100000, step=10000)

        # Exportknop

        invoertekst = "\n".join([
            f"jongens:{jongens_txt}\n",
            f"meisjes:{meisjes_txt}\n",
            f"verboden:{verboden_txt}\n",
            f"solo:{solo_txt}\n",
            f"back:{back_txt}\n",
            f"front:{front_txt}\n"
        ])
        st.markdown("""
            Je kan je instellingen eventueel downloaden zodat je de volgende keer hieruit kan kopiëren. Dan moet je alle namen niet meer intypen.
            """)
        st.download_button("Download deze gegevens als txt (voor de volgende keer)", invoertekst, file_name="zitplan_invoer.txt", mime="text/plain")
        st.markdown("""
            Klik hier om de klasplaatsen te genereren.
            """)

        if st.button("Genereer klasplaatsen"):
            # ----- parsing ---------------------------------------------------
            boys = [x.strip() for x in jongens_txt.split(",") if x.strip()]
            girls = [x.strip() for x in meisjes_txt.split(",") if x.strip()]
            names = boys + girls

            # duplicates?
            dupes = [n for n, cnt in Counter(names).items() if cnt > 1]
            if dupes:
                st.error(f"Dubbele namen in leerlingenlijst. Zorg dat elke naam uniek is (bv afkorting achternaam toevoegen): {', '.join(dupes)}")
                st.stop()


            # helper om losse lijsten te maken
            def split_csv(txt):
                return [x.strip() for x in txt.split(",") if x.strip()]


            def split_groups(txt):
                return [split_csv(line) for line in txt.strip().splitlines() if line.strip()]


            forbidden_groups = split_groups(verboden_txt)
            solo = split_csv(solo_txt)
            back = split_csv(back_txt)
            front = split_csv(front_txt)

            # onbekende namen verzamelen
            unknown = set()
            for lst in forbidden_groups + [solo, back, front]:
                unknown.update([n for n in lst if n not in names])
            if unknown:
                st.error(f"Onbekende namen: {', '.join(sorted(unknown))}")
                st.stop()

            st.info(f"Klas van {len(names)} leerlingen correct ingelezen.\n Er worden {aantal_pogingen} opstellingen gecontroleerd en de "
                    f"beste {n_layouts} worden daarna hieronder getoond.")

            # ===== generator =====
            genders = {n: "M" for n in boys}
            genders.update({n: "V" for n in girls})

            rng = random.Random(int(seed))
            gen = SeatingGenerator(
                names,
                forbidden_groups,
                front_pref=front,
                back_pref=back,
                solo_pref=solo,
                genders=genders,
                avoid_mixed_bank=avoid_mixed,
                rng=rng,
                max_attempts=aantal_pogingen   # evt. groter
            )

            # voortgangsbalk
            progress = st.progress(0.0)
            best = []
            seats = gen.seats1.copy()
            for attempt in range(gen.max_attempts):
                rng.shuffle(seats)
                assign = {}
                if gen._place_recursive(0, seats, assign):
                    score, missing = gen._evaluate(assign)
                    best.append((assign.copy(), score, missing))
                    best.sort(key=lambda x: x[1], reverse=True)
                    best = best[: int(n_layouts)]
                    if len(best) >= n_layouts and all(miss == [] for _,_,miss in best):
                        break

                if attempt % (gen.max_attempts // 1000) == 0:
                    progress.progress((attempt + 1) / gen.max_attempts)
            progress.empty()

            if not best:
                st.error("Geen enkele geldige opstelling gevonden.")
                st.stop()

            # ===== helper voor ascii-print =====
            def layout_to_str(assignment, seats):
                banks = defaultdict(list)
                for seat, name in assignment.items():
                    banks[(seat[0], seat[1])].append((seat[2], name))
                max_row = max(r for r, _, _ in seats)
                max_col = max(c for _, c, _ in seats)

                rtn = "\n".join(
                    " ".join(
                        f"{'/'.join(n for _, n in sorted(banks.get((r, c), []))):^16}" if banks.get((r, c))
                        else "----".center(16)
                        for c in range(max_col + 1)
                    ) for r in range(max_row + 1)
                )
                rtn += "\n\n VOORKANT LOKAAL HIER"
                return rtn


            # ===== output =====
            for i, (assign, sc, miss) in enumerate(best, 1):
                st.markdown(f"### Optie {i} — score {sc}")
                if miss:
                    st.warning("Niet aan voorwaarden voldaan: "+ ", ".join(miss))
                else:
                    st.success("Alle voorkeuren voldaan!")
                st.text("Opstelling 1: lokaal met 4 rijen.")
                st.code(layout_to_str(assign, gen.seats1))
                st.text("Opstelling 2: lokaal met 3 rijen. (laatste rij van opstelling 1 werd rechts gezet)")
                st.code(layout_to_str({map_to_layout2(s): n for s, n in assign.items()}, gen.seats2))
                st.divider()


st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; color: grey;'>"
    "Gemaakt door den Arno — Laatste update: 2026-01-07"
    "</div>",
    unsafe_allow_html=True
)

if __name__ == "__main__":
    pass