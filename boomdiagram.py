import matplotlib.pyplot as plt
import networkx as nx

def teken_boomdiagram(
        keuzes,
        x_step=3,
        bundel_hoogte=3,
        spreiding=0.8,
        marge_links=0.3,
        marge_rechts=0.3,
        padlabel_marge=1.2,
        figure_size=(14, 7),
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

    # ---------- PLOT ----------
    plt.figure(figsize=figure_size)

    nx.draw(G, pos, with_labels=False, node_size=0, arrows=False)

    # Staplabels
    for node_id, (x, y) in text_pos.items():
        plt.text(
            x, y,
            text_labels.get(node_id, node_id),
            ha="right" if node_id == "Start" else "left",
            va="center",
            fontsize=11
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
            fontsize=10,
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
