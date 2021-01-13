import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr
)

log = logging.getLogger('server')
connections = []


class ConnectionServer(asyncio.Protocol):

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
        # connections contains
        # list of objects
        for user in connections:
            if user != self:
                self.send("<N> user arrived!".encode())

    def data_received(self, data: bytes) -> None:
        # After establishing connection this method
        # will receive and store data;
        #
        # After - sending response to client
        # that requested any type of data

        # need to register /whisper command.
        # /whisper <username or hostname>
        log.debug("Message: {}:\t{}".format(self.address, data.decode()))
        for user in connections:
            if user != self:
                self.send(data)

    def connection_lost(self, error) -> None:
        # When connection is closed
        # either normally or with error,
        # this method called

        # if error occurred - exc contains
        # exception information in () format
        log.debug("Connection lost from: {}".format(self.address))

        connections.remove(self)
        super().connection_lost(error)

    def send(self, message: bytes) -> None:
        self.transport.write(message)


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
