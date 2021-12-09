import socket
import pickle
import os
import time


clear = lambda: os.system('clear')
host = '127.0.0.1'
port = 1109
playerID = None
server_connection = None# socket.socket()
chat = []

class GameState:
    def __init__(self):
        pass


game = GameState()


def send_data(protocol: int, data: bytes):
    payload_size = len(data)
    payload = protocol.to_bytes(1, "little", signed=False) + payload_size.to_bytes(4, "little", signed=False) + data
    server_connection.sendall(payload)


def send_game(game: GameState):
    raw_game = pickle.dumps(game, protocol=4)
    send_data(1, raw_game)


def send_chat(message: str):
    chat.append(message)
    raw_message = message.encode()
    send_data(2, raw_message)


def recieve_data():
    try:
        header = server_connection.recv(1)
    except (socket.timeout, BlockingIOError) as e:
        err = e.args[0]
        if err == 11:
            return False
        else:
            print(e)
        return False
    except socket.error as e:
        print(e)
        return False
    else:
        if len(header) == 0:
            print("connection closed")
            exit()
        else:
            # we have something, let's see what protocol has arrived
            protocol = int.from_bytes(header, "little", signed=False)
            # ok now how big is it?
            data_size = int.from_bytes(server_connection.recv(4), "little", signed=False)
            # let's start putting the payload together
            received_payload = b""
            reamining_payload_size = data_size
            while reamining_payload_size != 0:
                received_payload += server_connection.recv(reamining_payload_size)
                reamining_payload_size = data_size - len(received_payload)
            # ok, that's all of it, now we need to hand the data into the right protocol handler
            if protocol == 1:
                recieve_game(received_payload)
            elif protocol == 2:
                recieve_chat(received_payload)
            else:
                print("We've got an unknown protocol!:", protocol)
                return False
            return protocol
    return False


def recieve_chat(raw_chat):
    chat.append(raw_chat.decode())


def recieve_game(raw_game):
    global game
    game = pickle.loads(raw_game)


# def create_game():
#     global game, pname
#     pname = 'HOST'
#     game = GameState()
#     raw_game = pickle.dumps(game, protocol=4)

#
# def recieve_game():
#     global game, pname, your_turn
#     your_turn = 1
#     pname = 'GUEST'
#     raw_game = s.recv(1024)
#     game = pickle.loads(raw_game)


def game_loop():
    global game
    game_running = True
    print('HOST' if playerID == 1 else 'GUEST')
    counter = 0
    while game_running:
        status = recieve_data()
        if status:
            if status == 1:
                pass  # Jeśli ten kod się odpali, to właśnie dostaliśmy stan gry, od przeciwnika.
            elif status == 2:
                pass  # Jeśli ten kod się odpali, to właśnie dostaliśmy wiadomość na chat.
            # Jeśli wystarczy odświeżyć ekran, to można to zrobić tutaj.
        else:
            time.sleep(.1)
            # Jeśli nic nie dostaliśmy od serwera, to tyle czekamy.

        # game logic goes here
        # maybe copy this function for your game, so that we can have a function for every game.

        # use: continue
        # when it's not your turn, and you want to check for other player moves.
        # or when you want to check chat

        # use: send_chat(message)
        # when you want to post a message to chat

        # use: send_game(game)
        # when you are done with your move and want to send it over

        # use game.variable = 1337
        # when you want to have a variable that will be networked and both players can change it on their turn

        print(chat)
        counter += 1
        send_chat(('Host' if playerID == 1 else 'Guest') + str(counter))
        time.sleep(10)



def start_connection():
    global server_connection, playerID
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        server_connection = s
        player_id = s.recv(1)
        if player_id == b'1':
            playerID = 1
        elif player_id == b'2':
            playerID = 2
        # wait for game to begin
        s.recv(1)
        s.setblocking(False)
        game_loop()


if __name__ == '__main__':
    start_connection()