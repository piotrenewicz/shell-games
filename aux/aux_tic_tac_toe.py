import curses
from typing import Iterable


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


def launch_game(window: curses.window):
    multiline_print_center(["Gey", 'play'], window)
    window.getch()
    return


def main_menu(window: curses.window):
    options = {"Play": launch_game, "Quit": None}  # Selectable options
    options_keys = list(options.keys())  # List of selectable keys

    # Header and some space, unselectable
    unselectable_text = ["Tic-Tac-Toe", ""]
    lines = unselectable_text + options_keys  # Final printed list

    # Selectable lines in printed text
    selectable_range = list(
        range(len(unselectable_text), len(unselectable_text)+len(options_keys)))

    while True:
        # First selectable line highlighted
        selected_option = selectable_range[0]
        window.keypad(True)

        # Cycle through the menu
        key = None
        while not (key == curses.KEY_ENTER or key in [10, 13]):
            multiline_print_center(lines, window, selected_option)
            key = window.getch()

            if key == curses.KEY_UP and selected_option > selectable_range[0]:
                selected_option -= 1
            elif key == curses.KEY_DOWN and selected_option < selectable_range[-1]:
                selected_option += 1

        # Account for the unselectable lines and decrease the choice to match the selectables
        selected_option -= len(unselectable_text)

        selected_key = options_keys[selected_option]
        window.keypad(False)

        # Execute what's written in the dict under this key
        if selected_key.lower() == "quit":
            return
        options[selected_key](window)

    return
