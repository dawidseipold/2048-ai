from __future__ import annotations

import time
from typing import Optional, Tuple

from src.agents.base import Agent
from src.agents.greedy import GreedyAgent
from src.game.state import GameState
from src.heuristics.evaluate import evaluate

class ExpectimaxAgent(Agent):
    def __init__(
            self,
            weights: Optional[dict[str, float]] = None,
            max_depth: int = 3,
            time_limit_ms: Optional[int] = None,
            greedy_fallback: Optional[GreedyAgent] = None
    ) -> None:
        self.weights = weights
        self.max_depth = max_depth
        self.time_limit_ms = time_limit_ms
        self.greedy_fallback = greedy_fallback or GreedyAgent(
            weights = weights, fallback = "up"
        )
        self._deadline: Optional[float] = None

    def choose_move(self, state: GameState) -> str:
        self._deadline = (
            time.perf_counter() + ( self.time_limit_ms / 1000.0 )

            if self.time_limit_ms
            else None
        )

        best_move = None
        best_val = float("-inf")
        moves = state.legal_moves()

        if not moves:
            return "up"

        for move in moves:
            if self._timed_out():
                return self.greedy_fallback.choose_move(state)

            ns = state.clone()
            ns.step(move, spawn = False)
            val = self._chance_value(ns, depth = 1)

            if val > best_val:
                best_val = val
                best_move = move

        return best_move or "up"


    def _max_value(self, state, depth: int) -> float:
        if self._cutoff(state, depth):
            return evaluate(state.board, self.weights)

        moves = state.legal_moves()

        if not moves:
            return evaluate(state.board, self.weights)

        v = float("-inf")

        for move in moves:
            if self._timed_out():
                return evaluate(state.board, self.weights)

            ns = state.clone()
            ns.step(move, spawn = False)
            v = max(v, self._chance_value(ns, depth + 1))

        return v

    def _chance_value(self, state, depth: int) -> float:
        if self._cutoff(state, depth):
            return evaluate(state.board, self.weights)

        empties = state.empty_cells()

        if not empties:
            return self._max_value(state, depth + 1)

        expected = 0.0

        for (r, c) in empties:
            if self._timed_out():
                return evaluate(state.board, self.weights)

            ns2 = state.clone()
            ns2.board[r][c] = 2
            expected += 0.9 * self._max_value(ns2, depth + 1)

            ns4 = state.clone()
            ns4.board[r][c] = 4
            expected += 0.1 * self._max_value(ns4, depth + 1)

        return expected / float(len(empties))

    def _cutoff(self, state, depth: int) -> bool:
        if depth >= self.max_depth:
            return True

        if state.is_terminal():
            return True

        if self._timed_out():
            return True

        return False

    def _timed_out(self) -> bool:
        return self._deadline is not None and time.perf_counter() > self._deadline