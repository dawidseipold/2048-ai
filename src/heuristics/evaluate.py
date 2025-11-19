from __future__ import annotations

import math
from typing import Dict, List

def _log_board(board: List[List[int]]) -> List[List[float]]:
    lb: List[List[float]] = []

    for r in range(len(board)):
        row: List[float] = []
        for v in board[r]:
            if v <= 0:
                row.append(0.0)
            else:
                row.append(math.log2(v))
        lb.append(row)
    return lb

def count_empty(board: List[List[int]]) -> int:
    empty = 0

    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] == 0:
                empty += 1

    return empty


def monotonicity(board: List[List[int]]) -> float:
    """
    Mierzy 'uporządkowanie' wierszy i kolumn.
    Liczymy sumy zmian w dwóch kierunkach i bierzemy lepszy wariant.
    Im większa monotoniczność, tym lepiej.
    """

    lb = _log_board(board)

    def line_mono(line: List[float]) -> float:
        inc = 0.0
        dec = 0.0

        for i in range(len(line) - 1):
            diff = line[i + 1] - line[i]

            if diff > 0:
                inc += diff
            else:
                dec -= diff  # diff <= 0

        # bierz lepszy z dwóch kierunków (mniejsze zmiany = lepiej)
        return -min(inc, dec)

    total = 0.0

    # wiersze
    for r in range(len(lb)):
        total += line_mono(lb[r])

    # kolumny
    n = len(lb)
    m = len(lb[0]) if n > 0 else 0

    for c in range(m):
        col = [lb[r][c] for r in range(n)]
        total += line_mono(col)

    return total

def smoothness(board: List[List[int]]) -> float:
    """
    Kara za duże różnice między sąsiadami (poziomo i pionowo).
    Zwracamy wartość ujemną (większa 'chropowatość' = gorzej).
    """

    lb = _log_board(board)
    s = 0.0
    n = len(board)
    m = len(board[0]) if n > 0 else 0

    for r in range(n):
        for c in range(m):
            if board[r][c] == 0:
                continue
            if r + 1 < n and board[r + 1][c] != 0:
                s -= abs(lb[r][c] - lb[r + 1][c])
            if c + 1 < m and board[r][c + 1] != 0:
                s -= abs(lb[r][c] - lb[r][c + 1])

    return s


def max_in_corner(board: List[List[int]]) -> float:
    """
    1.0 jeśli największy kafelek jest w dowolnym rogu, inaczej 0.0
    """

    n = len(board)
    m = len(board[0]) if n > 0 else 0

    if n == 0 or m == 0:
        return 0.0

    maxv = 0

    for r in range(n):
        for c in range(m):
            if board[r][c] > maxv:
                maxv = board[r][c]

    corners = [(0, 0), (0, m - 1), (n - 1, 0), (n - 1, m - 1)]

    for (r, c) in corners:
        if board[r][c] == maxv:
            return 1.0

    return 0.0


def evaluate(board: List[List[int]], weights: Dict[str, float] | None = None) -> float:
    """
    Łączy cechy w wynik końcowy. Dostosuj wagi w JSON-ach.
    """

    if weights is None:
        weights = {
            "empty": 250.0,
            "mono": 1.0,
            "smooth": 0.1,  # będzie użyte ze znakiem minus
            "corner": 1000.0,
        }

    empty = count_empty(board)
    mono = monotonicity(board)
    smooth = smoothness(board)  # to jest ujemne lub 0
    corner = max_in_corner(board)

    score = (
        weights["empty"] * float(empty)
        + weights["mono"] * float(mono)
        # smoothness jest ujemne; dajemy minus, żeby wyższa waga = większa kara
        - weights["smooth"] * float(abs(smooth))
        + weights["corner"] * float(corner)
    )

    return float(score)