import socket
import time

host = "127.0.0.1"
port = 1109
game_state = None


def serwer_loop(player1, player2):
    serwer_running = True
    print("starting data transfer between players!")
    while serwer_running:
        time.sleep(.1)
        player2, player1 = player1, player2  # exchange players to alternate attempts to push data through
        try:
            msg = player1.recv(1024)
        except (socket.timeout, BlockingIOError) as e:
            err = e.args[0]
            # this next if/else is a bit redundant, but illustrates how the
            # timeout exception is setup
            if err == 11:
                continue
            else:
                print(e)
                print("we have a timeout problem")
                continue
        except socket.error as e:
            print(e)
            serwer_running = False
            print("error on the socket")
            continue
        else:
            if len(msg) == 0:
                print('Got an empty transmission.')
                serwer_running = False
                continue
            else:
                # got a message do something :)
                player2.send(msg)
    print("server closing")


def begin_serwer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("server started, waiting for clients")
        player1, p1addr = s.accept()
        player1.setblocking(False)
        player1.send(b'1')
        print("client1 connected.", p1addr)
        player2, p2addr = s.accept()
        player2.setblocking(False)
        player2.send(b'2')
        print("client2 connected.", p2addr)
        player1.send(b'0')  # inform both players to begin game
        player2.send(b'0')
        serwer_loop(player1, player2)
        s.close()  # server loop has quit, closing shop.


if __name__ == '__main__':
    begin_serwer()
