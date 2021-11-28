import socket

host = "127.0.0.1"
port = 1109
game_state = None


def serwer_loop(player1, player2):
    serwer_running = True
    try:
        while serwer_running:
            player2, player1 = player1, player2
            msg = player1.recv(1024)
            print(msg)
            player2.sendall(msg)
    except:
        pass


def begin_serwer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        player1, p1addr = s.accept()
        with player1:
            player1.sendall(b'1')
            game_state = player1.recv(1024)
            print(game_state)
            player2, p2addr = s.accept()
            with player2:
                player2.sendall(b'2')
                player2.sendall(game_state)
                serwer_loop(player1, player2)


if __name__ == '__main__':
    begin_serwer()
