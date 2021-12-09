import socket
import pickle
import time


playerID = None
server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chat = []


class GameState:
    def __init__(self):
        self.game_id = -1


game = GameState()


def send_data(protocol: int, data: bytes):
    payload_size = len(data)
    payload = protocol.to_bytes(1, "little", signed=False) + \
        payload_size.to_bytes(4, "little", signed=False) + data
    server_connection.sendall(payload)


def send_game(game: GameState):
    raw_game = pickle.dumps(game, protocol=4)
    send_data(1, raw_game)


def send_chat(message: str):
    chat.append(message)
    raw_message = message.encode()
    send_data(2, raw_message)


def receive_data():
    try:
        header = server_connection.recv(1)
    except (socket.timeout, BlockingIOError) as e:
        err = e.args[0]
        if err == 11 or err == 35 or err == 10035:
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
            return 3  # here causing return code for server gone.
        else:
            # we have something, let's see what protocol has arrived
            protocol = int.from_bytes(header, "little", signed=False)
            # ok now how big is it?
            data_size = int.from_bytes(
                server_connection.recv(4), "little", signed=False)
            # let's start putting the payload together
            received_payload = b""
            reamining_payload_size = data_size
            while reamining_payload_size != 0:
                received_payload += server_connection.recv(
                    reamining_payload_size)
                reamining_payload_size = data_size - len(received_payload)
            # ok, that's all of it, now we need to hand the data into the right protocol handler
            if protocol == 1:
                receive_game(received_payload)
            elif protocol == 2:
                receive_chat(received_payload)
            else:
                print("We've got an unknown protocol!:", protocol)
                return False
            return protocol
    return False


def receive_chat(raw_chat):
    chat.append(raw_chat.decode())


def receive_game(raw_game):
    global game
    game = pickle.loads(raw_game)

def game_loop():
    global game
    game_running = True
    print('HOST' if playerID == 1 else 'GUEST')
    counter = 0
    while game_running:
        status = receive_data()
        if status:
            if status == 1:
                # Jeśli ten kod się odpali, to właśnie dostaliśmy stan gry, od przeciwnika.
                pass
            elif status == 2:
                # Jeśli ten kod się odpali, to właśnie dostaliśmy wiadomość na chat.
                pass
            elif status == 3:
                exit()
            # Jeśli wystarczy odświeżyć ekran, to można to zrobić tutaj.
        else:
            time.sleep(.1)
            # Jeśli nic nie dostaliśmy od serwera, to tyle czekamy.

        # This is an example of game loop function.
        # do not write here, just import client at the top of game code.

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


def start_connection(host, port):
    global playerID
    server_connection.connect((host, port))
    player_id = server_connection.recv(1)
    if player_id == b'1':
        playerID = 1
    elif player_id == b'2':
        playerID = 2
    # wait for game to begin
    server_connection.recv(1)
    server_connection.setblocking(False)


def close_connection():
    server_connection.close()


if __name__ == '__main__':
    # start_connection('155.158.180.62', 1109)
    start_connection('127.0.0.1', 1109)
    game_loop()
    close_connection()

