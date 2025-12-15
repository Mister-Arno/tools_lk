# klasplaats_generator.py
"""Genereer **meerdere** klasopstellingen (4×3 ↔ 3×4)
-------------------------------------------------------
*   Alle harde regels worden 100 % gerespecteerd.
*   Zachte voorkeuren leveren een score op:
    +3  front-pref vervuld, +3 back-pref, +2 solo-pref
    −1  volledig lege bank in rij 1–2 (midden/voorlaatst)
*   Je kunt nu **N opstellingen** opvragen, samen met
    –   hun totaalscore
    –   een lijstje *welke* voorkeuren niet gehaald zijn.

Gebruik
~~~~bash
python klasplaats_generator.py --n 10 --seed 42
~~~~
"""
from __future__ import annotations

import argparse
import itertools
import random
from collections import defaultdict, Counter
from typing import Dict, List, Sequence, Tuple, Set, Optional

# ==== Types ================================================================
Seat = Tuple[int, int, str]  # (row, col, side) – side ∈ {"L", "R"}
Assignment = Dict[Seat, str]  # seat → leerling
Candidate = Tuple[Assignment, int, List[str]]  # indeling, score, uitleg


# ------------------------------------------------------------
# 1. Stoelen & mapping
# ------------------------------------------------------------

def build_seats_layout1() -> List[Seat]:
    return [(row, col, side)
            for row in range(4)  # 0 achter, 3 voor
            for col in range(3)  # 0 links → 2 rechts
            for side in ("L", "R")]


def map_to_layout2(seat: Seat) -> Seat:
    row, col, side = seat
    if row == 0:  # achterste rij → kolom 3
        return (col, 3, side)  # kolomnum wordt nieuwe rij
    return (row - 1, col, side)  # andere rijen één omhoog


def build_seats_layout2(seats1: Sequence[Seat]) -> List[Seat]:
    return [map_to_layout2(s) for s in seats1]


# ------------------------------------------------------------
# 2. Adjacency (buren) beide lay-outs
# ------------------------------------------------------------

def neighbouring_banks(row: int, col: int) -> List[Tuple[int, int]]:
    return [(row, col - 1), (row, col + 1), (row - 1, col), (row + 1, col)]


def build_adjacency(seats: Sequence[Seat]) -> Dict[Seat, Set[Seat]]:
    bank = defaultdict(list)
    for s in seats:
        bank[(s[0], s[1])].append(s)
    adj: Dict[Seat, Set[Seat]] = {s: set() for s in seats}
    for s in seats:
        r, c, _ = s
        adj[s].update(bank[(r, c)])
        for r2, c2 in neighbouring_banks(r, c):
            adj[s].update(bank.get((r2, c2), []))
        adj[s].discard(s)
    return adj


# ------------------------------------------------------------
# 3. Generator
# ------------------------------------------------------------

class SeatingGenerator:
    def __init__(self,
                 names: Sequence[str],
                 forbidden_groups: List[Sequence[str]],
                 *,
                 front_pref: Sequence[str] = (),
                 back_pref: Sequence[str] = (),
                 solo_pref: Sequence[str] = (),
                 genders: Optional[Dict[str, str]] = None,
                 avoid_mixed_bank: bool = False,
                 max_attempts: int = 100000,
                 rng: Optional[random.Random] = None):
        if len(names) > 24:
            raise ValueError("Meer dan 24 leerlingen past nooit.")
        self.names = list(names)
        self.front_pref, self.back_pref = set(front_pref), set(back_pref)
        self.solo_pref = set(solo_pref)
        self.genders = genders or {}
        self.avoid_mixed_bank = avoid_mixed_bank
        self.max_attempts = max_attempts
        self.rng = rng or random.Random()

        self.forbidden_pairs: Set[Tuple[str, str]] = {
            tuple(sorted(p))
            for group in forbidden_groups
            for p in itertools.combinations(group, 2)
        }

        # Precompute seats & adjacency
        self.seats1 = build_seats_layout1()
        self.seats2 = build_seats_layout2(self.seats1)
        self.adj1 = build_adjacency(self.seats1)
        self.adj2 = build_adjacency(self.seats2)

    # ---------- helpers ----------
    def _are_adjacent(self, a: Seat, b: Seat) -> bool:
        if b in self.adj1[a]:
            return True
        return map_to_layout2(b) in self.adj2[map_to_layout2(a)]

    # ---------- scoring & uitleg ----------
    def _evaluate(self, assignment: Assignment) -> Tuple[int, List[str]]:
        score, missing = 500, []

        # ---------------- per-leerling ­scores ----------------
        for seat, name in assignment.items():
            row1 = seat[0]                     # 4×3-lay-out
            row2 = map_to_layout2(seat)[0]     # 3×4-lay-out

            if name in self.front_pref:
                (row1 == 3 and row2 == 2) or missing.append(f"{name} niet vooraan")
                score += 200 if (row1 == 3 and row2 == 2) else 0

            if name in self.back_pref:
                (row1 == 0 and row2 == 0) or missing.append(f"{name} niet achteraan")
                score += 30 if (row1 == 0 and row2 == 0) else 0

            if name in self.solo_pref:
                mates = [n for s, n in assignment.items() if s[:2] == seat[:2] and s != seat]
                (not mates) or missing.append(f"{name} niet alleen")
                score += 100 if not mates else 0

        # ---------------- bank-analyses beide lay-outs ----------------
        EMPTY_PENALTY = 50
        FULL_PENALTY = {1: 100, 2: 200, 3: 400}   # afstand tot front­rij (1=2e rij, ...)

        # ---- lay-out 1: 4×3 ------------------------------
        for r in range(4):
            for c in range(3):
                seats_here = [s for s in assignment if s[:2] == (r, c)]
                dist = 3 - r                     # 0 = voorste rij
                if not seats_here:
                    score -= EMPTY_PENALTY
                    missing.append(f"Er is een lege bank (dus geen optimale bezetting)")
                elif len(seats_here) == 2 and dist > 0:
                    penalty = FULL_PENALTY[dist]           # dist is nu 1–3
                    score -= penalty


        # ---- lay-out 2: 3×4 ------------------------------
        for r in range(3):
            for c in range(4):
                seats_here = [s for s in assignment if map_to_layout2(s)[:2] == (r, c)]
                dist = 2 - r                     # 0 = voorste rij
                if not seats_here:
                    score -= EMPTY_PENALTY
                    missing.append(f"Er is een lege bank (dus geen optimale bezetting)")
                elif len(seats_here) == 2 and dist > 0:
                    penalty = FULL_PENALTY[dist]           # dist is nu 1–2
                    score -= penalty


        return score, missing




    # ---------- core backtracking ----------
    def _place_recursive(self, idx: int, seats: List[Seat], assign: Assignment) -> bool:
        if idx == len(self.names):
            return True
        name = self.names[idx]
        for seat in seats:
            if seat in assign:
                continue
            # harde paren
            if any(tuple(sorted((name, other))) in self.forbidden_pairs and self._are_adjacent(seat, s)
                   for s, other in assign.items()):
                continue
            # mixed bank
            if self.avoid_mixed_bank:
                mates = [assign[s] for s in assign if s[:2] == seat[:2]]
                if mates and any(self.genders.get(m) != self.genders.get(name) for m in mates):
                    continue
            assign[seat] = name
            if self._place_recursive(idx + 1, seats, assign):
                return True
            del assign[seat]
        return False

    # ---------- public API ----------
    def generate_candidates(self, n: int = 10) -> List[Candidate]:
        best: List[Candidate] = []
        seats = self.seats1.copy()
        for _ in range(self.max_attempts):
            self.rng.shuffle(seats)
            assign: Assignment = {}
            if self._place_recursive(0, seats, assign):
                score, missing = self._evaluate(assign)
                best.append((assign.copy(), score, missing))
                best.sort(key=lambda x: x[1], reverse=True)
                best = best[:n]  # houd top-n
                max_possible = 3 * len(self.front_pref | self.back_pref) + 2 * len(self.solo_pref)
                if len(best) >= n and best[-1][1] == max_possible:
                    break

        if not best:
            raise RuntimeError("Geen enkele geldige opstelling gevonden.")
        return best


# ------------------------------------------------------------
# 4. Visualisatie
# ------------------------------------------------------------

def print_layout(assignment: Assignment, seats: Sequence[Seat]) -> None:
    banks = defaultdict(list)
    for seat, name in assignment.items():
        banks[(seat[0], seat[1])].append((seat[2], name))
    max_row = max(r for r, _, _ in seats)
    max_col = max(c for _, c, _ in seats)
    for r in range(max_row + 1):
        row_cells = []
        for c in range(max_col + 1):
            mates = sorted(banks.get((r, c), []), key=lambda x: x[0])
            cell = "/".join(n for _, n in mates) if mates else "----"
            row_cells.append(f"{cell:^16}")
        print(" ".join(row_cells))
    print("TEST")


# ------------------------------------------------------------
# 5. CLI-demo
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10, help="Aantal lay-outs om te tonen")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    leerlingen = [
        "Lina", "Azra", "Berat", "Marouane", "Marouan",
        "Israe", "Fatimazahra", "Inaya", "Diestelle", "Jérémie",
        "Andy", "Farhad", "Zuzanna", "Arsela", "Mahdi",
    ]
    genders = {n: ("M" if n in {"Berat", "Marouane", "Marouan", "Mahdi", "Jérémie", "Andy", "Farhad"} else "V")
               for n in leerlingen}
    verboden = [["Marouan", "Marouane", "Berat"], ["Lina", "Diestelle"], ["Fatimazahra", "Zuzanna"], ["Andy", "Jérémie"]]
    front = ["Marouan", "Israe"]
    back = ["Mahdi"]
    solo = ["Marouan", "Israe"]

    rng = random.Random(args.seed)
    gen = SeatingGenerator(leerlingen, verboden,
                           front_pref=front, back_pref=back, solo_pref=solo,
                           genders=genders, avoid_mixed_bank=True,
                           rng=rng)
    cands = gen.generate_candidates(args.n)

    for i, (assign, sc, miss) in enumerate(cands, 1):
        print(f"\n### Kandidaat {i} — score {sc}")
        if miss:
            print("Niet voldaan: " + ", ".join(miss))
        else:
            print("Alle voorkeuren voldaan!")
        print("\nOpstelling 1 (4×3, front onder)")
        print_layout(assign, gen.seats1)
        print("\nOpstelling 2 (3×4, front onder)")
        assign2 = {map_to_layout2(s): n for s, n in assign.items()}
        print_layout(assign2, gen.seats2)
        print("#" * 80)


if __name__ == "__main__":
    main()
