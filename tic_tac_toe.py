from aux.aux_tic_tac_toe import *
import curses

# =====added here during merge to keep this code compatible with server=======
import client

class TicTacToeState(client.GameState):
    def __init__(self):
        self.game_id = 2

def create_game(window: curses.window):
    client.start_connection('127.0.0.1', 1109)
    client.game = TicTacToeState()
    client.send_game(client.game)
    main(window)
    
def join_game(window: curses.window):
    main(window)
# ============================================================================
    

def welcome(window: curses.window):
    lines = ["Welcome to Tic-Tac-Toe game!",
             "", "Press any key to continue"]
    multiline_print_center(lines, window)

    # Press any key to continue
    window.getch()


def main(window: curses.window):
    welcome(window)
    main_menu(window)


if __name__ == "__main__":
    main()
