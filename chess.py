import curses
import client
import time
import chessboard
import copy


class ChessState(client.GameState):
    def __init__(self):
        self.game_id = 3
        self.board = []
        self.kings = []

    def populate_board(self):
        self.board = []

        pawn_y = 1
        fig_y = 0
        for team in range(2):
            for i in range(8):
                self.board.append(Pawn(i, pawn_y, bool(team)))

            self.board.append(Tower(0, fig_y, bool(team)))
            self.board.append(Tower(7, fig_y, bool(team)))
            self.board.append(Horse(1, fig_y, bool(team)))
            self.board.append(Horse(6, fig_y, bool(team)))
            self.board.append(Bishop(2, fig_y, bool(team)))
            self.board.append(Bishop(5, fig_y, bool(team)))
            self.board.append(Queen(3, fig_y, bool(team)))
            self.board.append(King(4, fig_y, bool(team)))

            pawn_y = 6
            fig_y = 7

    def draw_board(self, game_window: curses.window):
        chessboard.draw_board(game_window)
        for chesspiece in self.board:
            chesspiece.draw(game_window)

    def space_taken(self, tx, ty):
        for piece in self.board:
            px, py = piece.position_x, piece.position_y
            if px == tx and py == ty:
                return piece
        return False

    def check(self):
        attacking_color = False if client.playerID == 1 else True
        king_defend = ChessPiece
        for piece in self.board:
            if type(piece) == King and piece.color != attacking_color:
                king_defend = piece
        x, y = king_defend.position_x, king_defend.position_y
        for piece in self.board:
            if piece.color == attacking_color:
                if piece.can_attack(x, y):
                    return False
        return True



class ChessPiece:
    def __init__(self, x: int, y: int, color: bool):
        self.position_x = x
        self.position_y = y
        self.color = color
        self.has_moved = False

    def do_move(self, x, y):
        self.position_x = x
        self.position_y = y
        self.has_moved = True

    def do_attack(self, x, y):
        target = client.game.space_taken(x, y)
        client.game.board.remove(target)
        self.do_move(x, y)

    def can_move(self, x: int, y: int):
        raise NotImplemented

    def can_attack(self, x: int, y: int):
        self.can_move(x, y)


    def consider_order(self, x, y):
        approved = False
        board_backup = copy.deepcopy(client.game.board)
        if self.can_move(x, y):
            self.do_move(x, y)
            approved = True
        elif self.can_attack(x, y):
            self.do_attack(x, y)
            approved = True

        if approved:
            if client.game.check():
                client.send_game(client.game)
                return True
            else:
                client.game.board = board_backup
                return False

    def line_free(self, x, y, straight: bool, diagonal: bool, aggresive=False):
        delta = x - self.position_x, y - self.position_y
        if delta == (0, 0):
            return False
        if (0 in delta and straight) \
                or (abs(delta[0]) == abs(delta[1]) and diagonal):
            normal = sign(delta[0]), sign(delta[1])
            position = self.position_x, self.position_y
            while not (position[0] == x and position[1] == y):
                position = position[0] + normal[0], position[1] + normal[1]  # walking through
                if not client.game.space_taken(position[0], position[1]):  # checking path
                    continue
                if aggresive and position[0] == x and position[1] == y:  # is this what i kill?
                    return True
                return False
            if aggresive:  # you have found no enemy
                return False
            return True  # your path was clear
        return False  # you can't even move like that

    def symbol(self):
        return "E"

    def draw(self, game_window: curses.window):
        x, y = chessboard.game_to_board(self.position_x, self.position_y)
        if self.color:
            game_window.addstr(y, x, self.symbol(), curses.A_REVERSE)
        else:
            game_window.addstr(y, x, self.symbol())


class Pawn(ChessPiece):
    def __init__(self, x: int, y: int, color: bool):
        super().__init__(x, y, color)
        self.used_special = False

    def symbol(self):
        return "P"

    def do_move(self, x, y):
        if not self.has_moved and abs(y - self.position_y) == 2:
            self.used_special = True
        self.position_x = x
        self.position_y = y
        self.has_moved = True
        if y == (0 if self.color else 7):
            # promocja
            client.game.board.append(Queen(self.position_x, self.position_y, self.color))
            client.game.board.remove(self)


    def can_move(self, x: int, y: int):
        allowed_direction = -1 if self.color else 1
        if x == self.position_x:
            step_one = self.position_y + allowed_direction
            if not client.game.space_taken(self.position_x, step_one):
                if y == step_one:
                    return True
                elif not self.has_moved:
                    step_two = step_one + allowed_direction
                    if not client.game.space_taken(self.position_x, step_two):
                        if y == step_two:
                            return True
        return False

    def can_attack(self, x: int, y: int):
        allowed_direction = -1 if self.color else 1
        target_piece = client.game.space_taken(x, y)
        if y == self.position_y + allowed_direction and \
                (x == self.position_x + 1 or x == self.position_x - 1):
            if target_piece:
                if target_piece.color != self.color:
                    return True
            else:  # check en_passant
                target_piece = client.game.space_taken(x, self.position_y)
                if target_piece:
                    if target_piece.color != self.color and type(target_piece) == Pawn:
                        if target_piece.used_special:
                            backup_board = copy.deepcopy(client.game.board)
                            client.game.board.remove(target_piece)
                            self.do_move(x, y)
                            if not client.game.check():
                                client.game.board = backup_board
                                return False

                            client.send_game(client.game)
                            global my_turn
                            my_turn = False
                            return False

        return False


class Tower(ChessPiece):
    def symbol(self):
        return "T"

    def can_move(self, x, y):
        return self.line_free(x, y, straight=True, diagonal=False, aggresive=False)

    def can_attack(self, x: int, y: int):
        target = client.game.space_taken(x, y)
        if target:
            if target.color != self.color:
                return self.line_free(x, y, straight=True, diagonal=False, aggresive=True)
        return False


class Horse(ChessPiece):
    def symbol(self):
        return "H"

    def in_range(self, x, y):
        delta = abs(x - self.position_x), abs(y - self.position_y)
        return delta in [
            (2, 1),
            (1, 2)]

    def can_move(self, x: int, y: int):
        return self.in_range(x, y) and not client.game.space_taken(x, y)

    def can_attack(self, x: int, y: int):
        target = client.game.space_taken(x, y)
        if target:
            return target.color != self.color and self.in_range(x, y)
        return False


class Bishop(ChessPiece):
    def symbol(self):
        return "B"

    def can_move(self, x: int, y: int):
        return self.line_free(x, y, straight=False, diagonal=True, aggresive=False)

    def can_attack(self, x: int, y: int):
        target = client.game.space_taken(x, y)
        if target:
            if target.color != self.color:
                return self.line_free(x, y, straight=False, diagonal=True, aggresive=True)
        return False

class Queen(ChessPiece):
    def symbol(self):
        return "Q"

    def can_move(self, x: int, y: int):
        return self.line_free(x, y, straight=True, diagonal=True, aggresive=False)

    def can_attack(self, x: int, y: int):
        target = client.game.space_taken(x, y)
        if target:
            if target.color != self.color:
                return self.line_free(x, y, straight=True, diagonal=True, aggresive=True)
        return False

class King(ChessPiece):
    # def __init__(self, x: int, y: int, color: bool):
    #     super().__init__(x, y, color)
    def symbol(self):
        return "K"

    def in_range(self, x, y):
        delta = abs(x - self.position_x), abs(y - self.position_y)
        if delta == (0,0):
            return False
        if delta[0] <= 1 and delta[1] <= 1:
            return True

    def can_move(self, x: int, y: int):
        if not self.has_moved:  # Castle.
            target = client.game.space_taken(x, y)
            if target:
                if target.color == self.color and type(target) == Tower and not target.has_moved:
                    if self.line_free(x, y, straight=True, diagonal=False, aggresive=True):
                        # executing a castle move
                        if not client.game.check():
                            return False
                        board_backup = copy.deepcopy(client.game.board)
                        direction = sign(x - self.position_x)
                        self.do_move(self.position_x + direction, self.position_y)
                        if not client.game.check():
                            client.game.board = board_backup
                            return False
                        self.do_move(self.position_x + direction, self.position_y)
                        if not client.game.check():
                            client.game.board = board_backup
                            return False
                        target.do_move(self.position_x - direction, self.position_y)
                        if not client.game.check():
                            client.game.board = board_backup
                            return False

                        client.send_game(client.game)
                        global my_turn
                        my_turn = False
                        return False

        return self.in_range(x, y) and not client.game.space_taken(x, y)

    def can_attack(self, x: int, y: int):
        target = client.game.space_taken(x, y)
        if target:
            return target.color != self.color and self.in_range(x, y)
        return False


def sign(val: int):
    if val == 0:
        return 0
    return -1 if val < 0 else 1


def create_game(window: curses.window):
    client.start_connection('155.158.180.62', 1109)
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
        curses.BUTTON1_CLICKED )
        # curses.BUTTON2_CLICKED )
        # curses.BUTTON3_CLICKED |
        # curses.BUTTON4_CLICKED )
    window.keypad(True)
    game_loop(window, chat_window, game_window)


def refresh_chat(chat_window: curses.window, chat_string):
    chat_window.clear()
    for level, line in enumerate(client.chat):
        chat_window.addstr(level+1, 1, line)

    chat_window.addstr(chat_size_h-2, 1, chat_string)
    chat_window.box()
    chat_window.refresh()



selected = False
selected_piece = None
def game_interaction(x, y):
    global selected, selected_piece
    if not selected:
        piece = client.game.space_taken(x, y)
        if piece:
            if (piece.color and client.playerID == 1) \
                or (not piece.color and client.playerID == 2):  # player1 plays White player2 plays black
                selected = True
                # selected_x = x
                # selected_y = y
                selected_piece = piece
        return False
    else:
        selected = False
        return selected_piece.consider_order(x, y)


def clicking_support():
    try:
        _, total_x, total_y, _, _ = curses.getmouse()
    except curses.error:
        return False, False
    if chessboard.inside(total_x, total_y):
        # chess click
        bx, by = chessboard.total_to_board(total_x, total_y)
        gx, gy = chessboard.board_to_game(bx, by)
        return True, game_interaction(gx, gy)
    return False, False


def ascii_helper(value):
    try:
        c = chr(value)
    except ValueError:
        return False
    return True

my_turn = None
def game_loop(window: curses.window, chat_window: curses.window, game_window: curses.window):
    global my_turn
    client.game.draw_board(game_window)
    game_window.refresh()
    window.refresh()
    my_turn = True if client.playerID == 1 else False
    pturn = not my_turn
    chat_header = "P1: " if client.playerID == 1 else "P2: "
    chat_string = "" + chat_header
    while True:
        status = client.receive_data()
        # status = False
        if status:
            if status == 1:
                client.game.draw_board(game_window)

                game_window.refresh()
                my_turn = True
            elif status == 2:
                # Jeśli ten kod się odpali, to właśnie dostaliśmy wiadomość na chat.
                refresh_chat(chat_window, chat_string)

            elif status == 3:
                break
            # Jeśli wystarczy odświeżyć ekran, to można to zrobić tutaj.
            continue

        if my_turn != pturn:
            pturn = my_turn
            if my_turn:
                for piece in client.game.board:
                    if piece.color == (1 if client.playerID == 1 else 0) and type(piece) == Pawn:
                        piece.used_special = False
                window.addstr(chessboard.total_board_y - 1, chessboard.total_board_x, "YOUR TURN")
            else:
                window.addstr(chessboard.total_board_y - 1, chessboard.total_board_x, "WAIT     ")
            window.refresh()

        key = window.getch()
        if key == -1:
            time.sleep(.05)
            continue

        elif key == 27:
            client.close_connection()
            break

        elif key == curses.KEY_MOUSE:
            if not my_turn:
                continue

            show, turn_done = clicking_support()
            if show:
                client.game.draw_board(game_window)
                if selected:
                    # client.send_chat("debug")
                    bx, by = chessboard.game_to_board(selected_piece.position_x, selected_piece.position_y)
                    game_window.addstr(by, bx - 1, "[")
                    game_window.addstr(by, bx + 1, "]")
                game_window.refresh()
                window.refresh()
            if turn_done:
                my_turn = False
                continue

        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            client.send_chat(chat_string)
            chat_string = "" + chat_header
            refresh_chat(chat_window, chat_string)

        elif key == curses.KEY_BACKSPACE:
            chat_string = chat_string[:-1]
            if len(chat_string) < 4:
                chat_string = chat_header
            refresh_chat(chat_window, chat_string)

        elif ascii_helper(key):
            chat_string = chat_string + chr(key)
            refresh_chat(chat_window, chat_string)


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
    refresh_chat(chat_window, "")

    game_window = chessboard.create_board(window, third_w, center_h)
    chessboard.invert = client.playerID == 2

    return chat_window, game_window
