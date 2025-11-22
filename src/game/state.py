# src/game/state.py
from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.game import constants as c
from src.game.logic import game_state, new_game

Move = str
ALLOWED_MOVES: tuple[str, ...] = ("up", "down", "left", "right")


@dataclass
class StepResult:
    reward: int
    done: bool


class GameState:
    def __init__(
            self,
            seed: Optional[int] = None,
            board: Optional[List[List[int]]] = None,
            score: int = 0,
    ) -> None:
        self.rng = random.Random(seed)
        self._seed = seed
        self.board = new_game(c.GRID_LEN) if board is None else copy.deepcopy(board)
        self.score = int(score)
        self.done = self._compute_done()

    def reset(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.rng = random.Random(seed)
            self._seed = seed
        elif self._seed is not None:
            self.rng = random.Random(self._seed)
        self.board = new_game(c.GRID_LEN)
        self.score = 0
        self.done = self._compute_done()

    def clone(self) -> "GameState":
        return GameState(seed=self._seed, board=self.board, score=self.score)

    def legal_moves(self) -> List[Move]:
        if self.done:
            return []
        legal: List[Move] = []
        for m in ALLOWED_MOVES:
            _, moved, _ = self._simulate_move_with_gain(m, self.board)
            if moved:
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
        if self.done:
            return StepResult(reward=0, done=True)
        if move not in ALLOWED_MOVES:
            raise ValueError(f"Nieznany ruch: {move}")

        new_board, moved, gain = self._simulate_move_with_gain(move, self.board)
        if not moved:
            self.done = self._compute_done()
            return StepResult(reward=0, done=self.done)

        self.board = new_board
        self.score += gain

        if spawn:
            self._spawn_tile()

        self.done = self._compute_done()
        return StepResult(reward=gain, done=self.done)

    def _simulate_move_with_gain(
            self, move: Move, board: List[List[int]]
    ) -> Tuple[List[List[int]], bool, int]:
        b = copy.deepcopy(board)
        gain = 0

        def cover_up(mat: List[List[int]]) -> Tuple[List[List[int]], bool]:
            new = [[0] * c.GRID_LEN for _ in range(c.GRID_LEN)]
            done_local = False
            for i in range(c.GRID_LEN):
                count = 0
                for j in range(c.GRID_LEN):
                    if mat[i][j] != 0:
                        new[i][count] = mat[i][j]
                        if j != count:
                            done_local = True
                        count += 1
            return new, done_local

        def merge_gain(mat: List[List[int]], done_flag: bool) -> Tuple[List[List[int]], bool]:
            nonlocal gain
            for i in range(c.GRID_LEN):
                for j in range(c.GRID_LEN - 1):
                    if mat[i][j] != 0 and mat[i][j] == mat[i][j + 1]:
                        mat[i][j] *= 2
                        gain += mat[i][j]
                        mat[i][j + 1] = 0
                        done_flag = True
            return mat, done_flag

        def reverse(mat: List[List[int]]) -> List[List[int]]:
            return [list(reversed(row)) for row in mat]

        def transpose(mat: List[List[int]]) -> List[List[int]]:
            return [list(row) for row in zip(*mat)]

        before = [row[:] for row in b]  # szybka kopia

        d1 = False # Inicjalizacja d1 i d2
        d2 = False

        if move == "left":
            b, d1 = cover_up(b)
            b, d2 = merge_gain(b, d1) # Poprawka: przekazujemy d1
            b, _ = cover_up(b)
        elif move == "right":
            b = reverse(b)
            b, d1 = cover_up(b)
            b, d2 = merge_gain(b, d1) # Poprawka: przekazujemy d1
            b, _ = cover_up(b)
            b = reverse(b)
        elif move == "up":
            b = transpose(b)
            b, d1 = cover_up(b)
            b, d2 = merge_gain(b, d1) # Poprawka: przekazujemy d1
            b, _ = cover_up(b)
            b = transpose(b)
        elif move == "down":
            b = transpose(b)
            b = reverse(b)
            b, d1 = cover_up(b)
            b, d2 = merge_gain(b, d1) # Poprawka: przekazujemy d1
            b, _ = cover_up(b)
            b = reverse(b)
            b = transpose(b)
        else:
            return board, False, 0

        moved = d1 or d2 or (b != before)
        return b, moved, gain

    def _spawn_tile(self) -> None:
        empties = self.empty_cells()
        if not empties:
            return
        r, k = self.rng.choice(empties)
        val = 4 if self.rng.random() < 0.1 else 2
        self.board[r][k] = val

    def _compute_done(self) -> bool:
        return game_state(self.board) in ("win", "lose")

    def max_tile(self) -> int:
        return max(max(row) for row in self.board)

    def __repr__(self) -> str:
        lines = [f"Score: {self.score}  Done: {self.done}"]
        for row in self.board:
            lines.append(" ".join(f"{v:4d}" for v in row))
        return "\n".join(lines)