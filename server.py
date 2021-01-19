import asyncio
import logging
import sys
import re

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)

log = logging.getLogger('server')
connections = []


class ConnectionServer(asyncio.Protocol):

    def __init__(self):
        self.mode = None
        self.name = None
        self.address = None
        self.addressed_to = None

    def connection_made(self, transport) -> None:
        # Each client connection triggers this method
        # :transport - instance of asyncio
        # "Transport, which provides an abstraction
        # for doing asynchronous I/O using the socket".
        #
        self.transport = transport
        self.address = "{:s}:{:d}".format(*self.transport.get_extra_info('peername'))
        connections.append(self)

        log.debug('Connection from: {}'.format(self.address))

        # need all users receive this
        #
        # connections contains
        # list of objects
        for user in connections:
            if user != self:
                user.send("<{}> has arrived!".format(self.address).encode())
            else:
                self.send("Use /register <login: between 3 and 10 characters or symbols> to continue".encode())

    def data_received(self, data: bytes) -> None:
        # After establishing connection this method
        # will receive and store data;
        #
        # After - sending response to client
        # that requested any type of data

        if re.match("^\/", data.decode()) is not None:
            if data.decode().strip(' ') == '/help':
                self.send("/register <username> - register user by his name. Min len - 3, max - 10,\n"
                          "/help - use it to see this message,\n"
                          "/whisper <username>- use this to PM someone,\n"
                          "/stop whisper <username> - stopping PM mode for current user and set your mode to Public".encode())
            if self.mode == "Public":
                if re.match(r'^\/whisper [0-9A-Za-z]{3,10}', data.decode()):
                    name = data.decode().split()[1]
                    if self.name == name:
                        self.send("Looks like you whispered to yourself... But no one will answer! :(".encode())
                    else:
                        self.set_whisper_mode(name=name, mode=True)
            elif self.mode == "Whisper":
                if re.match(r'^\/stop whisper [0-9A-Za-z]{3,10}', data.decode()):
                    # ending whisper for current user
                    name = data.decode().split()[2]
                    self.set_whisper_mode(name=name, mode=False)
            else:
                self.register(data)

        elif self.mode == "Public":
            self.multiple_send("<{}@{}> {}".format(self.name, self.address, data.decode()).encode())
        elif self.mode == "Whisper":
            print("IN WHISPER MODE!")
            self.addressed_to.send(data)

        log.debug("Message: {}:\t{}\tMode: {}".format(self.address, data.decode(), self.mode))

    def connection_lost(self, error) -> None:
        # When connection is closed
        # either normally or with error,
        # this method called

        # if error occurred - error contains
        # exception information in () format
        log.debug("Connection lost from: {}".format(self.address))

        connections.remove(self)
        self.multiple_send("<{}> Left chat".format(self.address).encode())
        super().connection_lost(error)

    def send(self, message: bytes) -> None:
        self.transport.write(message)

    def multiple_send(self, pattern: bytes):
        for user in connections:
            if user != self:
                user.send(pattern)

    def register(self, data: bytes):
        print(re.match(r'^\/register [0-9A-Za-z]{3,10}', data.decode()))
        match = re.match(r'^\/register [0-9A-Za-z]{3,10}', data.decode())
        if match is not None:
            if len(match.group()) == len(data.decode().strip('\n')):
                for user in connections:
                    if user.name is not None:
                        if user.name.replace('\n', '') == data.decode().split(' ')[1].replace('\n',
                                                                                              '') and user != self:
                            self.send('User with this name already exists!'.encode())
                            return
                self.mode = "Public"
                self.name = data.decode().split()[1]
                self.send("Registered successfully".encode())
                self.multiple_send("<{}@{}> Registered".format(self.name, self.address).encode())
            else:
                self.send("Use /register <[3-10] symbols>".encode())
        else:
            self.send("Use /register <[3-10] symbols>".encode())

    def pregMatch(self, compare_string: str, compared_string: str) -> bool:
        percents = 0
        for compare_letter, compared_letter in zip(compare_string, compared_string):
            if compare_letter == compared_letter:
                percents += 100 / len(compared_string)
        if percents >= 80:
            return True
        return False

    def set_whisper_mode(self, name: str, mode: bool) -> None:
        if mode:
            for user in connections:
                if user.name == name:
                    self.mode = "Whisper"
                    self.send("Mode set to whisper. Now you can write, no one will se it!".encode())
                    user.send("<{}@{}> whispered to you!".format(self.name, self.address).encode())
                    self.addressed_to = user
        else:
            if self.addressed_to.name == name:
                self.mode = "Public"
                self.send("Mode set to Public. Now you can chat with others!".encode())
                self.addressed_to.send("{} quited PM".format(self.name).encode())
                return
            else:
                self.send("No users with this name found...".encode())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # getting coroutine object
    log.debug("Serving server on: <localhost:8080>")
    coro = loop.create_server(ConnectionServer, host='localhost', port=8080)

    # run the Future to get it's result
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
