"""
_server.py
01. February 2024

handles all communication

Author:
Nilusink
"""
from websockets.exceptions import ConnectionClosedError
from websockets import WebSocketServerProtocol
from websockets.server import serve
from icecream import ic
import asyncio

from ..controllers import WsController


class Server:
    running = True

    def __init__(
        self,
        address: tuple[str, int]
    ) -> None:
        self._host = address[0]
        self._ip = address[1]

        self._stop = ...

    async def _client_handler(self, ws: WebSocketServerProtocol) -> None:
        ic("ws new client", ws.host, ws.port)

        # receive controller id
        c_id = await ws.recv()

        _ = WsController(c_id)

        try:
            async for message in ws:
                ic("received data", message)
                # controller.update_controlls(**message)

        # close propperly on connectino closed
        except ConnectionClosedError:
            ic("improper disconnect")

        finally:
            await ws.close()
            ic("ws client disconnected", ws.close_code, ws.close_reason)

    async def run(self) -> None:
        """
        run the server continuousely
        """
        loop = asyncio.get_event_loop()
        self._stop = loop.create_future()

        async with serve(self._client_handler, self._host, self._ip):
            # wait until close is called
            while self.running:
                await asyncio.sleep(.1)

    def close(self) -> None:
        self.running = False
        if self._stop is ...:
            raise RuntimeError(
                "tried running Server.close before running Server.run"
            )

        self._stop.set_result(None)
