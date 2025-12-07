import matplotlib.pyplot as plt
import networkx as nx
from fractions import Fraction

import matplotlib.pyplot as plt
import networkx as nx
from fractions import Fraction

def teken_boomdiagram(
        keuzes,
        x_step=3,
        bundel_hoogte=1.7,
        spreiding=0.8,
        marge_links=0.3,
        marge_rechts=0.3,
        padlabel_marge=1.2,
        save_path=None
):
    """
    Tekent een flexibel boomdiagram op basis van een lijst van keuzelijsten.
    keuzes = [["S","L"], ["V","K"], ["I","C"]]
    """

    G = nx.DiGraph()
    pos = {}
    text_pos = {}
    text_labels = {}
    paden = {}

    # ---------- START ----------
    text_pos["Start"] = (0, 0)
    text_labels["Start"] = "Start"
    pos["Start_out"] = (marge_rechts, 0)
    paden["Start"] = []

    huidige_knopen = ["Start"]

    # ---------- STAPPEN ----------
    for stap, opties in enumerate(keuzes, start=1):
        nieuwe_knopen = []
        x = stap * x_step

        y_basis = bundel_hoogte * (len(huidige_knopen) - 1) / 2

        for i, vorige in enumerate(huidige_knopen):
            y0 = y_basis - i * bundel_hoogte

            offsets = [
                ((len(opties) - 1) / 2 - j) * spreiding
                for j in range(len(opties))
            ]

            for keuze, offset in zip(opties, offsets):
                node_id = f"{vorige}|{keuze}|{stap}"

                text_labels[node_id] = keuze
                paden[node_id] = paden[vorige] + [keuze]

                y = y0 + offset

                text_pos[node_id] = (x, y)
                pos[f"{node_id}_in"] = (x - marge_links, y)
                pos[f"{node_id}_out"] = (x + marge_rechts, y)

                G.add_edge(f"{vorige}_out", f"{node_id}_in")
                nieuwe_knopen.append(node_id)

        huidige_knopen = nieuwe_knopen

    # ---------- DYNAMISCHE FIGUURGROOTTE ----------
    # Bereken de breedte en hoogte op basis van het aantal keuzes en takken
    aantal_keuzes = len(keuzes)
    aantal_takken = max(len(opties) for opties in keuzes)

    breedte = aantal_keuzes * x_step + 2  # Breedte per keuze, kan worden aangepast
    hoogte = max(3, len(huidige_knopen) * bundel_hoogte)  # Hoogte per tak, schaal op basis van bundel_hoogte

    print(f"Hoogte van de afbeelding: {hoogte}, Breedte: {breedte}")

    # Maak de figuur met de dynamisch berekende grootte
    plt.figure(figsize=(breedte, hoogte))

    # ---------- PLOT ----------
    nx.draw(G, pos, with_labels=False, node_size=0, arrows=False)

    # Labels knopen
    for node_id, (x, y) in text_pos.items():
        plt.text(
            x, y,
            text_labels.get(node_id, node_id),
            ha="right" if node_id == "Start" else "left",
            va="center",
            fontsize=14
        )

    # Padlabels achter eindtakken
    for node_id in huidige_knopen:
        x, y = text_pos[node_id]
        pad = ", ".join(paden[node_id])
        plt.text(
            x + padlabel_marge, y,
            f"({pad})",
            ha="left",
            va="center",
            fontsize=14,
            style="italic"
        )

    # Marges automatisch
    xs = [x for x, _ in text_pos.values()]
    ys = [y for _, y in text_pos.values()]
    plt.xlim(min(xs) - 1.5, max(xs) + 2.5)
    plt.ylim(min(ys) - 1.5, max(ys) + 1.5)

    plt.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return plt



def teken_kansboom(
        keuzes,
        kansen,
        x_step=3,
        bundel_hoogte=1.7,
        spreiding=0.8,
        marge_links=0.3,
        marge_rechts=0.3,
        padlabel_marge=1.2,
        figure_size=(14, 10),  # Verwijderd, we berekenen het dynamisch
        save_path=None,
        toon_breuken=True,
        toon_eindkans=True
):
    """
    keuzes  = [["S","L"], ["V","K"], ["I","C"]]
    kansen  = [[0.5,0.5], [0.4,0.6], [0.3,0.7]]
    toon_breuken = True/False (of kansen als breuken of decimalen tonen)
    """

    # Functie om kansen als breuk of decimaal weer te geven
    def format_kans(kans, toon_breuken):
        if toon_breuken:
            return str(Fraction(kans).limit_denominator(100))  # Weergave als breuk
        else:
            return str(round(kans, 2))  # Weergave als decimaal

    G = nx.DiGraph()
    pos = {}
    text_pos = {}
    text_labels = {}
    paden = {}
    kans_paden = {}

    # --------- CONTROLES ----------
    if len(keuzes) != len(kansen):
        raise ValueError("Aantal keuzelagen en kanslagen moet gelijk zijn.")

    for k in kansen:
        if abs(sum(k) - 1) > 0.01:
            raise ValueError("Kansen per stap moeten samen 1 zijn.")

    # ---------- START ----------
    text_pos["Start"] = (0, 0)
    text_labels["Start"] = "Start"
    pos["Start_out"] = (marge_rechts, 0)

    paden["Start"] = []
    kans_paden["Start"] = 1

    huidige_knopen = ["Start"]

    # ---------- STAPPEN ----------
    for stap, (opties, stapkansen) in enumerate(zip(keuzes, kansen), start=1):
        nieuwe_knopen = []
        x = stap * x_step
        y_basis = bundel_hoogte * (len(huidige_knopen) - 1) / 2

        for i, vorige in enumerate(huidige_knopen):
            y0 = y_basis - i * bundel_hoogte

            offsets = [
                ((len(opties) - 1) / 2 - j) * spreiding
                for j in range(len(opties))
            ]

            for keuze, kans, offset in zip(opties, stapkansen, offsets):
                node_id = f"{vorige}|{keuze}|{stap}"

                text_labels[node_id] = keuze
                paden[node_id] = paden[vorige] + [keuze]
                kans_paden[node_id] = kans_paden[vorige] * kans

                y = y0 + offset
                text_pos[node_id] = (x, y)
                pos[f"{node_id}_in"] = (x - marge_links, y)
                pos[f"{node_id}_out"] = (x + marge_rechts, y)

                # Format kans als breuk of decimaal
                kans_str = format_kans(kans, toon_breuken)

                G.add_edge(
                    f"{vorige}_out",
                    f"{node_id}_in",
                    label=kans_str
                )

                nieuwe_knopen.append(node_id)

        huidige_knopen = nieuwe_knopen

    # ---------- DYNAMISCHE FIGUURGROOTTE ----------
    # Bereken de breedte en hoogte op basis van het aantal keuzes en takken
    aantal_keuzes = len(keuzes)
    aantal_takken = max(len(opties) for opties in keuzes)
    breedte = aantal_keuzes * x_step + 2
    hoogte = max(3, len(huidige_knopen) * bundel_hoogte)
    print(f"Hoogte van de afbeelding: {hoogte}, Breedte: {breedte}")

    # Maak de figuur met de dynamisch berekende grootte
    plt.figure(figsize=(breedte, hoogte))

    # ---------- PLOT ----------
    nx.draw(G, pos, with_labels=False, node_size=0, arrows=False)

    # Labels knopen
    for node_id, (x, y) in text_pos.items():
        plt.text(
            x, y,
            text_labels.get(node_id, node_id),
            ha="right" if node_id == "Start" else "left",
            va="center",
            fontsize=14
        )

    # Kanslabels op pijlen
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)

    # Padlabels + eindkans
    for node_id in huidige_knopen:
        x, y = text_pos[node_id]
        pad = ", ".join(paden[node_id])
        totale_kans = round(kans_paden[node_id], 4)

        plt.text(
            x + padlabel_marge, y,
            f"({pad})  P = {totale_kans}" if toon_eindkans else f"({pad})",
            ha="left",
            va="center",
            fontsize=14,
            style="italic"
        )

    # Marges
    xs = [x for x, _ in text_pos.values()]
    ys = [y for _, y in text_pos.values()]
    plt.xlim(min(xs) - 1.5, max(xs) + 3)
    plt.ylim(min(ys) - 1.5, max(ys) + 1.5)

    plt.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return plt


