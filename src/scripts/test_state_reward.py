import pytest
from src.game.state import GameState

def test_merge_reward_left_2_plus_2():
    b = [[2,2,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    s = GameState(seed=1, board=b, score=0)
    res = s.step("left", spawn=False)
    assert s.board[0][0] == 4 and s.board[0][1] == 0
    assert res.reward == 4
    assert s.score == 4

def test_no_spawn_when_false():
    s = GameState(seed=1)
    empty_before = len(s.empty_cells())
    s.step("left", spawn=False)
    assert len(s.empty_cells()) == empty_before  # brak nowej płytki

def test_illegal_move_no_change():
    b = [[2,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    s = GameState(seed=1, board=b)
    res = s.step("left", spawn=False)
    assert res.reward == 0
    assert s.board == b