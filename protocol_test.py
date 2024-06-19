
"""
protocol_test.py
29. February 2024

test implementation of sockets for protocol development

Author:
melektron
"""

import asyncio
import socket
import struct
import collections
import dataclasses
import aioconsole as aioc 
import queue
import time
import enum

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
    OFF = 0
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

async def handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global testrd, testwt
    testrd = reader
    testwt = writer
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

    measure_span = 10
    times = collections.deque([time.perf_counter()] * measure_span, measure_span)


    while True:
        try:
            cmd = chr((await reader.readexactly(1))[0])
            
            match cmd:
                case "i":
                    # read remaining 20 bytes
                    msg = MsgIdentify.from_bytes(await reader.readexactly(msg_identify_struct.size))
                    print(f"Identity ({len(msg.identifier)}b): {msg.identifier}")
                case "u":
                    # read remaining bytes
                    msg = MsgUpdate.from_bytes(await reader.readexactly(msg_update_struct.size))
                    times.appendleft(time.perf_counter())
                    t10 = times[0] - times[-1]
                    t = int((t10 / measure_span) * 1000)
                    #print(f"Update {t:03}ms: {msg}")
        
        except asyncio.IncompleteReadError:
            print("Closed ended during read, disconnecting")
            writer.close()
            return
        except TimeoutError:
            print("Client timed out, disconnecting")
            writer.close()
            return

        #message = ":".join("{:02x}".format(c) for c in data)
        #addr = writer.get_extra_info('peername')
#
        #print(f"Received {message} ({len(data)} bytes) from {addr!r}")
        #try:
        #    print(f"ASCII: {data.decode("ASCII")}")
        #except UnicodeDecodeError:
        #    print("(Cannot decode to not valid Unicode)")

        #print(f"Send: {message!r}")
        #writer.write(data)
        #await writer.drain()

        #await asyncio.sleep(20);

    print("Close the connection")
    writer.close()
    await writer.wait_closed()


async def main() -> int:
    server = await asyncio.start_server(handle_echo, '0.0.0.0', 12345)
    

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    #async with server:
    #    try:
    #        await server.serve_forever()
    #    except asyncio.CancelledError:
    #        print("anceled")
    #        pass

    await server.start_serving()
    
    while True:
        input = await aioc.ainput("")
        if input == "l":
            animcmd = MsgAnimCmd(
                layer=2,
                anim_code=AnimCode.FLASH,
                prim_color=(255, 0, 255),
                sec_color=(0, 0, 0),
                prim_period=120,
                sec_period=0,
                keep=False
            )
            print(animcmd)
            msg = animcmd.to_bytes()
            print(f"as bytes: {msg} (len={len(msg)})")
            testwt.write(msg)
            await testwt.drain()
        elif input == "q":
            print("closing...")
            server.close()
            testwt.write(b'asdf')
            await testwt.drain()
            testwt.close()
            await server.wait_closed()
            break
    
    return 0;


if __name__ == "__main__":
    exit(asyncio.run(main()))