import curses
from random import randint

TERMINAL_WIDTH, TERMINAL_HEIGHT = 150, 50

number_to_guess = lambda: randint(1, 100)

def display_title(stdscr):
    title = "GUESS THE NUMBER"
    mini_game_title = stdscr.subwin(5, 40, TERMINAL_HEIGHT//2 - 20, TERMINAL_WIDTH//2 - 40)
    mini_game_title.attron(curses.color_pair(1))
    mini_game_title.box()
    mini_game_title.addstr(2, 20 - len(title)//2, title)
    mini_game_title.attroff(curses.color_pair(1))
    mini_game_title.refresh()

def display_chat(stdscr):
    chat_window = stdscr.subwin(45, 40, 2, 100)
    chat_window.box()
    chat_window.refresh()

def get_user_input(stdscr, gameplay_window):
    curses.echo()
    gameplay_window.addstr(1, 40 - len("YOUR NUMBER")//2, "YOUR NUMBER")
    

    while 1:
        user_input = str(gameplay_window.getstr(3, 39, 2))
        gameplay_window.addstr(1, 1, user_input)

        if not user_input.isnumeric():
            continue
        else:
            pass
            #Sent input to server




def guess_the_number(stdscr):
    player_1_score, player_2_score = 0, 0

    display_title(stdscr)
    display_chat(stdscr)

    #Results box
    game_results = stdscr.subwin(10, 80, TERMINAL_HEIGHT//2 - 10, TERMINAL_WIDTH//2 - 60)
    game_results.addstr(1, 40 - len("RESULTS")//2, "RESULTS")
    game_results.box()

    game_results.attron(curses.color_pair(1))
    game_results.addstr(3, 10 - len("PLAYER 1")//2, "PLAYER 1")
    game_results.addstr(3, 70 - len("PLAYER 1")//2, "PLAYER 2")
    game_results.attroff(curses.color_pair(1))

    game_results.addstr(5, 9 - len(str(player_1_score))//2, str(player_1_score))
    game_results.addstr(5, 69 - len(str(player_2_score))//2, str(player_2_score))
    
    game_results.refresh()

    #Gameplay box
    gameplay_window = stdscr.subwin(10, 80, TERMINAL_HEIGHT//2 + 5, TERMINAL_WIDTH//2 - 60)
    gameplay_window.box()
    gameplay_window.refresh()  

    get_user_input(stdscr, gameplay_window) 

    
    stdscr.getch()



