"""
_server.py
01. February 2024

handles all communication

Author:
Nilusink
"""
from websockets.exceptions import ConnectionClosedError
from websockets import WebSocketServerProtocol
from websockets.frames import CloseCode
from websockets.server import serve
from icecream import ic
import typing as tp
import pydantic
import asyncio

from ..controllers import WsController
from ..logic import WDTimer


class InitiateMessage(pydantic.BaseModel):
    m: tp.Literal["i"]
    t: float  # timeout in s
    id: str  # itentifier


class UpdateMessage(pydantic.BaseModel):
    m: tp.Literal["u"]
    x: int
    y: int
    b: bool  # joy button
    t: bool  # trigger button


class PingMessage(pydantic.BaseModel):
    m: tp.Literal["pi"] = "pi"


class PongMessage(pydantic.BaseModel):
    m: tp.Literal["po"]


Message = pydantic.TypeAdapter(
    tp.Annotated[
        tp.Union[
            InitiateMessage,
            UpdateMessage,
            PongMessage
        ],
        pydantic.Field(discriminator="m")
    ]
)


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
        i_raw = await ws.recv()
        i_data = InitiateMessage.model_validate_json(i_raw)

        controller = WsController(i_data.id)

        ping_timer = WDTimer(i_data.t)
        pong_timer = WDTimer(5)

        def ping():
            """
            sends a ping and starts the pong timer
            """
            ws.send(PingMessage().model_dump_json())
            pong_timer.refresh()

        def pong():
            """
            pong timeout

            closes websocket
            """
            ws.close(CloseCode.PROTOCOL_ERROR, "timeout")
            ic(f"controller didn't respond after {i_data.t + 5}s")

        # set timeout functinos
        ping_timer.on_timeout(ping)
        pong_timer.on_timeout(pong)

        # start ping timer
        ping_timer.refresh()

        try:
            # wait for messages
            async for message in ws:
                # parse message
                data = Message.validate_json(
                    message,
                    strict=False
                )

                # refresh ping timer on every message
                ping_timer.refresh()

                match data:
                    case InitiateMessage():
                        await ws.close(
                            CloseCode.PROTOCOL_ERROR,
                            "initiate message has already been sent"
                        )
                        raise RuntimeError(
                            "received initiate message more than once"
                        )

                    case UpdateMessage():
                        ic("received data", message)
                        controller.update_controlls(
                            data.t,
                            data.b,
                            data.x,
                            data.y
                        )

                    case PongMessage():
                        ic("pong")
                        pong_timer.cancel()

                    case _:
                        ic("unknown message type recived")

        # close propperly on connectino closed
        except ConnectionClosedError:
            await ws.close(CloseCode.INTERNAL_ERROR)
            ic("improper disconnect")

        finally:
            if not ws.closed:
                await ws.close(1000)

            ic("ws client disconnected", ws.close_code, ws.close_reason)

            ping_timer.cancel()
            pong_timer.cancel()

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
