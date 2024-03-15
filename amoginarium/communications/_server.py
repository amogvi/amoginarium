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


class InitiateMessage(pydantic.BaseModel):
    m: tp.Literal["i"]
    id: str  # itentifier


class UpdateMessage(pydantic.BaseModel):
    m: tp.Literal["u"]
    x: int
    y: int
    j: bool  # joy button
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
        try:
            # wait 20 seconds for the initiate message
            # if the client didn't send the message before 20 sec,
            # disconnect the client
            i_raw = await asyncio.wait_for(ws.recv(), 20)

            # convert received data to json
            i_data = InitiateMessage.model_validate_json(i_raw)

        # except timeout and invalid message errors
        except Exception:
            await ws.close(CloseCode.PROTOCOL_ERROR)
            ic("client didn't send initiate message")
            return

        ic("past send message")
        controller: WsController = WsController(i_data.id)

        try:
            # wait for messages
            async for message in ws:
                # parse message
                data = Message.validate_json(
                    message,
                    strict=False
                )

                match data:
                    case InitiateMessage():
                        raise RuntimeError(
                            "received initiate message more than once"
                        )

                    case UpdateMessage():
                        controller.update_controls(
                            data.t,
                            data.j,
                            data.x,
                            data.y
                        )

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
