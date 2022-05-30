from hypothesis import given

from shared.utils import decode_query, encode_query


@given(...)
def test_encoders_roundtrip(message: bytes):
    encoded = encode_query(message)
    decoded = decode_query(encoded)
    assert message == decoded
