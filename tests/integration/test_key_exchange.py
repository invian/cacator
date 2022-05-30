import base64
import socket
from ipaddress import IPv4Address
from typing import List

from dnslib import DNSQuestion
from hypothesis import given
from hypothesis import provisional as prov
from hypothesis import settings
from hypothesis import strategies as st

from evwsync.weather_synchronizer import WeatherSynchronizer
from server.adapters.fake import FakeSessionStorage
from server.schemas import Packet
from server.server import Server


def query2packet(request: str, source_ip: IPv4Address):
    source_ip = IPv4Address(source_ip)
    return Packet.from_dns_query(DNSQuestion(request), source_ip)


@given(prov.domains(), st.ip_addresses(v=4))
def test_key_exchange(domain: str, source_ip: IPv4Address):
    client = WeatherSynchronizer(
        data_factory=lambda: {}, servers=[base64.b64encode(domain.encode()).decode()]
    )
    repo = FakeSessionStorage()
    server = Server(repo)

    socket.getaddrinfo = lambda domain, *args: [
        (
            None,
            None,
            1,
            "",
            (str(address), 80),
        )
        for address in server.resolve(query2packet(domain, IPv4Address(source_ip)))
    ]

    client.send_dhe_init()
    assert (
        client.servers[base64.b64encode(domain.encode()).decode()]["key"]
        == list(repo.all_sessions().values())[0].key
    )


@given(prov.domains(), st.ip_addresses(v=4))
def test_key_exchange_with_restarted_server(domain: str, source_ip: IPv4Address):
    client = WeatherSynchronizer(
        data_factory=lambda: {"hello": 123},
        servers=[base64.b64encode(domain.encode()).decode()],
    )
    repo = FakeSessionStorage()
    server = Server(repo)

    socket.getaddrinfo = lambda domain, *args: [
        (
            None,
            None,
            1,
            "",
            (str(address), 80),
        )
        for address in server.resolve(query2packet(domain, IPv4Address(source_ip)))
    ]

    client.send_data_message()
    client.send_dhe_init()

    assert (
        client.servers[base64.b64encode(domain.encode()).decode()]["key"]
        == list(repo.all_sessions().values())[0].key
    )


@settings(max_examples=10)
@given(st.lists(prov.domains()), st.ip_addresses(v=4))
def test_multiserver_key_exchange(domains: List[str], source_ip: IPv4Address):
    client = WeatherSynchronizer(
        data_factory=lambda: {},
        servers=[base64.b64encode(domain.encode()).decode() for domain in domains],
    )
    repo = FakeSessionStorage()
    server = Server(repo)

    socket.getaddrinfo = lambda domain, *args: [
        (
            None,
            None,
            1,
            "",
            (str(address), 80),
        )
        for address in server.resolve(query2packet(domain, IPv4Address(source_ip)))
    ]

    client.send_dhe_init()
    for domain in domains:
        assert (
            client.servers[base64.b64encode(domain.encode()).decode()]["key"]
            == list(repo.all_sessions().values())[0].key
        )
