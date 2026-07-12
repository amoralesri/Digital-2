from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import struct

SOF = b"\xA5\x5A"
VERSION = 0x01
HEADER_SIZE = 8
CRC_SIZE = 2
MAX_PAYLOAD = 256


class Command(IntEnum):
    PING = 0x01
    GET_INFO = 0x02
    SET_FRAME = 0x10
    CLEAR = 0x11
    SET_BRIGHTNESS = 0x12
    STOP = 0x13
    ACK = 0x7E
    NACK = 0x7F


class Status(IntEnum):
    OK = 0
    CRC_ERROR = 1
    INVALID_LENGTH = 2
    UNKNOWN_COMMAND = 3
    DEVICE_BUSY = 4
    DMA_TIMEOUT = 5
    WS2812_TIMEOUT = 6
    PROTOCOL_VERSION_ERROR = 7
    TIMEOUT = 8


class ProtocolError(ValueError):
    pass


@dataclass(frozen=True)
class Packet:
    command: Command
    sequence: int
    payload: bytes = b""


def crc16_ccitt(data: bytes, initial: int = 0xFFFF) -> int:
    crc = initial
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def encode_packet(command: int | Command, sequence: int, payload: bytes = b"") -> bytes:
    command = Command(command)
    if not 0 <= sequence <= 0xFFFF:
        raise ValueError("Sequence must fit in 16 bits")
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("Payload is too large")
    body = struct.pack("<BBHH", VERSION, int(command), sequence, len(payload)) + payload
    return SOF + body + struct.pack("<H", crc16_ccitt(body))


def decode_packet(data: bytes) -> Packet:
    if len(data) < HEADER_SIZE + CRC_SIZE:
        raise ProtocolError("Packet too short")
    if data[:2] != SOF:
        raise ProtocolError("Invalid SOF")
    version, command_value, sequence, length = struct.unpack("<BBHH", data[2:HEADER_SIZE])
    if version != VERSION:
        raise ProtocolError("Unsupported protocol version")
    if length > MAX_PAYLOAD:
        raise ProtocolError("Payload too large")
    expected_size = HEADER_SIZE + length + CRC_SIZE
    if len(data) != expected_size:
        raise ProtocolError("Invalid packet length")
    body = data[2:HEADER_SIZE + length]
    expected_crc = struct.unpack("<H", data[HEADER_SIZE + length:expected_size])[0]
    if crc16_ccitt(body) != expected_crc:
        raise ProtocolError("Invalid CRC")
    try:
        command = Command(command_value)
    except ValueError as exc:
        raise ProtocolError("Unknown command") from exc
    return Packet(command=command, sequence=sequence, payload=data[HEADER_SIZE:HEADER_SIZE + length])


class PacketStreamDecoder:
    def __init__(self) -> None:
        self.buffer = bytearray()

    def feed(self, data: bytes) -> list[Packet]:
        self.buffer.extend(data)
        packets: list[Packet] = []
        while True:
            start = self.buffer.find(SOF)
            if start < 0:
                self.buffer.clear()
                return packets
            if start:
                del self.buffer[:start]
            if len(self.buffer) < HEADER_SIZE:
                return packets
            _, _, _, length = struct.unpack("<BBHH", self.buffer[2:HEADER_SIZE])
            if length > MAX_PAYLOAD:
                del self.buffer[0]
                continue
            packet_size = HEADER_SIZE + length + CRC_SIZE
            if len(self.buffer) < packet_size:
                return packets
            raw = bytes(self.buffer[:packet_size])
            del self.buffer[:packet_size]
            try:
                packets.append(decode_packet(raw))
            except ProtocolError:
                continue


def encode_ack(sequence: int, original: Command, status: Status = Status.OK, message: str = "") -> bytes:
    payload = bytes([int(original), int(status)]) + message.encode("ascii", errors="replace")[:48]
    return encode_packet(Command.ACK, sequence, payload)


def encode_nack(sequence: int, original: Command, status: Status, message: str = "") -> bytes:
    payload = bytes([int(original), int(status)]) + message.encode("ascii", errors="replace")[:48]
    return encode_packet(Command.NACK, sequence, payload)


def parse_ack_payload(payload: bytes) -> tuple[Command, Status, str]:
    if len(payload) < 2:
        raise ProtocolError("ACK/NACK payload too short")
    return Command(payload[0]), Status(payload[1]), payload[2:].decode("ascii", errors="replace")
