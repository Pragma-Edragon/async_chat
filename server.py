import asyncio

connections = []


async def handle_server(reader, writer):
    while True:
        try:
            data = await reader.read(1024)
            message = data.decode()
            client = writer.get_extra_info('peername')

            if len(connections) > 0:
                for user in connections:
                    if user != writer:
                        user.write(
                            ("<{:s}:{:d}>\t".format(*client) + message).encode()
                        )
                        await user.drain()

            if writer not in connections:
                connections.append(writer)
                for user in connections:
                    user.write("[root] New client arrived: {:s}:{:d}".format(*client).encode())

            print(connections)
        except ConnectionResetError as e:
            print(e)
            for user in connections:
                user.write("<{:s}:{:d}> disconnected".format(*user.get_extra_info('peername')).encode())
            pass

loop = asyncio.get_event_loop()
coro = asyncio.start_server(
    handle_server, '127.0.0.1', 8080, loop=loop
)
server = loop.run_until_complete(coro)

print("<Serving on: localhost:8080>")
try:
    loop.run_forever()
except KeyboardInterrupt:
    quit()

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()