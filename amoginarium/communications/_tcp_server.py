"""
_server.py
01. February 2024

handles all communication with amogistick via raw TCP binary protocol

Author:
melektron
"""

from icecream import ic
import typing as tp
import asyncio
import socket

from ._amogistick_client import AmogistickClient


class TCPServer:
    running = True

    def __init__(
            self,
            address: tuple[str, int]
    ) -> None:
        self._host = address[0]
        self._ip = address[1]

        self._stop: asyncio.Future = ...
        self._clients: list[AmogistickClient] = []

    async def _client_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        # configure keepalive
        # https://stackoverflow.com/questions/75326508/set-socket-options-on-python-asyncio-streams-api
        sock: socket.socket = writer.get_extra_info("socket")
        #print(f"SO_KEEPALIVE={sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)}")
        #print(f"TCP_KEEPIDLE={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE)}")
        #print(f"TCP_KEEPINTVL={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL)}")
        #print(f"TCP_KEEPCNT={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT)}")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 2)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
        #print(f"SO_KEEPALIVE={sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)}")
        #print(f"TCP_KEEPIDLE={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE)}")
        #print(f"TCP_KEEPINTVL={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL)}")
        #print(f"TCP_KEEPCNT={sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT)}")

        # create client instance
        client = AmogistickClient(reader, writer)
        self._clients.append(client)
        await client.run()

    async def run(self) -> None:
        """
        run the server continuously
        """
        # start server
        server = await asyncio.start_server(lambda r, w: self._client_handler(r, w), '0.0.0.0', 12345)
    
        # create future for clean exit
        loop = asyncio.get_event_loop()
        self._stop = loop.create_future()
        
        # host address overview
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        ic(f'amogistick TCP serving on {addrs}')

        await server.start_serving()
        try:
            await self._stop

        except asyncio.CancelledError:
            ic("amogistick TCP server canceled")
        finally:
            ic("amogistick TCP server closing...")
            # stop receiving new connections
            server.close()
            # close all existing connections
            for c in self._clients: await c.close()
            await server.wait_closed()

    def close(self) -> None:
        if self._stop is ...:
            raise RuntimeError(
                "tried running Server.close before running Server.run"
            )
        self._stop.set_result(None)
