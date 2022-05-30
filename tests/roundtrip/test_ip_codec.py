import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from shared.ip_codec import (
    FILL_CHAR,
    decode_ip,
    deobfuscate_packet_ordinal,
    encode_ip,
    obfuscate_packet_ordinal,
)


@given(st.binary(min_size=0, max_size=16))
def test_ip_codec_roundtrip(message: bytes):
    assume(FILL_CHAR not in message)
    encoded = encode_ip(message)
    decoded = decode_ip(encoded)
    assert message == decoded


def test_ip_codec_invalid():
    with pytest.raises(ValueError):
        encode_ip(b"\x7f")


@given(st.binary(min_size=15, max_size=15), st.integers(max_value=50, min_value=0))
def test_ordinal_obfuscation_roundtrip(message: bytes, integer: int):
    obfuscated = message = obfuscate_packet_ordinal(integer, message)
    assert deobfuscate_packet_ordinal(obfuscated) == integer
