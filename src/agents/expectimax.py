from __future__ import annotations

import time
from functools import lru_cache
from typing import Optional, Tuple, Dict, Union, List

from src.agents.base import Agent
from src.agents.greedy import GreedyAgent
from src.game.state import GameState
from src.heuristics.evaluate import evaluate

CacheKey = Tuple[Tuple[Tuple[int, ...], ...], str, int]

class ExpectimaxAgent(Agent):
    def __init__(
            self,
            weights: Optional[dict[str, float]] = None,
            max_depth: int = 3,
            adaptive_depth_config: Optional[Dict[str, int]] = None,
            time_limit_ms: Optional[int] = None,
            greedy_fallback: Optional[GreedyAgent] = None,
            cache_maxsize: int = 100000
    ) -> None:
        self.weights = weights
        self.max_depth_fixed = max_depth
        self.adaptive_depth_config = adaptive_depth_config
        self.time_limit_ms = time_limit_ms
        self.greedy_fallback = greedy_fallback or GreedyAgent(
            weights = weights, fallback = "up"
        )
        self._deadline: Optional[float] = None
        self._max_value_cached = lru_cache(maxsize = cache_maxsize)(self._max_value_inner)
        self._chance_value_cached = lru_cache(maxsize = cache_maxsize)(self._chance_value_inner)

    def choose_move(self, state: GameState) -> str:
        self._deadline = (
            time.perf_counter() + ( self.time_limit_ms / 1000.0 )

            if self.time_limit_ms
            else None
        )

        self._max_value_cached.cache_clear()
        self._chance_value_cached.cache_clear()

        current_max_depth = self._get_adaptive_depth(state)

        best_move = None
        best_val = float("-inf")
        moves = state.legal_moves()

        if not moves:
            return "up"

        scored_moves: List[Tuple[float, str]] = []
        for move in moves:
            ns = state.clone()
            ns.step(move, spawn = False)
            score = evaluate(ns.board, self.weights)
            scored_moves.append((score, move))

        scored_moves.sort(key = lambda x: x[0], reverse = True)

        for score, move in scored_moves:
            if self._timed_out():
                return self.greedy_fallback.choose_move(state)

            ns = state.clone()
            ns.step(move, spawn = False)

            board_tuple = self._board_to_tuple(ns.board)
            val = self._chance_value_cached(board_tuple, "CHANCE", current_max_depth, depth = 1)

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

    def _max_value_inner(self, board_tuple: Tuple[Tuple[int, ...], ...], node_type: str, max_depth_limit: int, depth: int) -> float:
        state = GameState(board = self._tuple_to_board(board_tuple))

        if self._cutoff(state, depth, max_depth_limit):
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

            next_board_tuple = self._board_to_tuple(ns.board)
            v = max(v, self._chance_value_cached(next_board_tuple, "CHANCE", max_depth_limit, depth + 1))

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

    def _chance_value_inner(self, board_tuple: Tuple[Tuple[int, ...], ...], node_type: str, max_depth_limit: int, depth: int) -> float:
        state = GameState(board = self._tuple_to_board(board_tuple))

        if self._cutoff(state, depth, max_depth_limit):
            return evaluate(state.board, self.weights)

        empties = state.empty_cells()

        if not empties:
            return self._max_value_cached(board_tuple, "MAX", max_depth_limit, depth + 1)

        expected = 0.0

        for (r, c) in empties:
            if self._timed_out():
                return evaluate(state.board, self.weights)

            # kafelek 2
            ns2 = state.clone()
            ns2.board[r][c] = 2
            next_board_tuple_2 = self._board_to_tuple(ns2.board)
            expected += 0.9 * self._max_value_cached(next_board_tuple_2, "MAX", max_depth_limit, depth + 1)

            # kafelek 4
            ns4 = state.clone()
            ns4.board[r][c] = 4
            next_board_tuple_4 = self._board_to_tuple(ns4.board)
            expected += 0.1 * self._max_value_cached(next_board_tuple_4, "MAX", max_depth_limit, depth + 1)

        return expected / float(len(empties))

    def _cutoff(self, state: GameState, current_depth: int, max_depth_limit: Optional[int] = None) -> bool:
        """Warunki zatrzymania rekurencji"""

        if current_depth >= max_depth_limit:
            return True

        if state.is_terminal():
            return True

        if self._timed_out():
            return True

        return False

    def _timed_out(self) -> bool:
        return self._deadline is not None and time.perf_counter() > self._deadline

    def _get_adaptive_depth(self, state: GameState) -> int:
        """Zwraca adaptacyjną głębokość w zależności od liczby pustych pól"""

        if self.adaptive_depth_config is None:
            return self.max_depth_fixed

        base = self.adaptive_depth_config.get("base", 2)
        threshold = self.adaptive_depth_config.get("threshold", 6)
        bonus = self.adaptive_depth_config.get("bonus", 1)

        if len(state.empty_cells()) >= threshold:
            return base + bonus

        return base

    @staticmethod
    def _board_to_tuple(board: List[List[int]]) -> Tuple[Tuple[int, ...], ...]:
        return tuple(tuple(row) for row in board)

    @staticmethod
    def _tuple_to_board(board_tuple: Tuple[Tuple[int, ...], ...]) -> List[List[int]]:
        return [list(row) for row in board_tuple]