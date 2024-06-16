"""
_server.py
01. February 2024

handles all communication with amogistick via raw TCP binary protocol

Author:
melektron
"""

import asyncio
import collections
import dataclasses
from icecream import ic
import queue
import struct
import time
from ..controllers._amogistick_controller import AmogistickController


msg_identify_struct = struct.Struct(">20s")
@dataclasses.dataclass
class MsgIdentify:
    identifier: str

    @classmethod
    def from_bytes(cls, data: bytes) -> "MsgIdentify":
        # grab all bytes from string until the null terminator and convert to string
        id_bytes: bytes = msg_identify_struct.unpack(data)[0]
        return cls(id_bytes.split(bytes([0]))[0].decode())
        

msg_update_struct = struct.Struct(">ii????")
@dataclasses.dataclass
class MsgUpdate:
    x_value: int
    y_value: int
    joystick_pressed: bool
    trigger_pressed: bool
    aux_l_pressed: bool
    aux_r_pressed: bool

    @classmethod
    def from_bytes(cls, data: bytes) -> "MsgUpdate":
        return cls(*msg_update_struct.unpack(data))


class AmogistickClient:

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        super().__init__()
        self._reader = reader
        self._writer = writer
        self._controller: AmogistickController = None

        self._in_timeout = False
        self._is_closed = False

    async def run(self) -> None:
        """
        processes communication
        """
        measure_span = 10
        times = collections.deque([time.perf_counter()] * measure_span, measure_span)

        try:
            # first complete the identification procedure
            if chr((await self._reader.readexactly(1))[0]) != "i":
                raise RuntimeError("Amogistick started with invalid initialization sequence")
            # read remaining 20 bytes of identify message
            msg = MsgIdentify.from_bytes(await self._reader.readexactly(msg_identify_struct.size))
            ic(f"Identity ({len(msg.identifier)}b): {msg.identifier}")

            # create the controller
            self._controller = AmogistickController(msg.identifier)
            
            while True:
                cmd = chr((await self._reader.readexactly(1))[0])
                
                match cmd:
                    case "i":
                        # read remaining 20 bytes
                        msg = MsgIdentify.from_bytes(await self._reader.readexactly(msg_identify_struct.size))
                        ic(f"Warning: repeated Identity message received ({len(msg.identifier)}b): {msg.identifier}")
                    case "u":
                        # read remaining bytes
                        msg = MsgUpdate.from_bytes(await self._reader.readexactly(msg_update_struct.size))
                        times.appendleft(time.perf_counter())
                        t10 = times[0] - times[-1]
                        t = int((t10 / measure_span) * 1000)
                        #ic(f"Update {t:03}ms: {msg}")
                        self._controller.update_controls(
                            msg.trigger_pressed,
                            msg.aux_l_pressed,
                            msg.aux_r_pressed,
                            msg.joystick_pressed,
                            msg.x_value,
                            msg.y_value
                        )
            
        except asyncio.IncompleteReadError:
            ic("amogistick: closed ended during read, disconnecting")
            await self.close()

        except TimeoutError:
            ic("amogistick: client timed out, disconnecting")
            self._in_timeout = True
            await self.close()
    
    async def close(self) -> None:
        """
        closes the client cleanly if possible and not done already, or just let's it rot if there's no other way
        """
        # TODO: make sure the client instance is actually deleted and properly garbage collected (server needs to give up it's reference for that)

        if self._is_closed: # already closed
            return
        self._writer.close()
        if not self._in_timeout:    # If we are already in a timeout, trying again will just throw another timeout error.
            await self._writer.wait_closed()
        self._is_closed = True

