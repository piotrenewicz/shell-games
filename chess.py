import curses
import client


class ChessState(client.GameState):
    def __init__(self):
        self.game_id = 3


def create_game(window: curses.window):
    client.start_connection('127.0.0.1', 1109)
    client.game = ChessState()
    client.send_game(client.game)
#     begin


def join_game(window: curses.window):
    pass
#     begin
