import curses
import client
import time
import chessboard


class ChessState(client.GameState):
    def __init__(self):
        self.game_id = 3
        self.board = []

    def populate_board(self):
        self.board = []
        self.board.append(King(4, 4, True))

    def draw_board(self, game_window: curses.window):
        chessboard.draw_board(game_window)
        for chesspiece in self.board:
            chesspiece.draw(game_window)


class ChessPiece:
    def __init__(self, x: int, y: int, color: bool):
        self.position_x = x
        self.position_y = y
        self.color = color

    def can_move(self, x: int, y: int):
        raise NotImplemented

    def can_attack(self, x: int, y: int):
        self.can_move(x, y)

    def symbol(self):
        return "E"

    def draw(self, game_window: curses.window):
        x, y = chessboard.game_to_board(self.position_x, self.position_y)
        game_window.addstr(y, x, self.symbol())


class King(ChessPiece):
    # def __init__(self, x: int, y: int, color: bool):
    #     super().__init__(x, y, color)
    def symbol(self):
        return "K"



def create_game(window: curses.window):
    client.start_connection('127.0.0.1', 1109)
    client.game = ChessState()
    client.game.populate_board()
    client.send_game(client.game)
    begin(window)
#     begin


def join_game(window: curses.window):
    begin(window)
#     begin


def begin(window: curses.window):
    chat_window, game_window = first_draw(window)
    curses.mousemask(
        curses.BUTTON1_CLICKED | 
        curses.BUTTON2_CLICKED | 
        curses.BUTTON3_CLICKED | 
        curses.BUTTON4_CLICKED )
    window.keypad(True)
    game_loop(window, chat_window, game_window)


def refresh_chat(chat_window: curses.window):
    for level, line in enumerate(client.chat):
        chat_window.addstr(level+1, 1, line)
    chat_window.refresh()


def clicking_support():
    _, total_x, total_y, _, _ = curses.getmouse()
    if chessboard.inside(total_x, total_y):
        # chess click
        client.send_chat("board")
    elif total_x in range(chat_loc_x, chat_loc_x+chat_size_w) and total_y in range(chat_loc_y, chat_loc_y+chat_size_h):
        # chat click
        client.send_chat("chat")


def game_loop(window: curses.window, chat_window: curses.window, game_window: curses.window):

    while True:
        status = client.receive_data()
        # status = False
        if status:
            if status == 1:
                # Jeśli ten kod się odpali, to właśnie dostaliśmy stan gry, od przeciwnika.
                pass
            elif status == 2:
                # Jeśli ten kod się odpali, to właśnie dostaliśmy wiadomość na chat.
                refresh_chat(chat_window)

            elif status == 3:
                break
            # Jeśli wystarczy odświeżyć ekran, to można to zrobić tutaj.
            continue

        key = window.getch()
        if key == -1:
            time.sleep(.05)
            continue

        if key == ord('q'):
            client.close_connection()
            break

        if key == curses.KEY_MOUSE:
            clicking_support()


        client.game.draw_board(game_window)
        game_window.refresh()
        window.refresh()


chat_loc_x = 100
chat_loc_y = 2
chat_size_w = 40
chat_size_h = 45

def first_draw(window: curses.window):
    window.clear()

    max_height, max_width = window.getmaxyx()
    center_h = max_height // 2
    third_w = max_width // 3

    chat_window = window.subwin(chat_size_h, chat_size_w, chat_loc_y, chat_loc_x)
    chat_window.box()
    chat_window.refresh()

    game_window = chessboard.create_board(window, third_w, center_h)
    chessboard.invert = client.playerID == 2

    return chat_window, game_window
