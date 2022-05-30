from hypothesis import given

from evwsync.weather_synchronizer import WeatherSynchronizer
from server.adapters.fake import FakeSessionStorage
from server.server import Server
from shared.ip_codec import decode_ip
from shared.utils import decode_query, encode_query


@given(...)
def test_packetizations_roundtrip(message: bytes):
    encoded = encode_query(message)
    client = WeatherSynchronizer(data_factory=lambda: {})
    server = Server(FakeSessionStorage())
    packets = server.packetize(encoded)
    decoded_packets = [decode_ip(packet) for packet in packets]
    depacketized = client.depacketize(decoded_packets)
    decoded = decode_query(depacketized)
    assert decoded == message
