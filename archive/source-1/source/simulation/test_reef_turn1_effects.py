"""The turn-1 result is derived from the card capability blocks, not hardcoded."""
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)


def _have():
    try:
        import openpyxl; return True
    except Exception:
        return False


def test_gate_tally_is_data_driven():
    if not _have():
        print("SKIP: openpyxl not installed"); return
    import reef_turn1_effects as T
    from mechanisms import card_effects as CE
    board, trace, upkeep = T.run("protect")
    icons = CE.available_icons(board)
    # role passive (oxygen) + cultivator-boosted Filterweed (oxygen) = 2; conditional Knowledge gain = 1
    assert icons.get("oxygen") == 2, icons
    assert icons.get("knowledge") == 1, icons
    # roles assigned from the each_player_chooses block
    assert board.players[0].role_id and board.players[1].role_id
    # the gate is evaluated and closed (1 Knowledge short)
    assert any(k == "GATE" and "CLOSED" in d for k, _w, d in trace)


if __name__ == "__main__":
    test_gate_tally_is_data_driven(); print("PASS")
