import os

from hypothesis import given

from shared.aes import decrypt_message, encypt_message


@given(...)
def test_encryptors_roundtrip(message: bytes):
    key = os.urandom(32)
    iv = os.urandom(16)

    encoded = encypt_message(message, key, iv)
    decoded = decrypt_message(encoded, key, iv)

    assert message == decoded
