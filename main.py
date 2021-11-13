from os import system
import curses

TERMINAL_WIDTH, TERMINAL_HEIGHT = 150, 50
MENU_OPTIONS = ['Guess the number', "Rock paper scissor", "Tic Tac Toe", "Chess", "Quit"]

def initial_settings():
    """ Function setting up initial terminal settings like it's width nad height."""
    #Setting terminal width and height to 150x50
    command = f"printf '\e[8;{TERMINAL_HEIGHT};{TERMINAL_WIDTH}t'"
    system(command)

    stdscr = curses.initscr()

    curses.noecho() #Do not echo user inputs
    curses.cbreak() #Do note wait for user to press ENTER/RETURN to confirm input
    curses.curs_set(0) #Hide cursor
    

    if curses.has_colors(): #Check whether terminal supports color display
        curses.start_color()
    #If not maybe we should consider quitting game right here and display an error message

    return stdscr

def display_banner(stdscr):
    title_width, title_height = 93, 8
    banner = """
 _______           _______  _        _          _______  _______  _______  _______  _______ 
(  ____ \|\     /|(  ____ \( \      ( \        (  ____ \(  ___  )(       )(  ____ \(  ____ \\
| (    \/| )   ( || (    \/| (      | (        | (    \/| (   ) || () () || (    \/| (    \/
| (_____ | (___) || (__    | |      | |        | |      | (___) || || || || (__    | (_____ 
(_____  )|  ___  ||  __)   | |      | |        | | ____ |  ___  || |(_)| ||  __)   (_____  )
      ) || (   ) || (      | |      | |        | | \_  )| (   ) || |   | || (            ) |
/\____) || )   ( || (____/\| (____/\| (____/\  | (___) || )   ( || )   ( || (____/\/\____) |
\_______)|/     \|(_______/(_______/(_______/  (_______)|/     \||/     \|(_______/\_______)                                                                                               
    """
    #Centering the title 
    title_pos_x = TERMINAL_WIDTH//2 - title_width//2
    title_pos_y = TERMINAL_HEIGHT//2 - title_height - 10
    #Creating sub window just for title
    title_window = stdscr.subwin(title_height+5, title_width+5, title_pos_y, title_pos_x)

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) #Setting pair of color, in this case red font on black(gray) background
    title_window.attron(curses.color_pair(1)) #Initializing mentioned pair for colorful printing
    title_window.addstr(1, 1, banner) #printing title banner
    title_window.refresh() 
    title_window.attroff(curses.color_pair(1)) #Disbale colorful printing

def print_menu(menu_window, selected_row_idx):
    main_menu_width, main_menu_height = 40, 10
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    for index, el in enumerate(MENU_OPTIONS):
        x = main_menu_width//2 - len(el)//2
        y = 1 + index
        if index == selected_row_idx:
            menu_window.attron(curses.color_pair(2))
            menu_window.addstr(y, x, el)
            menu_window.attroff(curses.color_pair(2))
        else:
            menu_window.addstr(y, x, el)
    
    menu_window.refresh()


def main_menu(stdscr):
    main_menu_width, main_menu_height = 40, 10
    menu_window = stdscr.subwin(main_menu_height, main_menu_width, TERMINAL_HEIGHT//2, TERMINAL_WIDTH//2 - 20)
    menu_window.box()
    menu_window.keypad(True)

    current_row_idx = 0
    print_menu(menu_window, current_row_idx)

    while 1:
        key = menu_window.getch()        

        if key == curses.KEY_UP and current_row_idx > 0:
            current_row_idx -= 1
        elif key == curses.KEY_DOWN and current_row_idx < len(MENU_OPTIONS)-1:
            current_row_idx += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            stdscr.clear()
            menu_window.clear()
            stdscr.refresh()

            if(current_row_idx == 0):
                stdscr.addstr(0, 0, "Here goes {} implementation".format(MENU_OPTIONS[current_row_idx]))
            elif(current_row_idx == 1):
                stdscr.addstr(0, 0, "Here goes {} implementation".format(MENU_OPTIONS[current_row_idx]))
            elif(current_row_idx == 2):
                stdscr.addstr(0, 0, "Here goes {} implementation".format(MENU_OPTIONS[current_row_idx]))
            elif(current_row_idx == 3):
                stdscr.addstr(0, 0, "Here goes {} implementation".format(MENU_OPTIONS[current_row_idx]))
            elif(current_row_idx == 4):
                quit_game(stdscr)

            stdscr.refresh()
            stdscr.getch()
            

        print_menu(menu_window, current_row_idx)

        stdscr.refresh()

def quit_game(stdscr):
    curses.endwin() #Restore terminal normal mode
    exit(0)




       

    


if __name__ == "__main__":
    stdscr = initial_settings()
    display_banner(stdscr)
    main_menu(stdscr)
    