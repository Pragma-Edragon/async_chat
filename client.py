import asyncio
import logging
import functools
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stdout
)

SERVER_ADDRESS = ('localhost', 8080)


class ClientClass(asyncio.Protocol):

    def __init__(self, future, message=None):
        self.log = logging.getLogger('client')
        self.message = message
        self.f = future

    def connection_made(self, transport) -> None:
        self.transport = transport
        self.address = self.transport.get_extra_info('peername')
        self.log.debug("Connection made to: {:s}:{:d}".format(*self.address))
        self.transport.write("Hello, world!".encode())
        print(self.ainput())
        if self.transport.can_write_eof():
            self.transport.write_eof()

    def data_received(self, data: bytes) -> None:
        self.log.debug("Message: {!r}".format(data))

    def connection_lost(self, exc) -> None:
        self.transport.close()
        if not self.f.done():
            self.f.set_result(True)
        super().connection_lost(exc)

    async def ainput(self):
        return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client_completed = asyncio.Future()
    client_factory = functools.partial(
        ClientClass,
        future=client_completed
    )
    factory_coro = loop.create_connection(
        client_factory,
        *SERVER_ADDRESS,
    )
    try:
        loop.run_until_complete(factory_coro)
        loop.run_until_complete(client_completed)
    finally:
        loop.close()
