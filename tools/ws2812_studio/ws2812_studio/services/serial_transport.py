from __future__ import annotations

from dataclasses import dataclass
import queue
import threading
import time
from typing import Protocol

try:
    import serial
    from serial.tools import list_ports
except ImportError:  # pragma: no cover - handled in UI.
    serial = None
    list_ports = None

from .protocol import Command, HEADER_SIZE, SOF, decode_packet, encode_ack, encode_nack, encode_packet, Status


class Transport(Protocol):
    def open(self) -> None: ...
    def close(self) -> None: ...
    def transact(self, packet: bytes, timeout: float = 1.0) -> bytes: ...


def available_serial_ports() -> list[str]:
    if list_ports is None:
        return []
    return [port.device for port in list_ports.comports()]


@dataclass
class SerialTransport:
    port: str
    baudrate: int = 115200
    timeout: float = 0.25

    def __post_init__(self) -> None:
        self._serial = None

    def open(self) -> None:
        if serial is None:
            raise RuntimeError("pyserial is not installed")
        self._serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout, write_timeout=self.timeout)

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def transact(self, packet: bytes, timeout: float = 1.0) -> bytes:
        if self._serial is None:
            raise RuntimeError("Serial port is not open")
        self._serial.reset_input_buffer()
        self._serial.write(packet)
        self._serial.flush()
        deadline = time.monotonic() + timeout
        data = bytearray()
        while time.monotonic() < deadline:
            chunk = self._serial.read(256)
            if chunk:
                data.extend(chunk)
                start = data.find(SOF)
                if start < 0:
                    data.clear()
                    continue
                if start:
                    del data[:start]
                if len(data) >= HEADER_SIZE:
                    length = data[6] | (data[7] << 8)
                    packet_size = HEADER_SIZE + length + 2
                    if len(data) >= packet_size:
                        return bytes(data[:packet_size])
        raise TimeoutError("Device did not respond")


class SimulatedTransport:
    def __init__(self, latency_s: float = 0.03) -> None:
        self.latency_s = latency_s
        self.is_open = False
        self.last_frame = bytes(192)
        self.brightness = 255
        self.inject_timeout = False
        self.inject_busy = False

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def transact(self, packet: bytes, timeout: float = 1.0) -> bytes:
        if not self.is_open:
            raise RuntimeError("Simulator is not connected")
        if self.inject_timeout:
            time.sleep(min(timeout, 0.1))
            raise TimeoutError("Simulated timeout")
        time.sleep(self.latency_s)
        request = decode_packet(packet)
        if self.inject_busy:
            return encode_nack(request.sequence, request.command, Status.DEVICE_BUSY, "busy")
        if request.command == Command.PING:
            return encode_ack(request.sequence, request.command, Status.OK, "pong")
        if request.command == Command.GET_INFO:
            info = (
                b"WS2812 Studio FW 0.1|Colorlight 5A-75B V8.2|"
                b"8x8|64|GRB|DMA|115200"
            )
            return encode_packet(Command.ACK, request.sequence, bytes([Command.GET_INFO, Status.OK]) + info)
        if request.command == Command.SET_FRAME:
            if len(request.payload) != 192:
                return encode_nack(request.sequence, request.command, Status.INVALID_LENGTH, "frame length")
            self.last_frame = request.payload
            return encode_ack(request.sequence, request.command)
        if request.command == Command.CLEAR:
            self.last_frame = bytes(192)
            return encode_ack(request.sequence, request.command)
        if request.command == Command.SET_BRIGHTNESS:
            if len(request.payload) != 1:
                return encode_nack(request.sequence, request.command, Status.INVALID_LENGTH, "brightness")
            self.brightness = request.payload[0]
            return encode_ack(request.sequence, request.command)
        if request.command == Command.STOP:
            return encode_ack(request.sequence, request.command)
        return encode_nack(request.sequence, request.command, Status.UNKNOWN_COMMAND, "unknown")


class TransportWorker(threading.Thread):
    def __init__(self, transport: Transport) -> None:
        super().__init__(daemon=True)
        self.transport = transport
        self.requests: "queue.Queue[tuple[bytes, float, queue.Queue[bytes | Exception]]]" = queue.Queue()
        self.running = True

    def run(self) -> None:
        self.transport.open()
        while self.running:
            try:
                packet, timeout, result_queue = self.requests.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                result_queue.put(self.transport.transact(packet, timeout))
            except Exception as exc:  # noqa: BLE001 - sent to UI.
                result_queue.put(exc)
        self.transport.close()

    def stop(self) -> None:
        self.running = False

    def transact(self, packet: bytes, timeout: float = 1.0) -> bytes:
        result_queue: "queue.Queue[bytes | Exception]" = queue.Queue()
        self.requests.put((packet, timeout, result_queue))
        result = result_queue.get(timeout=timeout + 0.5)
        if isinstance(result, Exception):
            raise result
        return result
