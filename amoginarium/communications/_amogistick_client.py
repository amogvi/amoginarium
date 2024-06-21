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
import struct
import time
import enum
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


class AnimCode(enum.Enum):
    INACTIVE = 0
    STATIC = 1
    FLASH = 2
    BLINK = 3
    SINGLE_FADE = 4
    CYCLIC_FADE = 5


msg_anim_cmd_struct = struct.Struct(">1sBBBBBBBBII?")
@dataclasses.dataclass
class MsgAnimCmd:
    layer: int
    anim_code: AnimCode 
    prim_color: tuple[int, int, int]
    sec_color: tuple[int, int, int]
    prim_period: int
    sec_period: int
    keep: bool
    m: bytes = b"a"

    def to_bytes(self) -> bytes:
        return msg_anim_cmd_struct.pack(
            self.m,
            self.layer,
            self.anim_code.value,
            self.prim_color[0],
            self.prim_color[1],
            self.prim_color[2],
            self.sec_color[0],
            self.sec_color[1],
            self.sec_color[2],
            self.prim_period,
            self.sec_period,
            self.keep
        )


class AmogistickClient:

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        super().__init__()
        self._reader = reader
        self._writer = writer
        self._controller: AmogistickController = None

        self._in_timeout = False
        self._is_closed = False

        self._measure_span = 10
        self._times = collections.deque([time.perf_counter()] * self._measure_span, self._measure_span)

    async def run(self) -> None:
        """
        processes communication
        """

        try:
            # first complete the identification procedure
            if chr((await self._reader.readexactly(1))[0]) != "i":
                raise RuntimeError("Amogistick started with invalid initialization sequence")
            # read remaining 20 bytes of identify message
            msg = MsgIdentify.from_bytes(await self._reader.readexactly(msg_identify_struct.size))
            ic(f"Identity ({len(msg.identifier)}b): {msg.identifier}")

            # create or get the controller
            self._controller = AmogistickController.get(msg.identifier)
            # link animation callbacks
            self._controller.on_feedback_hit = lambda: self.send_message(MsgAnimCmd(
                0, 
                AnimCode.FLASH, 
                (255, 0, 0), 
                (0, 0, 0),
                8, 
                0,
                False
            ))
            self._controller.on_feedback_shoot = lambda: self.send_message(MsgAnimCmd(
                1, 
                AnimCode.FLASH, 
                (0, 0, 255), 
                (0, 0, 0),
                2, 
                0,
                False
            ))
            self._controller.on_feedback_heal_start = lambda: self.send_message(MsgAnimCmd(
                3, 
                AnimCode.CYCLIC_FADE, 
                (0, 0, 0),
                (40, 180, 0),
                60,
                200,
                True
            ))
            self._controller.on_feedback_heal_stop = lambda: self.send_message(MsgAnimCmd(
                3, 
                AnimCode.INACTIVE, 
                (0, 0, 0), 
                (0, 0, 0),
                0, 
                0,
                False
            ))

            # reset all currently running controller animations
            self.send_message(MsgAnimCmd(0, AnimCode.INACTIVE, (0, 0, 0), (0, 0, 0), 0, 0, False))
            self.send_message(MsgAnimCmd(1, AnimCode.INACTIVE, (0, 0, 0), (0, 0, 0), 0, 0, False))
            self.send_message(MsgAnimCmd(2, AnimCode.INACTIVE, (0, 0, 0), (0, 0, 0), 0, 0, False))
            self.send_message(MsgAnimCmd(3, AnimCode.INACTIVE, (0, 0, 0), (0, 0, 0), 0, 0, False))

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
                        self._times.appendleft(time.perf_counter())
                        t10 = self._times[0] - self._times[-1]
                        self._controller.current_update_period = int((t10 / self._measure_span) * 1000)
                        #ic(f"Update {self._controller.current_update_period:03}ms: {msg}")
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
    
    def send_message(self, msg: MsgAnimCmd ) -> None:  # and possibly more in the future
        self._writer.write(msg.to_bytes())
        # ic("send: ", msg.to_bytes())
        asyncio.get_event_loop().create_task(self._writer.drain())
    
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

