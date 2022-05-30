import socket
from ipaddress import IPv6Address
from typing import List

FILL_CHAR = b"\x7f"


def obfuscate_packet_ordinal(order: int, packet: bytes) -> bytes:
    # obfuscates the sequence number
    return chr(50 - order).encode("ascii")


def deobfuscate_packet_ordinal(packet: bytes) -> int:
    if not packet:
        return -1
    return abs(packet[-1] - 50)


def packetize(message: bytes) -> List[bytes]:
    if not message:
        return []

    packet_length = 16

    # Packetize into 15 byte packets, leaving 1 byte of room for the sequence number
    data_length = packet_length - 1
    packets = [message[i : i + data_length] for i in range(0, len(message), data_length)]

    packets = [packets[i] + obfuscate_packet_ordinal(i, packets[i]) for i in range(0, len(packets))]

    # Ensure length of response is a multiple of 16, pad last packet with \x00
    packets[-1] = packets[-1].ljust(16, FILL_CHAR)

    return packets


def encode_ip(message: bytes) -> IPv6Address:
    if FILL_CHAR in message:
        raise ValueError("Message contains reserved characters")
    try:
        return IPv6Address(socket.inet_ntop(socket.AF_INET6, message.ljust(16, FILL_CHAR)))
    except Exception:
        raise ValueError(f"Invalid IPv6 address: [{len(message)}] {message}")


def decode_ip(ip: IPv6Address) -> bytes:
    return socket.inet_pton(socket.AF_INET6, str(ip)).rstrip(FILL_CHAR)
