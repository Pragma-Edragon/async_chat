import threading
import socket
import sys


def get_attr():
    # getting ARGV args with sys.argv
    if sys.argv[1] is None and sys.argv[2] is None:
        raise KeyError("HOST and PORT must be set!")
    return sys.argv[1], sys.argv[2]


# creating socket IP/V4 TCP object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST, PORT = get_attr()
sock.connect((HOST, int(PORT)))


def send_to_server():
    sock.send('Hello, world!'.encode())
    while True:
        print(":")
        message = sys.stdin.readline()
        if len(message) <= 0:
            quit()
        sock.send(message.encode())


def receive_from_server():
    while True:
        data = sock.recv(1024)
        if data:
            print(data.decode())


if __name__ == '__main__':
    threading_send = threading.Thread(target=send_to_server).start()
    threading_recv = threading.Thread(target=receive_from_server).start()
