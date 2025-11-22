# tests/integration_test.py
import pytest
import copy

from src.game.state import GameState, ALLOWED_MOVES
from src.game import logic
from typing import List

def print_board(board: List[List[int]]) -> str:
    return "\n".join([" ".join([f"{val:4d}" for val in row]) for row in board])

# --- Testy legalnych ruchów ---
def test_legal_moves_basic_moves_possible():
    # Plansza z ruchami, które NA PEWNO ZMIENIĄ planszę
    board = [
        [2, 0, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    state = GameState(board=board, seed=0)
    # Zgodnie z analizą: up, down, right są legalne. Left nie jest.
    assert "up" in state.legal_moves()
    assert "down" in state.legal_moves()
    assert "left" not in state.legal_moves()
    assert "right" in state.legal_moves() # <--- Zmienione na "in"


def test_legal_moves_no_moves_possible_full_board():
    board = [
        [2, 4, 8, 16],
        [32, 64, 128, 256],
        [512, 1024, 2, 4],
        [8, 16, 32, 64],
    ]
    state = GameState(board=board, seed=0)
    assert state.is_terminal() is True
    assert len(state.legal_moves()) == 0

def test_legal_moves_only_horizontal_merge_possible():
    # Plansza, gdzie tylko ruchy HORYZONTALNE są legalne (bo nastąpi merge)
    board = [
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    state = GameState(board=board, seed=0)
    # Zgodnie z analizą: left, right, down są legalne. Up nie jest.
    assert "left" in state.legal_moves()
    assert "right" in state.legal_moves()
    assert "up" not in state.legal_moves()
    assert "down" in state.legal_moves() # <--- Zmienione na "in"


# --- Testy kroku (step) na nielegalnym ruchu ---
def test_step_on_illegal_move_no_change():
    # Plansza, na której ruch 'up' niczego nie zmienia
    board = [
        [2, 4, 8, 16],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    initial_state = GameState(board=board, seed=0)
    initial_board_copy = copy.deepcopy(initial_state.board)
    
    # Próbujemy wykonać ruch, który jest nielegalny (bo nic się nie zmieni)
    # Ruch "up" dla tej planszy powinien być nielegalny, bo nic się nie zmienia.
    # Weryfikujemy to, symulując ruch i sprawdzając, czy plansza jest taka sama.
    assert "up" not in initial_state.legal_moves(), "Ruch 'up' niespodziewanie legalny dla tej planszy"
    
    res = initial_state.step("up", spawn=True) # spawn=True nie zadziała, bo moved=False
    assert initial_state.board == initial_board_copy, "Plansza zmieniła się mimo nielegalnego ruchu"
    assert res.reward == 0, "Reward nie powinien być zero dla nielegalnego ruchu"
    assert res.done == initial_state.is_terminal(), "Stan terminalny źle wyliczony po nielegalnym ruchu"


# --- Testy terminalności ---
def test_terminal_state_win():
    board = [
        [2048, 2, 4, 8],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    state = GameState(board=board, seed=0)
    assert state.is_terminal() is True
    assert logic.game_state(state.board) == 'win'

def test_terminal_state_lose():
    board = [
        [2, 4, 8, 16],
        [32, 64, 128, 256],
        [512, 1024, 2, 4],
        [8, 16, 32, 64],
    ]
    state = GameState(board=board, seed=0)
    assert state.is_terminal() is True
    assert logic.game_state(state.board) == 'lose'

def test_terminal_state_not_over():
    board = [
        [2, 4, 8, 0],
        [16, 32, 64, 128],
        [256, 512, 1024, 2],
        [4, 8, 16, 32],
    ]
    state = GameState(board=board, seed=0)
    assert state.is_terminal() is False
    assert logic.game_state(state.board) == 'not over'