from __future__ import annotations
from typing import Optional

from src.agents.base import Agent, SupportGameState
from src.heuristics.evaluate import evaluate
from src.heuristics.weights_loader import load_weights


class GreedyAgent(Agent):
    def __init__(self, weights: Optional[dict[str, float]] = None, fallback: str = "up"):
        """
        :param weights: słownik wag dla heurystyki; Jeśli None, evaluate użyje domyślnych
        :param fallback: ruch awaryjny gdy brak legalnych
        """

        self.weights = weights
        self.fallback = fallback

    def choose_move(self, state: SupportGameState) -> str:
        moves = state.legal_moves()

        if not moves:
            return self.fallback

        best_move = None
        best_val = float("-inf")

        for move in moves:
            ns = state.clone()
            ns.step(move, spawn = False)
            val = evaluate(ns.board, self.weights)

            if val > best_val:
                best_val = val
                best_move = move

        return best_move or self.fallback