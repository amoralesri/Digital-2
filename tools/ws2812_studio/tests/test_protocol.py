import pytest

from ws2812_studio.services.protocol import (
    Command,
    PacketStreamDecoder,
    ProtocolError,
    Status,
    crc16_ccitt,
    decode_packet,
    encode_ack,
    encode_packet,
    parse_ack_payload,
)


def test_crc16_ccitt_known_vector():
    assert crc16_ccitt(b"123456789") == 0x29B1


def test_encode_decode_ping():
    raw = encode_packet(Command.PING, 7)
    packet = decode_packet(raw)
    assert packet.command == Command.PING
    assert packet.sequence == 7
    assert packet.payload == b""


def test_bad_crc_rejected():
    raw = bytearray(encode_packet(Command.PING, 1))
    raw[-1] ^= 0x55
    with pytest.raises(ProtocolError):
        decode_packet(bytes(raw))


def test_stream_decoder_recovers_after_garbage():
    decoder = PacketStreamDecoder()
    raw = b"garbage" + encode_packet(Command.CLEAR, 3)
    packets = decoder.feed(raw)
    assert len(packets) == 1
    assert packets[0].command == Command.CLEAR


def test_ack_payload():
    raw = encode_ack(4, Command.SET_FRAME, Status.OK, "done")
    packet = decode_packet(raw)
    original, status, message = parse_ack_payload(packet.payload)
    assert packet.command == Command.ACK
    assert original == Command.SET_FRAME
    assert status == Status.OK
    assert message == "done"
