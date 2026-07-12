from ws2812_studio.models.frame import Frame
from ws2812_studio.services.device_controller import DeviceController
from ws2812_studio.services.protocol import Command, encode_ack, encode_packet
from ws2812_studio.services.protocol import Status
from ws2812_studio.services.serial_transport import SerialTransport, SimulatedTransport


def test_simulated_device_ping_info_and_frame():
    transport = SimulatedTransport(latency_s=0)
    controller = DeviceController(transport)
    controller.open()
    assert controller.ping().ok
    info = controller.get_info()
    assert info.ok
    assert b"Colorlight 5A-75B" in info.payload
    frame = Frame.blank((10, 20, 30))
    result = controller.send_frame(frame)
    assert result.ok
    assert transport.last_frame[:3] == bytes([10, 20, 30])
    assert controller.clear().status == Status.OK
    controller.close()


class FragmentedSerial:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.written = b""

    def reset_input_buffer(self):
        pass

    def write(self, packet):
        self.written += packet

    def flush(self):
        pass

    def read(self, _size):
        if self.chunks:
            return self.chunks.pop(0)
        return b""


def test_serial_transport_waits_for_complete_fragmented_packet():
    response = encode_ack(9, Command.GET_INFO, Status.OK, "studio-ready")
    serial = FragmentedSerial([response[:3], response[3:8], response[8:]])
    transport = SerialTransport("/dev/null")
    transport._serial = serial

    raw = transport.transact(encode_packet(Command.GET_INFO, 9), timeout=0.2)

    assert raw == response
