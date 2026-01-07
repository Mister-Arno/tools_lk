import matplotlib.pyplot as plt
import networkx as nx
from fractions import Fraction

def teken_boom(
        keuzes,
        kansen=None,  # Kansen kunnen optioneel zijn voor de kansboom
        x_step=3,
        bundel_hoogte=1.7,
        spreiding=0.8,
        marge_links=0.3,
        marge_rechts=0.3,
        padlabel_marge=1.2,
        toon_breuken=True,  # Optioneel om breuken te tonen
        toon_eindkans=True,  # Optioneel om de kans van de eindtak te tonen
        save_path=None
):
    """
    Tekent een boomdiagram of kansboom, afhankelijk van de aanwezigheid van kansen.

    keuzes  = [["S","L"], ["V","K"], ["I","C"]]
    kansen  = [[0.5,0.5], [0.4,0.6], [0.3,0.7]] (optioneel, alleen nodig voor kansboom)
    toon_breuken = True/False (of kansen als breuken of decimalen tonen)
    toon_eindkans = True/False (om kans van de eindtakken te tonen)
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
    if kansen and len(keuzes) != len(kansen):
        raise ValueError("Aantal keuzelagen en kanslagen moet gelijk zijn.")

    if kansen:
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
    for stap, (opties) in enumerate(keuzes, start=1):
        nieuwe_knopen = []
        x = stap * x_step
        y_basis = bundel_hoogte * (len(huidige_knopen) - 1) / 2

        for i, vorige in enumerate(huidige_knopen):
            y0 = y_basis - i * bundel_hoogte

            offsets = [
                ((len(opties) - 1) / 2 - j) * spreiding
                for j in range(len(opties))
            ]

            for j, keuze in enumerate(opties):
                node_id = f"{vorige}|{keuze}|{stap}"

                text_labels[node_id] = keuze
                paden[node_id] = paden[vorige] + [keuze]

                # Als kansen gegeven zijn, bereken de kans van het pad
                if kansen:
                    kans = kansen[stap - 1][j]
                    kans_paden[node_id] = kans_paden[vorige] * kans
                    kans_str = format_kans(kans, toon_breuken)
                else:
                    kans_paden[node_id] = 1
                    kans_str = ""

                y = y0 + offsets[j]

                text_pos[node_id] = (x, y)
                pos[f"{node_id}_in"] = (x - marge_links, y)
                pos[f"{node_id}_out"] = (x + marge_rechts, y)

                # Voeg de kans als label toe aan de verbinding
                G.add_edge(f"{vorige}_out", f"{node_id}_in", label=kans_str)

                nieuwe_knopen.append(node_id)

        huidige_knopen = nieuwe_knopen

    # ---------- DYNAMISCHE FIGUURGROOTTE ----------
    # Bereken de breedte en hoogte op basis van het aantal keuzes en takken
    aantal_keuzes = len(keuzes)
    aantal_takken = max(len(opties) for opties in keuzes)
    breedte = aantal_keuzes * x_step + 2
    hoogte = max(3, len(huidige_knopen) * bundel_hoogte)

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

    # Kanslabels op pijlen als het een kansboom is
    if kansen:
        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)

    # Padlabels + eindkans
    for node_id in huidige_knopen:
        x, y = text_pos[node_id]
        pad = ", ".join(paden[node_id])
        totale_kans = round(kans_paden[node_id], 4)

        # Toon kans alleen als gevraagd
        if toon_eindkans:
            plt.text(
                x + padlabel_marge, y,
                f"({pad})  P = {totale_kans}",
                ha="left",
                va="center",
                fontsize=14,
                style="italic"
            )
        else:
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
    plt.xlim(min(xs) - 1.5, max(xs) + 3)
    plt.ylim(min(ys) - 1.5, max(ys) + 1.5)

    plt.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return plt


def teken_boom_permutatie(
        keuzes,
        r=None,
        kans_functie=None,     # callable(remaining, keuze, stap, pad) -> float in [0,1]
        x_step=3,
        bundel_hoogte=1.7,
        spreiding=0.8,
        marge_links=0.3,
        marge_rechts=0.3,
        padlabel_marge=1.2,
        save_path=None
):
    """
    Tekent een permutatieboom (zonder terugleggen) op basis van een startpool.

    Voorbeeld:
        teken_boom_permutatie(["A","B","C","D"], r=3)
        => 4 takken in stap1, 3 in stap2, 2 in stap3

    kansen:
        - "uniform": elke keuze aan een knoop heeft kans 1/len(remaining)
        - None: geen kanslabels en geen eindkansen
    kans_functie:
        - als je niet-uniforme kansen wilt per knoop (overrulet 'kansen')
    """
    print(keuzes)
    print(r)

    # --------- CONTROLES ----------
    keuzes = list(keuzes)
    if len(set(keuzes)) != len(keuzes):
        # Niet verboden, maar dan "zonder terugleggen" op waarde werkt ambigu.
        # Oplossing: maak labels uniek (bv. ("A",0), ("A",1)) of geef unieke strings.
        raise ValueError("Pool bevat dubbels. Maak items uniek (bv. 'A1','A2') of gebruik unieke tuples.")

    n = len(keuzes)
    if r is None:
        r = n
    if not (0 <= r <= n):
        raise ValueError(f"r moet tussen 0 en {n} liggen (kreeg r={r}).")

    # ---------- START ----------
    G = nx.DiGraph()
    pos = {}
    text_pos = {}
    text_labels = {}
    paden = {}
    kans_paden = {}

    text_pos["Start"] = (0, 0)
    text_labels["Start"] = "Start"
    pos["Start_out"] = (marge_rechts, 0)
    paden["Start"] = []
    kans_paden["Start"] = 1.0

    huidige_knopen = ["Start"]

    # ---------- STAPPEN ----------
    for stap in range(1, r + 1):
        nieuwe_knopen = []
        x = stap * x_step
        y_basis = bundel_hoogte * (len(huidige_knopen) - 1) / 2

        for i, vorige in enumerate(huidige_knopen):
            y0 = y_basis - i * bundel_hoogte
            pad_tot_nu = paden[vorige]

            remaining = [item for item in keuzes if item not in pad_tot_nu]
            if not remaining:
                continue

            offsets = [((len(remaining) - 1) / 2 - j) * spreiding for j in range(len(remaining))]

            for j, keuze in enumerate(remaining):
                node_id = f"{vorige}|{keuze}|{stap}"

                text_labels[node_id] = str(keuze)
                paden[node_id] = pad_tot_nu + [keuze]



                y = y0 + offsets[j]

                text_pos[node_id] = (x, y)
                pos[f"{node_id}_in"] = (x - marge_links, y)
                pos[f"{node_id}_out"] = (x + marge_rechts, y)

                G.add_edge(f"{vorige}_out", f"{node_id}_in")
                nieuwe_knopen.append(node_id)

        huidige_knopen = nieuwe_knopen

    # ---------- FIGUURGROOTTE ----------
    breedte = r * x_step + 2
    hoogte = max(3, len(huidige_knopen) * bundel_hoogte)
    plt.figure(figsize=(breedte, hoogte))

    # ---------- PLOT ----------
    nx.draw(G, pos, with_labels=False, node_size=0, arrows=False)

    for node_id, (xx, yy) in text_pos.items():
        plt.text(
            xx, yy,
            text_labels.get(node_id, node_id),
            ha="right" if node_id == "Start" else "left",
            va="center",
            fontsize=14
        )

    for node_id in huidige_knopen:
        xx, yy = text_pos[node_id]
        pad = ", ".join(map(str, paden[node_id]))
        tekst = f"({pad})"

        plt.text(
            xx + padlabel_marge, yy,
            tekst,
            ha="left",
            va="center",
            fontsize=14,
            style="italic"
        )

    xs = [xx for xx, _ in text_pos.values()]
    ys = [yy for _, yy in text_pos.values()]
    plt.xlim(min(xs) - 1.5, max(xs) + 3)
    plt.ylim(min(ys) - 1.5, max(ys) + 1.5)

    plt.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return plt

if __name__ == "__main__":
    keuzes_perm = ["A", "B", "C"]
    teken_boom_permutatie(keuzes_perm, r=3)
    plt.show()