import socket
from ipaddress import IPv4Address, IPv6Address
from typing import List

from hypothesis import given

from evwsync.weather_synchronizer import WeatherSynchronizer


@given(...)
def test_prepare_data_message(_typecode: int, _message: bytes):
    client = WeatherSynchronizer(data_factory=lambda: {})
    client.prepare_data_message(_typecode, _message)


@given(...)
def test_split_to_packets(message: bytes):
    WeatherSynchronizer.split_to_packets(message)


@given(...)
def test_form_dns_queries(
    packets: List[bytes],
    domain: str,
    is_data: bool,
    session_code: str,
    stream_code: str,
):
    WeatherSynchronizer.form_dns_queries(
        packets,
        domain,
        is_data,
        session_code,
        stream_code,
    )


@given(...)
def test_send_dns_queries(queries: List[str], ip: IPv4Address):
    socket.getaddrinfo = lambda *_: [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (str(ip), 80))]
    WeatherSynchronizer.send_dns_queries(queries)


@given(...)
def test_iv_from_bytes(iv: bytes):
    WeatherSynchronizer.iv_from_bytes(iv)


@given(...)
def test_message2queries(
    session_code: str,
    stream_code: str,
    domain: str,
    message: bytes,
    as_data: bool,
):
    client = WeatherSynchronizer(data_factory=lambda: {})
    client.message2queries(session_code, stream_code, domain, message, as_data)


@given(...)
def test_build_data_message(
    session_code: str,
    stream_code: str,
    domain: str,
    typecode: int,
    message: str,
):
    client = WeatherSynchronizer(data_factory=lambda: {})
    client.build_data_message(session_code, stream_code, domain, typecode, message)


@given(...)
def test_sort_packets(packets: List[bytes]):
    WeatherSynchronizer.sort_packets(packets)


@given(...)
def test_depacketize(packets: List[bytes]):
    client = WeatherSynchronizer(data_factory=lambda: {})
    client.depacketize(packets)


@given(...)
def test_resolve_server_answer(packets: List[IPv6Address]):
    client = WeatherSynchronizer(data_factory=lambda: {})
    client.resolve_server_answer(packets)


@given(...)
def test_resolve_server_public_key(public_key: int):
    client = WeatherSynchronizer(data_factory=lambda: {})
    client.resolve_server_public_key(public_key)


@given(...)
def test_packetize_dhe_init(domain: str, sesion_code: str, stream_code: str):
    client = WeatherSynchronizer(data_factory=lambda: {})
    client.packetize_dhe_init(domain, sesion_code, stream_code)


@given(...)
def test_init_server(domain: str, ip: IPv4Address):
    socket.getaddrinfo = lambda *_: [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (str(ip), 80))]

    client = WeatherSynchronizer(data_factory=lambda: {})
    client.init_server(domain)
