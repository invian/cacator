import socket
from ipaddress import IPv4Address

from dnslib import DNSQuestion
from hypothesis import given
from hypothesis import strategies as st

from evwsync.weather_synchronizer import WeatherSynchronizer
from server.adapters.fake import FakeSessionStorage
from server.schemas import Packet, SessionInfo
from server.server import Server


def query2packet(request: str, source_ip: IPv4Address):
    source_ip = IPv4Address(source_ip)
    return Packet.from_dns_query(DNSQuestion(request), source_ip)


@given(st.builds(SessionInfo))
def test_key_exchange(data: SessionInfo):
    client = WeatherSynchronizer(data_factory=lambda: data.dict())
    repo = FakeSessionStorage()
    server = Server(repo)

    socket.getaddrinfo = lambda domain, *_: [
        (
            None,
            None,
            1,
            "",
            (str(address), 80),
        )
        for address in server.resolve(query2packet(domain, IPv4Address("127.0.0.1")))
    ]

    client.send_data_message()
    assert list(repo.all_sessions().values())[0].info == data
