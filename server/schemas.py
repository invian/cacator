from __future__ import annotations

from datetime import datetime, timedelta
from ipaddress import IPv4Address
from typing import Any, Dict, List, Optional

from dnslib import DNSQuestion
from loguru import logger
from pydantic import BaseModel, Field, NonNegativeInt, validator


class SessionInfo(BaseModel):
    hostname: Optional[str] = None
    kernel: Optional[str] = None
    uid: Optional[str] = None
    source_ip: Optional[IPv4Address] = None


PacketData = str


NON_DATA_PREAMBLE = "ph"


class Packet(BaseModel):
    preamble: str
    # The first byte of preamble is that packet's sequence number
    # The second byte of preamble is the total number of pkts
    # So pkt[0] & pkt[1] tells the server how to reassemble
    # To make this *slightly* less obvious on the wire,
    # the digits are inverted (0=f, 1=e, ...).
    #
    # However non-data packets use the NON_DATA_PREAMBLE as
    # a base. The NON_DATA_PREAMBLE characters are incremented
    # to encode seq/total information. NON_DATA_PREAMBLE
    # must be carefully chosen because of this: each char
    # cannot be greater than 'k' because 'k' + 15 = 'z' and
    # beyond that we have non-DNS characters.
    contains_data: bool = False
    stream_code: str
    session_code: str
    domain: str
    source_ip: IPv4Address
    data: PacketData
    order: NonNegativeInt = 0
    out_of: NonNegativeInt = 0

    def last(self):
        return self.order == self.out_of - 1

    @validator("stream_code", "preamble")
    def validate_stream_code(cls, v):
        # Sanity check.
        # If all the fields aren't there we won't be able to decode the packet.
        if len(v) != 2:
            raise SyntaxError("Not a beacon packet.")
        return v

    @validator("session_code")
    def validate_session_code(cls, v):
        # Sanity check.
        # If all the fields aren't there we won't be able to decode the packet.
        if len(v) != 4:
            raise SyntaxError("Not a beacon packet.")
        return v

    @validator("contains_data", pre=True, always=True)
    def contains_data_check(cls, v, values, **kwargs):
        logger.debug("contains_data={}", v)
        try:
            return not ord(values["preamble"][0]) >= ord(NON_DATA_PREAMBLE[0])
        except Exception as e:
            raise SyntaxError(f"Not a beacon packet: {e}")

    @validator("order", pre=True, always=True)
    def order_check(cls, v, values, **kwargs):
        try:
            if values["contains_data"]:
                return abs(int(values["preamble"][0], 16) - 15)
            else:
                return abs(ord(NON_DATA_PREAMBLE[0]) - ord(values["preamble"][0]))
        except Exception as e:
            raise SyntaxError(f"Not a beacon packet: {e}")

    @validator("out_of", pre=True, always=True)
    def total_check(cls, v, values, **kwargs):
        try:
            if values["contains_data"]:
                return abs(int(values["preamble"][1], 16) - 15)
            else:
                return abs(ord(NON_DATA_PREAMBLE[1]) - ord(values["preamble"][1]))
        except Exception as e:
            raise SyntaxError(f"Not a beacon packet: {e}")

    @staticmethod
    def from_dns_query(query: DNSQuestion, source_ip: IPv4Address) -> Packet:
        """
        Create a packet from a DNS query.
        """
        # Extract queried hostname as a string without trailing dot.
        query_name = str(query.qname)[:-1]
        fields = query_name.split(".")
        logger.debug("Parsed fields: {} {}", len(fields), fields)

        if len(fields) < 5:
            logger.debug("Received a non-beacon packet.")
            raise SyntaxError("Not a beacon packet.")

        # Packet format: <preamble><data>.<stream>.<session>.hostname.tld
        #   First 2 bytes of the first subdomain is the preamble
        #   The rest of the first subdomain is encrypted data
        #   The second subdomain is the stream ID
        #   The third subdomain is the session cookie

        packet = Packet(
            domain=".".join(fields[3:]),
            stream_code=fields[1],  # beacon v1 uses a 2 byte stream ID
            session_code=fields[2],  # beacon v1 uses a 4 byte session ID
            preamble=fields[0][:2],
            data=fields[0][2:],  # beacon v1 supports 1-50 bytes of data
            source_ip=source_ip,
        )

        logger.debug("Contains data: {}", ord(fields[0][:2][0]) >= ord(NON_DATA_PREAMBLE[0]))
        logger.debug("Parsed packet: {}", packet)
        return packet


class Stream(BaseModel):
    total_pkts: NonNegativeInt = 0
    pkts: List[Optional[PacketData]] = Field(default_factory=list)
    has_data: bool = False
    expiry: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(seconds=300))

    @validator("pkts", pre=True, always=True)
    def populate_packets(cls, v, values, **kwargs):
        if values["total_pkts"] == 0:
            return []
        if len(v) == values["total_pkts"]:
            return v
        return [None] * values["total_pkts"]

    @property
    def expired(self) -> bool:
        if not self.expiry:
            return True

        return datetime.utcnow() > self.expiry


class Session(BaseModel):
    key: Optional[int] = None
    iv: Optional[int] = None
    outbound_queue: dict = Field(default_factory=dict)
    streams: Dict[str, Stream] = Field(default_factory=dict)
    info: Dict[str, Any] = Field(default_factory=dict)
    interval: Optional[str] = None
    checkins: NonNegativeInt = 0
    version: Optional[NonNegativeInt] = None
    last_seen: Optional[datetime] = None
    source_ip: Optional[IPv4Address] = None
