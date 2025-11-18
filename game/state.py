# src/game/state.py
from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Importujemy Twoje moduły z folderu game/
# Jeżeli ten plik jest w src/game/state.py, a obok leżą logic.py i constants.py,
# to użyj względnego importu. Jeśli logic.py/constants.py są też w src/game/,
# zamień poniżej na from . import logic as logic, from . import constants as c
import game.logic as logic
import game.constants as c


Move = str  # "up" | "down" | "left" | "right"

MOVES = {
    "up": logic.up,
    "down": logic.down,
    "left": logic.left,
    "right": logic.right,
}


@dataclass
class StepResult:
    reward: int
    done: bool


class GameState:
    """
    Czysty wrapper na Twoją logikę 2048.

    - Rozdziela etap ruchu (deterministyczny) od losowego spawnu (spawn=True/False).
    - Pozwala seedować RNG dla powtarzalności.
    - Zapewnia funkcje: legal_moves, step, clone, empty_cells, is_terminal, reset.
    """

    def __init__(
            self,
            seed: Optional[int] = None,
            board: Optional[List[List[int]]] = None,
            score: int = 0,
    ) -> None:
        self.rng = random.Random(seed)
        self._seed = seed

        if board is None:
            self.board = logic.new_game(c.GRID_LEN)
        else:
            self.board = copy.deepcopy(board)

        # U Ciebie w logic.py score nie jest osobno liczony,
        # więc będziemy liczyć reward jako "zysk z merge'ów" per ruch.
        # Można go estymować przez różnicę sumy kafelków po ruchu i przed,
        # ale ponieważ add_two dodaje 2, bez spawnu różnica = reward.
        self.score = int(score)
        self.done = self._compute_done()

    # --------------- API ---------------

    def reset(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.rng = random.Random(seed)
            self._seed = seed
        elif self._seed is not None:
            self.rng = random.Random(self._seed)

        self.board = logic.new_game(c.GRID_LEN)
        self.score = 0
        self.done = self._compute_done()

    def clone(self) -> "GameState":
        return GameState(seed=self._seed, board=self.board, score=self.score)

    def legal_moves(self) -> List[Move]:
        if self.done:
            return []
        legal: List[Move] = []
        for m, fn in MOVES.items():
            new_board, moved = self._simulate_move(fn, self.board)
            if moved:  # zmiana układu oznacza legalny ruch
                legal.append(m)
        return legal

    def is_terminal(self) -> bool:
        return self._compute_done()

    def empty_cells(self) -> List[Tuple[int, int]]:
        cells: List[Tuple[int, int]] = []
        for r in range(c.GRID_LEN):
            for k in range(c.GRID_LEN):
                if self.board[r][k] == 0:
                    cells.append((r, k))
        return cells

    def step(self, move: Move, spawn: bool = True) -> StepResult:
        """
        Wykonuje ruch.
        - Jeśli spawn=True, po ruchu dodaje losową płytkę 2 (90%) lub 4 (10%).
        - Zwraca reward: przybliżony zysk z łączeń (bez doliczania spawnu).
        """
        if self.done:
            return StepResult(reward=0, done=True)

        if move not in MOVES:
            raise ValueError(f"Nieznany ruch: {move}")

        move_fn = MOVES[move]

        before_sum = self._sum_tiles(self.board)
        new_board, moved = self._simulate_move(move_fn, self.board)

        if not moved:
            # nielegalny – brak zmiany
            self.done = self._compute_done()
            return StepResult(reward=0, done=self.done)

        after_sum = self._sum_tiles(new_board)
        # reward to przyrost sumy kafelków wynikający z merge'ów
        reward = after_sum - before_sum

        self.board = new_board
        self.score += max(0, reward)

        if spawn:
            self._spawn_tile()

        self.done = self._compute_done()
        return StepResult(reward=max(0, reward), done=self.done)

    # --------------- Wnętrzności ---------------

    def _simulate_move(
            self, move_fn, board: List[List[int]]
    ) -> Tuple[List[List[int]], bool]:
        """
        Używa funkcji z logic.py (left/right/up/down), które zwracają (board, done)
        gdzie 'done' oznacza, że coś się przesunęło/zmerge'owało w tej operacji.
        """
        bcopy = copy.deepcopy(board)
        new_board, moved = move_fn(bcopy)
        # new_board to nowa macierz, moved = czy była zmiana
        return new_board, bool(moved)

    def _spawn_tile(self) -> None:
        empties = self.empty_cells()
        if not empties:
            return
        r, k = self.rng.choice(empties)
        val = 4 if self.rng.random() < 0.1 else 2
        self.board[r][k] = val

    def _compute_done(self) -> bool:
        state = logic.game_state(self.board)
        if state == "win":
            return True
        if state == "lose":
            return True
        # "not over" -> False
        return False

    @staticmethod
    def _sum_tiles(board: List[List[int]]) -> int:
        return sum(sum(row) for row in board)

    def max_tile(self) -> int:
        return max(max(row) for row in self.board)

    def __repr__(self) -> str:
        lines = []
        lines.append(f"Score: {self.score}  Done: {self.done}")
        for row in self.board:
            lines.append(" ".join(f"{v:4d}" for v in row))
        return "\n".join(lines)