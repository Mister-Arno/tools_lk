import random
import math

import random
import math

def derdegraad_benadering(
        x_bound: int = 8,
        y_bound: int = 10,
        extrema_y_symmetry: bool = False,        # ⬅️ beslist OF extrema elkaars tegengestelde zijn
        max_tries: int = 20000,
):

    """
    Genereert een stukgewijze functie met twee parabolen die lijkt op een derdegraadsfunctie.

    - coincident_zeros = True  ⟺  x1 = x3
    - coincident_zeros = False ⟺ x1 ≠ x3
    - force_symmetry = True   ⟺  yv2 = -yv1
    - force_symmetry = False  ⟺  yv2 ≠ -yv1
    """

    xs = list(range(-x_bound, x_bound + 1))
    ys = list(range(-y_bound, y_bound + 1))

    for _ in range(max_tries):

        # ---------- 1. NULPUNTEN ----------
        x2 = random.choice(xs)
        same_parity = [x for x in xs if (x - x2) % 2 == 0 and x != x2]
        if len(same_parity) < 1:
            continue

        if len(same_parity) < 2:
            continue
        x1, x3 = random.sample(same_parity, 2)

        x1, x2, x3 = sorted([x1, x2, x3])


        if abs(x2 - x1) < 2 or abs(x3 - x2) < 2:
            continue

        # ---------- 2. EXTREEM LINKS ----------
        xv1 = (x1 + x2) / 2
        if abs(xv1) > x_bound:
            continue

        denom1 = (xv1 - x1) * (xv1 - x2)
        if abs(denom1) < 1e-9:
            continue

        possible_yv1 = [y for y in ys if y != 0 and abs(y) <= y_bound // 2]
        if not possible_yv1:
            continue

        yv1 = random.choice(possible_yv1)
        a1 = yv1 / denom1

        # ---------- 3. GLAD AANSLUITEN ----------

        if (x2 - x3) == 0:
            continue
        a2 = a1 * (x2 - x1) / (x2 - x3)

        # ---------- 4. EXTREEM RECHTS ----------
        xv2 = (x2 + x3) / 2
        if abs(xv2) > x_bound:
            continue

        yv2 = a2 * (xv2 - x2) * (xv2 - x3)
        if abs(yv2 - round(yv2)) > 1e-9:
            continue
        yv2 = int(round(yv2))

        if abs(yv2) > y_bound:
            continue

        # ---------- 5. S-VORM EN SYMMETRIE ----------
        if yv1 * yv2 > 0:
            continue  # altijd S-vorm

        if extrema_y_symmetry:
            if yv2 != -yv1:
                continue
        else:
            if yv2 == -yv1:
                continue

        # ---------- 6. VERTICALE SHIFT ----------
        possible_shifts = [
            t for t in ys
            if abs(yv1 + t) <= y_bound and abs(yv2 + t) <= y_bound
        ]

        if not possible_shifts:
            continue

        t = random.choice(possible_shifts)

        yv1_s = yv1 + t
        yv2_s = yv2 + t

        # ---------- 7. FUNCTIES ----------
        def P1(x):
            return a1 * (x - x1) * (x - x2) + t

        def P2(x):
            return a2 * (x - x2) * (x - x3) + t

        # ---------- 8. NUMMERIEKE CONTROLE NULPUNTEN ----------
        for xx in [x1, x2, x3]:
            yy = P1(xx) if xx <= x2 else P2(xx)
            if abs(yy) > 1e-6:
                break
        else:
            # ---------- 9. GEO­GEBRA VOORSCHRIFT ----------
            def fmt(c):
                if abs(c - round(c)) < 1e-9:
                    return str(int(round(c)))
                return str(c)

            def term(c):
                c_int = int(round(c))
                if c_int >= 0:
                    return f"(x-{c_int})"
                else:
                    return f"(x+{-c_int})"

            p1_func = f"{fmt(a1)}*{term(x1)}*{term(x2)}"
            if t != 0:
                p1_func += f"+{t}"

            p2_func = f"{fmt(a2)}*{term(x2)}*{term(x3)}"
            if t != 0:
                p2_func += f"+{t}"

            geogebra_rule = f"If[x <= {x2}, {p1_func}, {p2_func}]"

            return {
                "x1": x1, "x2": x2, "x3": x3,
                "xv1": xv1, "yv1": yv1_s,
                "xv2": xv2, "yv2": yv2_s,
                "a1": a1, "a2": a2,
                "y_shift": t,
                "rule": geogebra_rule
            }

    raise RuntimeError("Geen geschikte functie gevonden")

def vierdegraad_benadering(
        x_bound: int = 10,
        y_bound: int = 10,
        max_tries: int = 20000,
):
    """
    Genereert een stukgewijze functie met drie parabolen die lijkt op een vierdegraadsfunctie.
    De functie is C^1 continu (glad) bij de verbindingspunten en heeft gegarandeerd
    vier integer wortels (nulpunten) omdat de verticale shift t = 0 is.
    """

    xs = list(range(-x_bound, x_bound + 1))
    ys = list(range(-y_bound, y_bound + 1))

    # Forceer de verticale shift t = 0
    t = 0

    for _ in range(max_tries):

        # ---------- 1. NULPUNTEN (x1, x2, x3, x4) ----------
        start_x = random.choice(xs)
        # Zorg ervoor dat de nulpunten dezelfde pariteit hebben om xv1, xv2, xv3 integers of half-integers te maken
        same_parity = [x for x in xs if (x - start_x) % 2 == 0]

        if len(same_parity) < 4:
            continue

        x1, x2, x3, x4 = sorted(random.sample(same_parity, 4))

        if not (abs(x2 - x1) >= 2 and abs(x3 - x2) >= 2 and abs(x4 - x3) >= 2):
            continue

        # ---------- 2. EXTREEM LINKS (P1) ----------
        xv1 = (x1 + x2) / 2
        if abs(xv1) > x_bound:
            continue

        denom1 = (xv1 - x1) * (xv1 - x2)
        if abs(denom1) < 1e-9:
            continue

        # yv1 is de y-waarde van het extremum, moet binnen de grenzen vallen
        possible_yv1 = [y for y in ys if y != 0 and abs(y) <= y_bound]
        if not possible_yv1:
            continue

        yv1 = random.choice(possible_yv1)
        a1 = yv1 / denom1

        # ---------- 3. GLAD AANSLUITEN (a2) ----------
        if (x2 - x3) == 0:
            continue
        a2 = a1 * (x2 - x1) / (x2 - x3)

        # ---------- 4. GLAD AANSLUITEN (a3) ----------
        if (x3 - x4) == 0:
            continue
        a3 = a2 * (x3 - x2) / (x3 - x4)

        # ---------- 5. EXTREEM MIDDEN (P2) ----------
        xv2 = (x2 + x3) / 2
        if abs(xv2) > x_bound:
            continue

        yv2 = a2 * (xv2 - x2) * (xv2 - x3)
        if abs(yv2 - round(yv2)) > 1e-9:
            continue
        yv2 = int(round(yv2))

        if abs(yv2) > y_bound:
            continue

        # ---------- 6. EXTREEM RECHTS (P3) ----------
        xv3 = (x3 + x4) / 2
        if abs(xv3) > x_bound:
            continue

        yv3 = a3 * (xv3 - x3) * (xv3 - x4)
        if abs(yv3 - round(yv3)) > 1e-9:
            continue
        yv3 = int(round(yv3))

        if abs(yv3) > y_bound:
            continue

        # Omdat t=0, zijn de verschoven y-waarden gelijk aan de onverschoven y-waarden
        yv1_s = yv1
        yv2_s = yv2
        yv3_s = yv3

        # ---------- 7. NUMMERIEKE CONTROLE GLADHEID ----------

        # Controleer gladheid bij x2
        if abs(a1 * (x2 - x1) - a2 * (x2 - x3)) > 1e-6:
            continue

        # Controleer gladheid bij x3
        if abs(a2 * (x3 - x2) - a3 * (x3 - x4)) > 1e-6:
            continue

        # ---------- 8. GEO­GEBRA VOORSCHRIFT ----------
        def fmt(c):
            if abs(c - round(c)) < 1e-9:
                return str(int(round(c)))
            return str(c)

        def term(c):
            c_int = int(round(c))
            if c_int >= 0:
                return f"(x-{c_int})"
            else:
                return f"(x+{-c_int})"

        def format_parabola(a, z1, z2):
            # t=0, dus geen shift toevoegen
            return f"{fmt(a)}*{term(z1)}*{term(z2)}"

        p1_func = format_parabola(a1, x1, x2)
        p2_func = format_parabola(a2, x2, x3)
        p3_func = format_parabola(a3, x3, x4)

        geogebra_rule = f"If[x <= {x2}, {p1_func}, If[x <= {x3}, {p2_func}, {p3_func}]]"

        return {
            "x1": x1, "x2": x2, "x3": x3, "x4": x4,
            "xv1": xv1, "yv1": yv1_s,
            "xv2": xv2, "yv2": yv2_s,
            "xv3": xv3, "yv3": yv3_s,
            "a1": a1, "a2": a2, "a3": a3,
            "y_shift": t,
            "rule": geogebra_rule
        }

    raise RuntimeError("Geen geschikte functie gevonden")


# ================= ZELFTEST =================
if __name__ == "__main__":
    # for i in range(5):
    #     info = generate_geogebra_piecewise_approximation_smooth(
    #         extrema_y_symmetry=False
    #     )
    #     print(f"\nVoorbeeld {i+1}")
    #     print("nulpunten:", info["x1"], info["x2"], info["x3"])
    #     print("extremum links :", (info["xv1"], info["yv1"]))
    #     print("extremum rechts:", (info["xv2"], info["yv2"]))
    #     print("verticale shift:", info["y_shift"])
    #     print("GeoGebra:", info["rule"])


    for i in range(3):
        info = vierdegraad_benadering()
        print(f"Voorbeeld {i+1}")
        print("nulpunten (y=0):", info["x1"], info["x2"], info["x3"], info["x4"])
        print("extremum links :", (info["xv1"], info["yv1"]))
        print("extremum midden:", (info["xv2"], info["yv2"]))
        print("extremum rechts:", (info["xv3"], info["yv3"]))
        print("verticale shift:", info["y_shift"])
        print("GeoGebra:", info["rule"])
