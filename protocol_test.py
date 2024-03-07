
"""
protocol_test.py
29. February 2024

test implementation of sockets for protocol development

Author:
melektron
"""

import asyncio
import socket

async def handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # configure keepalive
    # https://stackoverflow.com/questions/75326508/set-socket-options-on-python-asyncio-streams-api
    sock: socket.socket = writer.get_extra_info("socket")
    print(f"SO_KEEPALIVE={sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)}")
    print(f"TCP_KEEPIDLE={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE)}")
    print(f"TCP_KEEPINTVL={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL)}")
    print(f"TCP_KEEPCNT={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT)}")
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 2)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
    print(f"SO_KEEPALIVE={sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)}")
    print(f"TCP_KEEPIDLE={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE)}")
    print(f"TCP_KEEPINTVL={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL)}")
    print(f"TCP_KEEPCNT={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT)}")


    while True:
        data: bytes = None
        try:
            data = await reader.read(100)
        except TimeoutError:
            print("Client timed out, disconnecting")
            writer.close()
            return

        message = ":".join("{:02x}".format(c) for c in data)
        addr = writer.get_extra_info('peername')

        print(f"Received {":".join(hex(x) for x in data)} ({len(message)} bytes) from {addr!r}")

        print(f"Send: {message!r}")
        writer.write(data)
        await writer.drain()

        #await asyncio.sleep(20);

    print("Close the connection")
    writer.close()
    await writer.wait_closed()


async def main() -> int:
    server = await asyncio.start_server(handle_echo, '0.0.0.0', 12345)
    

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            print("anceled")
            pass
    
    return 0;


if __name__ == "__main__":
    exit(asyncio.run(main()))