from aux.aux_tic_tac_toe import *
import curses


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
