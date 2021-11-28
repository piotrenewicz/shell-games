import socket
import pickle
import os


clear = lambda: os.system('clear')
host = '127.0.0.1'
port = 1109
pname = None
your_turn = None
class GameState:
    chat = ["Initial message",]
    def add_message(self, message: str):
        self.chat.append(message)


game = GameState()


def create_game(s: socket.socket):
    global game, pname, your_turn
    your_turn = 0
    pname = 'HOST'
    game = GameState()
    raw_game = pickle.dumps(game.chat, protocol=pickle.HIGHEST_PROTOCOL)
    s.sendall(raw_game)


def recieve_game(s: socket.socket):
    global game, pname, your_turn
    your_turn = 1
    pname = 'GUEST'
    raw_game = s.recv(1024)
    game.chat = pickle.loads(raw_game)


def game_loop(s: socket.socket):
    global game, your_turn
    game_running = True
    print(pname)
    while game_running:
        if your_turn:
            message = input("your turn: ")
            game.add_message("".join(['[', pname, '] ', message]))
            s.sendall(pickle.dumps(game.chat, protocol=pickle.HIGHEST_PROTOCOL))
            your_turn = 0
        else:
            # del game
            game.chat = pickle.loads(s.recv(1024))
            clear()
            for msg in game.chat:
                print(msg)
            your_turn = 1


def start_connection():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        player_id = s.recv(1024)
        if player_id == b'1':
            create_game(s)
        elif player_id == b'2':
            recieve_game(s)
        game_loop(s)


if __name__ == '__main__':
    start_connection()