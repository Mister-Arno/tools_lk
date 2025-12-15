# -*- coding: utf-8 -*-
"""
Seating generator voor een Vlaamse klas (max. 24 leerlingen)
===========================================================

Deze module genereert een klasopstelling die tegelijk geldig is voor:
    1. 4 rijen × 3 banken  (Layout A)
    2. 3 rijen × 4 banken  (Layout B)  ➜ ontstaat door de laatste rij
       (rij 3) van Layout A als extra kolom rechts te draaien.

Voor beide lay‑outs moeten alle harde regels gerespecteerd blijven:
    • Leerlingen in een ‘verbods‑groep’ mogen nooit
      – naast elkaar,
      – vóór/achter elkaar
      (ook niet met een gangpad ertussen).
    • ‘Alleen‑zitters’ krijgen een volledige bank voor zichzelf.

Voorkeuren (voor/achteraan) worden zo goed mogelijk vervuld, maar zijn
minder hard dan de bovenstaande regels.

Gebruik:
    from seating_generator import generate_seating, print_layouts

    layoutA, layoutB = generate_seating(
        names, forbidden_groups, want_front, want_back, want_solo
    )
    print_layouts(layoutA, layoutB)
"""
from __future__ import annotations

import itertools
import random
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

# ──────────────────────────────────────────────────────────────────────────────
#  Interne representatie
# ──────────────────────────────────────────────────────────────────────────────

Seat = Tuple[int, int, int]  # (row, col, side) – side: 0 = links, 1 = rechts
Assignment = Dict[Seat, str]

# Layout A: 4 rijen × 3 banken ↔ 12 banken → 24 zitjes
ROWS_A, COLS_A = 4, 3
BANKS_A = [(r, c) for r in range(ROWS_A) for c in range(COLS_A)]
SEATS_A: List[Seat] = [(r, c, s) for (r, c) in BANKS_A for s in (0, 1)]

# Transformatie naar Layout B (3 × 4)
# ────────────────────────────────────
# Bank (3, c) uit Layout A wordt Bank (r = c, c = 3) in Layout B.

def to_layout_b(seat: Seat) -> Seat:
    r, c, s = seat
    if r == 3:
        return (c, 3, s)  # rij en kolom verwisselen, side onveranderd
    return seat

# Beschouw een seat als ‘naburig’ wanneer hij horizontaal (±1 kolom) of
# verticaal (±1 rij) aansluit, óf de partner‑seat in dezelfde bank is.

def _adjacent_pairs(seats: Sequence[Seat]) -> Dict[Seat, set]:
    adj: Dict[Seat, set] = defaultdict(set)
    for a, b in itertools.combinations(seats, 2):
        ar, ac, _ = a
        br, bc, _ = b
        same_bank = (ar == br and ac == bc)
        hori_adj = (ar == br and abs(ac - bc) == 1)
        vert_adj = (ac == bc and abs(ar - br) == 1)
        if same_bank or hori_adj or vert_adj:
            adj[a].add(b)
            adj[b].add(a)
    return adj

ADJ_A = _adjacent_pairs(SEATS_A)
SEATS_B = [to_layout_b(s) for s in SEATS_A]
ADJ_B = _adjacent_pairs(SEATS_B)
# Vereist: een conflict in één van beide layouts telt → unie van beide grafen
ADJ_COMBINED: Dict[Seat, set] = {
    s: ADJ_A[s].union(ADJ_B[s]) for s in SEATS_A
}

# Helper om snel de ‘buddy‑seat’ (zelfde bank) op te halen
BUDDY: Dict[Seat, Seat] = {
    s: (s[0], s[1], 1 - s[2]) for s in SEATS_A
}

# ──────────────────────────────────────────────────────────────────────────────
#  Hoofd‑API
# ──────────────────────────────────────────────────────────────────────────────

def generate_seating(
        names: Sequence[str],
        forbidden_groups: Sequence[Sequence[str]],
        want_front: Sequence[str] = (),
        want_back: Sequence[str] = (),
        want_solo: Sequence[str] = (),
        max_attempts: int = 50_000,
) -> Tuple[List[List[List[Optional[str]]]], List[List[List[Optional[str]]]]]:
    """Zoek een geldige opstelling.  Werpt *ValueError* wanneer geen
    oplossing gevonden wordt in *max_attempts* pogingen."""

    if len(names) > len(SEATS_A):
        raise ValueError("Meer leerlingen dan zitplaatsen (24).")

    # Mapping: leerling → set van ‘verboden buren’
    forbidden_map: Dict[str, set] = defaultdict(set)
    for group in forbidden_groups:
        for a, b in itertools.combinations(group, 2):
            forbidden_map[a].add(b)
            forbidden_map[b].add(a)

    students = list(names)

    # Sorteer leerlingen op strengheid (solo ≫ groep ≫ rest)
    def _key(name: str):
        return (
            name in want_solo,
            bool(forbidden_map[name]),
            name in want_front or name in want_back,
        )

    students.sort(key=_key, reverse=True)

    # Pref‑rangschikking per leerling: lijst van seats in gewenste volgorde
    seat_pref: Dict[str, List[Seat]] = {}
    for st in students:
        seats = SEATS_A.copy()
        random.shuffle(seats)  # beetje variatie
        if st in want_front:
            seats.sort(key=lambda s: s[0])          # rij 0 = vooraan
        elif st in want_back:
            seats.sort(key=lambda s: -s[0])         # rij 3 = achteraan
        seat_pref[st] = seats

    # Backtracking
    assignment: Assignment = {}
    reserved: set = set()  # seats die leeg moeten blijven (solo‑banken)

    def backtrack(idx: int) -> bool:
        if idx == len(students):
            return True  # alles geplaatst

        st = students[idx]
        for seat in seat_pref[st]:
            if seat in assignment or seat in reserved:
                continue
            buddy = BUDDY[seat]
            # Solo‑leerling? Partner‑seat moet vrij blijven
            if st in want_solo and (buddy in assignment or buddy in reserved):
                continue
            # Check verboden buren
            ok = True
            for adj in ADJ_COMBINED[seat]:
                mate = assignment.get(adj)
                if mate and (mate in forbidden_map[st]):
                    ok = False
                    break
            if not ok:
                continue

            # Plaats leerling
            assignment[seat] = st
            if st in want_solo:
                reserved.add(buddy)
            if backtrack(idx + 1):
                return True
            # ↺ backtrack
            del assignment[seat]
            if st in want_solo:
                reserved.discard(buddy)
        return False

    for attempt in range(max_attempts):
        assignment.clear()
        reserved.clear()
        random.shuffle(students)  # nieuw startpunt
        if backtrack(0):
            break
    else:
        raise ValueError("Geen geldige opstelling gevonden.")

    # Bouw grids
    gridA: List[List[List[Optional[str]]]] = [[ [None, None] for _ in range(COLS_A) ] for _ in range(ROWS_A)]
    for seat, pupil in assignment.items():
        r, c, side = seat
        gridA[r][c][side] = pupil
    # Solo‑banken krijgen een expliciete ‘—’ voor de lege zitplaats
    for seat in reserved:
        r, c, side = seat
        gridA[r][c][side] = "—"

    # Layout B afleiden via transformatie
    gridB: List[List[List[Optional[str]]]] = [[ [None, None] for _ in range(4) ] for _ in range(3)]
    for (r, c, s), pupil in assignment.items():
        nr, nc, ns = to_layout_b((r, c, s))
        gridB[nr][nc][ns] = pupil
    for seat in reserved:
        nr, nc, ns = to_layout_b(seat)
        gridB[nr][nc][ns] = "—"
    return gridA, gridB

# ──────────────────────────────────────────────────────────────────────────────
#  Puur esthetisch: console‑afdruk
# ──────────────────────────────────────────────────────────────────────────────

def _fmt_bank(bank: List[Optional[str]]) -> str:
    left, right = bank
    def cell(x):
        return (x or "—").center(10)
    return f"{cell(left)}|{cell(right)}"


def print_layout(layout: List[List[List[Optional[str]]]]):
    # Onderste rij eerst printen (voorkant van het lokaal)
    for row in layout:
        print("   ".join(_fmt_bank(b) for b in row))
    print()


def print_layouts(layoutA, layoutB):
    print("Layout A – 4×3 (voorkant onderaan)\n" + "="*50)
    print_layout(layoutA)
    print("Layout B – 3×4 (voorkant onderaan)\n" + "="*50)
    print_layout(layoutB)

# ──────────────────────────────────────────────────────────────────────────────
#  Demo (alleen uitvoeren wanneer module standalone draait)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pupils = [f"Lln{i:02d}" for i in range(1, 23)]  # 22 leerlingen
    forbidden = [ ["Lln01", "Lln02"], ["Lln03", "Lln04", "Lln05"] ]
    front = ["Lln06", "Lln07"]
    back = ["Lln08", "Lln09"]
    solo = ["Lln10", "Lln11"]

    a, b = generate_seating(pupils, forbidden, front, back, solo)
    print_layouts(a, b)
