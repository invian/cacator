import base64
import binascii
from random import randint


def int_to_bytes(integer) -> bytes:
    if integer < 0:
        return b"-" + int_to_bytes(-integer)
    return integer.to_bytes((integer.bit_length() + 7) // 8, "big")


def encode_query(query: bytes) -> bytes:
    encoded = base64.b32encode(query)
    converted = encoded.lower().replace(b"=", b"-") + b"".join(
        [chr(randint(97, 122)).encode() for _ in range(0, 3)]
    )
    return converted


def decode_query(query: bytes) -> bytes:
    processed = query[:-3].upper().replace(b"-", b"=")
    try:
        return base64.b32decode(processed)
    except binascii.Error:
        return query


def calc_public_key(g, a, p):
    return pow(g, a, p)


def calc_common_key(client_public, a, p):
    return pow(client_public, a, p)
