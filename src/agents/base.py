from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol

class SupportGameState(Protocol):
    def __init__(self):
        self.board = None

    def legal_moves(self) -> list[str]: ...
    def clone(self) -> "SupportGameState": ...
    def step(self, move: str, spawn: bool = True): ...

class Agent(ABC):
    @abstractmethod
    def choose_move(self, state: SupportGameState) -> str:
        """
        Zwraca nazwę ruchu: "up" | "down" | "left" | "right"
        """

        raise NotImplementedError