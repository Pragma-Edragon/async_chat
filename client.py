import logging
import asyncio
import sys
from asyncio import StreamWriter, StreamReader

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stdout
)

SERVER_ADDRESS = ('localhost', 8080)
log = logging.getLogger('Client')


async def clientConenction(loop):
    reader, writer = await asyncio.open_connection(*SERVER_ADDRESS, loop=loop)
    tasks = [nonBlocking_dataSender(writer), nonBlocking_dataReceiver(reader)]
    await asyncio.gather(*tasks)


async def nonBlocking_dataSender(writer: StreamWriter):
    while True:
        output = await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline
        )
        writer.write(output.encode())


async def nonBlocking_dataReceiver(reader: StreamReader):
    while True:
        data = await reader.read(1024)
        if not data:
            log.debug('Connection closed.')
            return
        log.debug(data.decode().strip('\n'))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(clientConenction(loop))
    finally:
        loop.close()
