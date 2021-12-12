import curses
import client
from time import sleep
from random import randint
from main import quit_game

TERMINAL_WIDTH, TERMINAL_HEIGHT = 150, 50
HOST = '127.0.0.1'
PORT = 1109

class GuessState(client.GameState):
    def __init__(self):
        self.number_to_guess = randint(1, 100)
        self.game_id = 0
        self.player_scores = [0, 0]
        self.player_numbers = ["", ""]
        self.player_won = 0


def create_game(stdscr):
    client.start_connection(HOST, PORT)
    client.game = GuessState()
    client.send_game(client.game)
    guess_the_number(stdscr)

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

    return chat_window

def check_answer():
    return int(client.game.player_numbers[client.playerID - 1]) == client.game.number_to_guess
        



def get_user_input(stdscr, gameplay_window, chat_window):
    curses.echo()
    player_turn = client.playerID == 1
    user_input = ""
    client.send_chat(str(client.game.number_to_guess))
    while 1:
        sleep(.05)
        gameplay_window.addstr(1, 1, ' '*38)
        status = client.receive_data()            
        
        if status == 2:
            chat_window.addstr(1,1, "\n|".join(client.chat))
            chat_window.refresh()
        elif status == 3:
            client.close_connection()
            quit_game(stdscr)

        if player_turn:            
            gameplay_window.addstr(1, 40 - len("YOUR NUMBER")//2, "YOUR NUMBER")
            #user_input = str(gameplay_window.getstr(3, 39, 2))
            c = stdscr.getch()
            if c == curses.KEY_ENTER or c == 10 or c == 13:
                client.send_chat(user_input)           
                client.game.player_numbers[client.playerID - 1] = user_input
                player_turn = False
                if check_answer():
                    client.game.player_won = client.playerID
                    gameplay_window.addstr(5, 40 - len('You won!')//2, "You won!")
                client.send_game(client.game)
                user_input = ""
            elif c != -1:
                user_input = user_input + chr(c)
                gameplay_window.addstr(3, 39, user_input)
            
            #client.send_chat(str(aux_num))                
        else:
            gameplay_window.addstr(1, 40 - len("OTHER INPUT")//2, "OTHER INPUT")
            gameplay_window.addstr(3, 39, "  ")
            if status == 1:
                player_turn = True
                if client.game.player_won:
                    gameplay_window.addstr(5, 40 - len('You lost!')//2, "You lost!")
               

        gameplay_window.refresh()


def join_game(stdscr):
    guess_the_number(stdscr)










def guess_the_number(stdscr):

    display_title(stdscr)
    chat_window = display_chat(stdscr)


    #Results box
    game_results = stdscr.subwin(10, 80, TERMINAL_HEIGHT//2 - 10, TERMINAL_WIDTH//2 - 60)
    game_results.addstr(1, 40 - len("RESULTS")//2, "RESULTS")
    game_results.box()

    game_results.attron(curses.color_pair(1))
    game_results.addstr(3, 10 - len("PLAYER 1")//2, "PLAYER 1")
    game_results.addstr(3, 70 - len("PLAYER 1")//2, "PLAYER 2")
    game_results.attroff(curses.color_pair(1))

    game_results.addstr(5, 9 - len(str(client.game.player_scores[0]))//2, str(client.game.player_scores[0]))
    game_results.addstr(5, 69 - len(str(client.game.player_scores[1]))//2, str(client.game.player_scores[1]))
    
    game_results.refresh()

    #Gameplay box
    gameplay_window = stdscr.subwin(10, 80, TERMINAL_HEIGHT//2 + 5, TERMINAL_WIDTH//2 - 60)
    gameplay_window.box()
    gameplay_window.refresh()  

    get_user_input(stdscr, gameplay_window, chat_window) 

    
    stdscr.getch()




