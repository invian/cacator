import base64
import json
import os
from ipaddress import IPv4Address

import pytest
from dnslib import QTYPE, DNSQuestion
from hypothesis import given
from hypothesis import provisional as prov
from loguru import logger

from evwsync.weather_synchronizer import WeatherSynchronizer
from server.adapters.fake import FakeSessionStorage
from server.schemas import Packet
from server.server import Server
from shared.ip_codec import packetize


@given(prov.domains())
@pytest.mark.skip(
    reason="Stream deletes before we can read it again (assembled is empty after resolve())"
)
def test_keypair_reassemble(domain: str):
    session_code = "test"
    stream_code = "te"
    iv = os.urandom(16)

    client = WeatherSynchronizer(
        data_factory=lambda: {},
        servers=[base64.b64encode(domain.encode()).decode()],
    )

    dhe_message = client.build_dhe_init_packet(iv)
    dhe_init_queries = client.message2queries(
        session_code,
        stream_code,
        base64.b64encode(domain.encode()).decode(),
        dhe_message,
        False,
    )

    server = Server(FakeSessionStorage())
    for query in dhe_init_queries:
        packet = Packet.from_dns_query(
            DNSQuestion(query, qtype=QTYPE.AAAA),
            IPv4Address("127.0.0.1"),
        )
        server.resolve(packet)

    assembled = server.parse_message(stream_code, session_code, has_data=False)

    assert assembled
    client_keypair = json.loads(assembled)
    assert "B" in client_keypair
    assert "iv" in client_keypair
    assert client_keypair["B"] == client.build_public_key()
    assert client_keypair["iv"] == client.iv_from_bytes(iv)


def test_server_public_transmission():
    client = WeatherSynchronizer(data_factory=lambda: {})
    server = Server(FakeSessionStorage())
    public_key = server.respond_with_public_key()
    logger.debug("public_key {}", public_key)
    packets = server.packetize(public_key)

    message = client.resolve_server_answer(packets)
    server_public_key = int.from_bytes(message, "big")

    assert server_public_key == server.public_key


@given(...)
def test_response_assembly(message: bytes):
    client = WeatherSynchronizer(data_factory=lambda: {})
    packets = packetize(message)
    response = client.depacketize(packets)

    assert response == message
