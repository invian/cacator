from hypothesis import given

from shared.ip_codec import deobfuscate_packet_ordinal
from shared.utils import decode_query, encode_query, int_to_bytes


@given(...)
def test_deobfuscate_packet_ordinal(packet: bytes):
    deobfuscate_packet_ordinal(packet)


@given(...)
def test_decode_query(query: bytes):
    decode_query(query)


@given(...)
def test_encode_query(query: bytes):
    encode_query(query)


@given(...)
def test_int_to_bytes(value: int):
    int_to_bytes(value)
