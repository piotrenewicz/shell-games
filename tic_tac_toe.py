import curses
from typing import Iterable
import client


class TicTacToeState(client.GameState):
    def __init__(self):
        self.game_id = 2
        self.board = [[0]*board_size for _ in range(board_size)]


def create_game(window: curses.window):
    client.start_connection('155.158.180.62', 1109)
    client.game = TicTacToeState()
    client.send_game(client.game)
    launch_game(window)


def join_game(window: curses.window):
    launch_game(window)


board_size = 5  # size of the board, A, usually 3, 5 or 7
points_to_win = board_size
# A*A array of zeros, ones and twos, representing empty field, X and O respectively
# board = [[0]*board_size for _ in range(board_size)]
# 1=X is for player 1, 2=O is for player 2, 0=" " is for free field
symbols = {1: "X", 2: "O", 0: " "}
# current_player = 1  # Default first player

height_step = 2  # Skip 1 character when printing horizontal lines of the board
width_step = 4  # Skip 3 characters when printing vertical lines of the board


def get_y_for_row(row: int, center_y: int):
    """Get absolute Y position on the screen for the Nth row on the player's table"""
    return center_y + (row - board_size//2)*height_step


def get_x_for_column(column: int, center_x: int):
    """Get absolute X position on the screen for the Nth column on the player's table"""
    return center_x + (column - board_size//2)*width_step


def multiline_print_center(lines: "Iterable[str] | str", window: curses.window, highlights: "Iterable[int] | int" = None):
    # Convert to list if str was given
    if isinstance(lines, str):
        lines = lines.split("\n")
    # Convert highlights to list
    if not isinstance(highlights, Iterable):
        highlights = [highlights]

    # Some variables to make life easier
    num_lines = len(lines)
    max_height, max_width = window.getmaxyx()
    center_h, center_w = max_height//2, max_width//2

    # Check if the text will fit into the screen
    assert all([len(line) <= max_width for line in lines]
               ), f"Some or all lines are wider than the screen! Max line character count is {max_width}."
    assert len(
        lines) <= max_height, f"Too many lines! Max line count is {max_height}."

    window.clear()
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # Print lines
    for i, line in enumerate(lines):
        height_bias = num_lines//2-i
        width_bias = len(line)//2

        # Choose coloring for hightlighted and non-hightlighted lines
        color_pair_num = 2 if i in highlights else 0
        window.addstr(center_h-height_bias, center_w -
                      width_bias, line, curses.color_pair(color_pair_num))

    return


def draw_symbols(window: curses.window):
    max_height, max_width = window.getmaxyx()
    center_h, center_w = max_height//2, max_width//2

    for i, line in enumerate(client.game.board):
        for j, value in enumerate(line):
            symbol = symbols[value]
            symbol_y = get_y_for_row(i, center_h)
            symbol_x = get_x_for_column(j, center_w)
            window.addstr(symbol_y, symbol_x, symbol)

    return


def select_square(window: curses.window):
    max_height, max_width = window.getmaxyx()
    center_h, center_w = max_height//2, max_width//2

    # Automatically set the symbol to the center
    selected_row, selected_column = board_size//2, board_size//2

    window.keypad(True)
    key = None

    draw_board(window)

    symbol = symbols[client.playerID]
    symbol_y = None  # Absolute coordinate on the board
    symbol_x = None  # Absolute coordinate on the board
    symbol_placed = False
    while not symbol_placed:
        if symbol_x is not None and symbol_y is not None:
            window.addstr(symbol_y, symbol_x, str(
                client.game.board[selected_row][selected_column]))
        draw_symbols(window)

        # Select symbol, calculate the correct position on the board
        symbol_y = get_y_for_row(selected_row, center_h)
        symbol_x = get_x_for_column(selected_column, center_w)

        window.addstr(symbol_y, symbol_x, symbol,
                      curses.A_BLINK | curses.A_REVERSE)

        # Move around the board
        key = window.getch()
        if (key == curses.KEY_ENTER or key in [10, 13]):
            if client.game.board[selected_row][selected_column] == 0:
                client.game.board[selected_row][selected_column] = client.playerID
                symbol_placed = True
        elif key == curses.KEY_UP:
            selected_row -= 1
        elif key == curses.KEY_DOWN:
            selected_row += 1
        elif key == curses.KEY_RIGHT:
            selected_column += 1
        elif key == curses.KEY_LEFT:
            selected_column -= 1

        # Protection against overflow and underflow
        selected_row = max(min(selected_row, board_size-1), 0)
        selected_column = max(min(selected_column, board_size-1), 0)

    window.keypad(False)

    return


def draw_board(window: curses.window):
    window.clear()
    max_height, max_width = window.getmaxyx()
    center_h, center_w = max_height//2, max_width//2

    hline_length = board_size*width_step-1
    vline_length = board_size*height_step-1

    hline_init_y = center_h-board_size * height_step//2
    hline_init_x = center_w - hline_length//2

    vline_init_y = center_h - vline_length//2
    vline_init_x = center_w - board_size * width_step//2

    for i in range(1, board_size):
        window.hline(hline_init_y+i*height_step, hline_init_x,
                     curses.ACS_HLINE, hline_length)

    for i in range(1, board_size):
        window.vline(vline_init_y, vline_init_x+i*width_step,
                     curses.ACS_VLINE, vline_length)

    return


def check_window(iterable: "list[int]"):
    all_ones = all(elem == 1 for elem in iterable)
    all_twos = all(elem == 2 for elem in iterable)

    return 1 if all_ones else 2 if all_twos else 0


def check_rows(board: "list[list[int]]", x_to_win: int, checks_per_line: int):
    for row in board:
        for i in range(checks_per_line):
            window = row[i:x_to_win+i]
            result = check_window(window)
            if result:
                return result
    return 0


def check_columns(board: "list[list[int]]", x_to_win: int, checks_per_line: int):
    n_columns = len(board[0])
    for i in range(n_columns):
        # Transpose a column to be like a row, and do exactly the same what with a row
        column = [row[i] for row in board]
        for i in range(checks_per_line):
            window = column[i:x_to_win+i]
            result = check_window(window)
            if result:
                return result
    return 0


def check_descending_diagonals(board: "list[list[int]]", x_to_win: int, checks_per_line: int):
    for row_bias in range(checks_per_line):
        for column_bias in range(checks_per_line):
            # End looping over biases
            diagonal = []
            for i in range(x_to_win):
                diagonal.append(board[row_bias+i][column_bias+i])
            result = check_window(diagonal)
            if result:
                return result
    return 0


def check_ascending_diagonals(board: "list[list[int]]", x_to_win: int, checks_per_line: int):
    last_index = len(board)-1
    for row_bias in range(checks_per_line):
        for column_bias in range(checks_per_line):
            # End looping over biases
            diagonal = []
            for i in range(x_to_win):
                diagonal.append(board[last_index-row_bias-i][column_bias+i])
            result = check_window(diagonal)
            if result:
                return result
    return 0


def get_winner(board: "list[list[int]]", x_to_win: int):
    # If x_to_win != board_size, we have to create a sliding window
    checks_per_line = len(board)-x_to_win+1
    winner = check_rows(board, x_to_win, checks_per_line) or \
        check_columns(board, x_to_win, checks_per_line) or \
        check_ascending_diagonals(board, x_to_win, checks_per_line) or \
        check_descending_diagonals(board, x_to_win, checks_per_line)

    return winner


def win(winner: int, window: curses.window):
    window.clear()
    multiline_print_center(
        ["Congratulations!", f"Player {winner}-{symbols[winner]} is the winner"], window)
    window.getch()

    return


def launch_game(window: curses.window):
    my_turn = True if client.playerID == 1 else False
    while True:
        status = client.receive_data()
        if status:
            if status == 1:
                my_turn = True
            elif status == 3:
                exit()

        if my_turn:
            if not get_winner(client.game.board, points_to_win):
                select_square(window)
            client.send_game(client.game)
            my_turn = False
        if (winner := get_winner(client.game.board, points_to_win)):
            break
    win(winner, window)


#
# def main_menu(window: curses.window):
#     options = {"Play": launch_game, "Quit": None}  # Selectable options
#     options_keys = list(options.keys())  # List of selectable keys
#
#     # Header and some space, unselectable
#     unselectable_text = ["Tic-Tac-Toe", ""]
#     lines = unselectable_text + options_keys  # Final printed list
#
#     # Selectable lines in printed text
#     selectable_range = list(
#         range(len(unselectable_text), len(unselectable_text)+len(options_keys)))
#
#     while True:
#         # First selectable line highlighted
#         selected_option = selectable_range[0]
#         window.keypad(True)
#
#         # Cycle through the menu
#         key = None
#         while not (key == curses.KEY_ENTER or key in [10, 13]):
#             multiline_print_center(lines, window, selected_option)
#             key = window.getch()
#
#             if key == curses.KEY_UP and selected_option > selectable_range[0]:
#                 selected_option -= 1
#             elif key == curses.KEY_DOWN and selected_option < selectable_range[-1]:
#                 selected_option += 1
#
#         # Account for the unselectable lines and decrease the choice to match the selectables
#         selected_option -= len(unselectable_text)
#
#         selected_key = options_keys[selected_option]
#         window.keypad(False)
#
#         # Execute what's written in the dict under this key
#         if selected_key.lower() == "quit":
#             return
#         options[selected_key](window)
#
#     return


# =====added here during merge to keep this code compatible with server=======


# ============================================================================

#
# def welcome(window: curses.window):
#     lines = ["Welcome to Tic-Tac-Toe game!",
#              "", "Press any key to continue"]
#     multiline_print_center(lines, window)
#
#     # Press any key to continue
#     window.getch()


# def main(window: curses.window):
#     # welcome(window)
#     main_menu(window)

#
# if __name__ == "__main__":
#     main()
