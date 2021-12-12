import curses

_height_step = 2  # Skip 1 character when printing horizontal lines
_width_step = 4  # Skip 3 characters when printing vertical lines
board_size = 8
total_board_x, total_board_y = None, None
invert = False


def perform_invert(x, y):
    if invert:
        x -= board_size - 1
        y -= board_size - 1
        x, y = -x, -y

    return x, y


def board_to_game(x, y):
    x, y = (x-1) // _width_step, (y-1) // _height_step
    return perform_invert(x, y)


def game_to_board(x, y):
    x, y = perform_invert(x, y)
    x, y = x * _width_step, y * _height_step
    x, y = x + _width_step // 2, y + _height_step // 2
    return x, y

def total_to_board(x, y):
    return x - total_board_x, y - total_board_y

def inside(x, y):
    x, y = total_to_board(x, y)
    x, y = board_to_game(x, y)
    # try:
    #     _x, _y = game_to_board(x, y)
    #     game_window.addstr(_y, _x, "X")
    #     game_window.refresh()
    # except:
    #     pass
    return x in range(board_size) and y in range(board_size)


# game_window = curses.window


def draw_board(game_window: curses.window):
    hline_length = board_size * _width_step - 1
    vline_length = board_size * _height_step - 1

    game_window.clear()
    game_window.box()

    for i in range(1, board_size):
        game_window.hline(0 + i * _height_step, 1,
                          curses.ACS_HLINE, hline_length)

    for i in range(1, board_size):
        game_window.vline(1, 0 + i * _width_step,
                          curses.ACS_VLINE, vline_length)

    game_window.refresh()
    # return game_window


def create_board(window: curses.window, x, y):
    global total_board_x, total_board_y
    total_board_y, total_board_x = y - board_size*_height_step // 2, x - board_size*_width_step // 2
    hline_length = board_size * _width_step - 1
    vline_length = board_size * _height_step - 1

    # hline_init_y = center_h - board_size * height_step // 2
    # hline_init_x = center_w - hline_length // 2
    #
    # vline_init_y = center_h - vline_length // 2
    # vline_init_x = center_w - board_size * width_step // 2

    # global game_window
    game_window = window.subwin(vline_length + 2, hline_length + 2,
                                total_board_y, total_board_x)
    draw_board(game_window)
    return game_window