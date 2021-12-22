import curses
import client
from time import sleep
from random import randint
from main import quit_game

TERMINAL_WIDTH, TERMINAL_HEIGHT = 150, 50
HOST = '155.158.180.62'
PORT = 1109

class GuessState(client.GameState):
    def __init__(self):
        self.number_to_guess = randint(1, 100)
        self.game_id = 0
        self.player_scores = [0, 0]
        self.player_numbers = ["", ""]
        self.player_won = 0
        self.wins_to_end = 2

    def end_a_match(self, stdscr, window):
        if self.player_scores[0] == self.wins_to_end:
            display_title(window, end = True)

            while 1:
                sleep(.5)
                c = stdscr.getch()
                if c == curses.KEY_ENTER or c == 10 or c == 13:
                    quit_game(stdscr)
        elif self.player_scores[1] == self.wins_to_end:
            display_title(window, end = True)

            while 1:
                sleep(.5)
                c = stdscr.getch()
                if c == curses.KEY_ENTER or c == 10 or c == 13:
                    quit_game(stdscr)

    def generate_new_number(self):
        self.number_to_guess = randint(1, 100)
            


def create_game(stdscr):
    client.start_connection(HOST, PORT)
    client.game = GuessState()
    client.send_game(client.game)
    guess_the_number(stdscr)

def join_game(stdscr):
    guess_the_number(stdscr)

def display_title(window, end = False):
    """Display mini game title or info when game is finished"""

    window.erase()
    title = "GUESS THE NUMBER"
    window.attron(curses.color_pair(1))
    window.box()
    if end:
        window.addstr(2, 20 - len("GAME OVER")//2, "GAME OVER")
    else:
        window.addstr(2, 20 - len(title)//2, title)
        window.attroff(curses.color_pair(1))
    window.refresh()

def display_chat(window):
    """Displays chat window and it's content"""
    window.refresh()

def display_chat_text_field(window):
    window.refresh()

def display_results(window):
    """Displays players scores"""
    window.erase()
    window.addstr(1, 40 - len("RESULTS")//2, "RESULTS")
    window.box()

    window.attron(curses.color_pair(1))
    window.addstr(3, 10 - len("PLAYER 1")//2, "PLAYER 1")
    window.addstr(3, 70 - len("PLAYER 1")//2, "PLAYER 2")
    window.attroff(curses.color_pair(1))

    window.addstr(5, 9 - len(str(client.game.player_scores[0]))//2, str(client.game.player_scores[0]))
    window.addstr(5, 69 - len(str(client.game.player_scores[1]))//2, str(client.game.player_scores[1]))
    
    window.refresh()

def check_answer():
    return int(client.game.player_numbers[client.playerID - 1]) == client.game.number_to_guess
        
def gameplay(stdscr, gameplay_window, chat_window, results_window, chat_text_field):
    player_turn = client.playerID == 1
    to_send = ""
    user_input = ""
    gameplay_window.addstr(5, 2, " "*37)
    flag = True

    while 1:
        sleep(.05)
        gameplay_window.addstr(1, 1, ' '*38)
        status = client.receive_data()            
        
        #Chat
        if status == 2:
            chat_window.addstr(1,1, "\n|".join(client.chat))
            chat_window.refresh()
        elif status == 3:
            client.close_connection()
            quit_game(stdscr)

        #Player's input    
        if player_turn:            
            display_gameplay(gameplay_window, 0)
            #user_input = str(gameplay_window.getstr(3, 39, 2))
            c = gameplay_window.getch()
            if c == curses.KEY_ENTER or c == 10 or c == 13:
                if flag == False:
                    client.send_chat(to_send)
                    to_send = ""
                else:
                    gameplay_window.addstr(3, 39, "  ")
                    client.send_chat(user_input)           
                    client.game.player_numbers[client.playerID - 1] = user_input
                    player_turn = False
                    if check_answer():
                        client.game.player_scores[client.playerID - 1] += 1
                        display_gameplay(gameplay_window, 2)
                        display_results(results_window)
                        client.game.generate_new_number()
                        client.game.end_a_match(stdscr, title_window)
                    client.send_game(client.game)
                user_input = ""
            #if key different than ENTER/RETURN
            elif c != -1:
                #if KEY '/' -> switch to chat
                if c == 47:
                    flag = not flag
                    user_input = ""
                    to_send = ""
                #Number input
                if flag and c in range(48, 58):
                    user_input = user_input + chr(c)
                    gameplay_window.addstr(3, 39, user_input)
                #Chat input
                elif flag == False:

                    to_send = to_send + chr(c)
                    chat_text_field.addstr(1, 1, " "*30)
                    chat_text_field.addstr(1, 1, to_send)
                    chat_text_field.refresh()
            
            #client.send_chat(str(aux_num))

        #Other's player input                
        else:
            display_gameplay(gameplay_window, 1)
            if status == 1:
                player_turn = True
                if client.game.player_won:
                    gameplay_window.addstr(5, 40 - len('You lost!')//2, "You lost!")
               

        gameplay_window.refresh()

def display_gameplay(window, state = 0):
    window.addstr(1, 2, " "*70)
    if state == 0:     
        window.addstr(1, 40 - len("YOUR NUMBER")//2, "YOUR NUMBER")
        window.addstr(5, 2, " "*70)
    elif state == 1:
        window.addstr(1, 40 - len("PLAYER 2 INPUT")//2, "PLAYER 2 INPUT")
    elif state == 3:
        pass
    else:
        window.addstr(5, 2, " "*70)
        window.addstr(5, 40 - len('You guessed the number!')//2, "You guessed the number!")

    window.box()
    window.refresh() 


def guess_the_number(stdscr):

    title_window = stdscr.subwin(5, 40, TERMINAL_HEIGHT//2 - 20, TERMINAL_WIDTH//2 - 40)
    chat_window = stdscr.subwin(40, 40, 2, 100)
    chat_text_field = stdscr.subwin(5, 40, 42, 100)
    results_window = stdscr.subwin(10, 80, TERMINAL_HEIGHT//2 - 10, TERMINAL_WIDTH//2 - 60)
    gameplay_window = stdscr.subwin(10, 80, TERMINAL_HEIGHT//2 + 5, TERMINAL_WIDTH//2 - 60)
    
    display_title(title_window)
    display_chat(chat_window)
    display_results(results_window)  
    display_chat_text_field(chat_text_field)

    gameplay(stdscr, gameplay_window, chat_window, results_window, chat_text_field) 

    
    stdscr.getch()