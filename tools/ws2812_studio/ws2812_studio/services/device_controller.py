from __future__ import annotations

from dataclasses import dataclass
import itertools

from ws2812_studio.models.frame import Frame

from .color_order import apply_brightness, rgb_to_ws2812_bytes
from .mapping import MatrixMapping
from .protocol import Command, Packet, decode_packet, encode_packet, parse_ack_payload, Status
from .serial_transport import Transport


@dataclass
class DeviceResponse:
    ok: bool
    command: Command
    status: Status
    message: str = ""
    payload: bytes = b""


class DeviceController:
    def __init__(self, transport: Transport, mapping: MatrixMapping | None = None) -> None:
        self.transport = transport
        self.mapping = mapping or MatrixMapping()
        self._sequence = itertools.count(1)

    def open(self) -> None:
        self.transport.open()

    def close(self) -> None:
        self.transport.close()

    def _send(self, command: Command, payload: bytes = b"", timeout: float = 1.0) -> DeviceResponse:
        sequence = next(self._sequence) & 0xFFFF
        raw = self.transport.transact(encode_packet(command, sequence, payload), timeout=timeout)
        packet = decode_packet(raw)
        if packet.command not in (Command.ACK, Command.NACK):
            return DeviceResponse(False, command, Status.UNKNOWN_COMMAND, "unexpected response", packet.payload)
        original, status, message = parse_ack_payload(packet.payload)
        return DeviceResponse(packet.command == Command.ACK and status == Status.OK, original, status, message, packet.payload[2:])

    def ping(self) -> DeviceResponse:
        return self._send(Command.PING)

    def get_info(self) -> DeviceResponse:
        return self._send(Command.GET_INFO)

    def clear(self) -> DeviceResponse:
        return self._send(Command.CLEAR)

    def stop(self) -> DeviceResponse:
        return self._send(Command.STOP)

    def set_brightness(self, value: int) -> DeviceResponse:
        return self._send(Command.SET_BRIGHTNESS, bytes([max(0, min(255, int(value)))]))

    def send_frame(self, frame: Frame, brightness: int = 255) -> DeviceResponse:
        scale = max(0, min(255, int(brightness)))
        pixels = []
        for r, g, b in frame.pixels:
            pixels.append(apply_brightness((r, g, b), scale))
        mapped = self.mapping.reorder_pixels(pixels)
        payload = bytearray()
        for r, g, b in mapped:
            payload.extend(rgb_to_ws2812_bytes(r, g, b))
        return self._send(Command.SET_FRAME, bytes(payload), timeout=1.5)
