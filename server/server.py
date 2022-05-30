import base64
import json
import os
import socket
from datetime import datetime
from ipaddress import IPv6Address
from random import randint
from typing import Any, Dict, List

from loguru import logger

from server.adapters.sessions_storage import SessionsStorage
from server.packet_parser import assemble_message
from server.schemas import Packet, Session, Stream
from shared.ip_codec import packetize
from shared.utils import calc_common_key, calc_public_key, encode_query, int_to_bytes


class Server:
    def __init__(self, storage: SessionsStorage):
        self.storage = storage
        self.g = 2
        self.p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74
        self.b = (self.p >> 1) + 73

    def packetize(self, message: bytes) -> List[IPv6Address]:
        packets = packetize(message)
        ips = []
        for packet in packets:
            ip = IPv6Address(socket.inet_ntop(socket.AF_INET6, packet))
            logger.debug("Attaching response packet: {} {}", ip, packet)
            ips.append(ip)

        return ips

    def resolve(self, packet: Packet) -> List[IPv6Address]:

        self.append_to_stream(packet)
        logger.debug("Received packet: {}", packet)

        session = self.storage.session(packet.session_code)

        if packet.last():
            session = self.storage.session(packet.session_code)
            if not session:
                raise ValueError("Client must reinitialize: no session")

            session.source_ip = packet.source_ip
            session.last_seen = datetime.utcnow()
            session.checkins += 1
            self.storage.update(packet.session_code, session)

            logger.debug("Persisting session: {}", session)
            message = self.parse_message(
                packet.stream_code,
                packet.session_code,
                packet.contains_data,
            )
            if not message:
                logger.error("Problem with parsing message. Skipping reaction")
                return self.packetize(self.respond_with_random())

            response_message = self.react(
                packet.session_code,
                message,
                packet.contains_data,
            )
            logger.debug("Sending response message: {}", response_message)
            packets = self.packetize(response_message)
            logger.debug("Sending DHE response packets: {}", packets)

            return packets

        return self.packetize(self.respond_with_random())

    def clean_up_stream(self, stream_code: str, session_code: str):
        session = self.storage.session(session_code)
        if not session:
            return
        del session.streams[stream_code]
        self.storage.update(session_code, session)

    def init_dhe(self, session: Session, session_code: str, message: str):
        try:
            client_keypair = json.loads(message)
            if "B" not in client_keypair or "iv" not in client_keypair:
                raise ValueError(
                    "Client must reinitialize: invalid DHE message: {}",
                    client_keypair,
                )
            session.key = calc_common_key(client_keypair["B"], self.b, self.p)
            session.iv = client_keypair["iv"]
            self.storage.update(session_code, session)

        except json.JSONDecodeError:
            logger.error("Problem with parsing JSON keypair. Skipping reaction")
            return self.respond_with_random()

        logger.debug("Sending public key")
        return self.respond_with_public_key()

    def react(
        self,
        session_code: str,
        message: str,
        has_data: bool,
    ) -> bytes:
        session = self.storage.session(session_code)
        if not session:
            raise ValueError("Client must reinitialize: no session")

        if not has_data:  # Means DHE initialization
            logger.debug("Received DHE initialization")
            return self.init_dhe(session, session_code, message)

        logger.warning("Received message with data. Parsing fields")

        try:
            logger.info("Received message: {}", message)
            session_info = self.parse_machine_data(message)
            session.info = session_info
            self.storage.update(session_code, session)
        except json.JSONDecodeError:
            logger.error("Problem with parsing JSON machine data. Skipping reaction")
            raise ValueError("Client is probably broken. Invalid machine data format")
        return self.respond_with_random()

    def parse_machine_data(self, message: str) -> Dict[str, Any]:
        data = json.loads(message)
        logger.debug("Session info: {}", data)
        # return SessionInfo(**data)
        return data

    @property
    def public_key(self) -> int:
        return calc_public_key(self.g, self.b, self.p)

    def respond_with_public_key(self) -> bytes:
        public_key = self.public_key
        logger.debug("Sending public key: {}", public_key)
        return encode_query(int_to_bytes(public_key))

    def respond_with_random(self) -> bytes:
        # Default ACK is a bunch of random data, to make ACKs not look the same on the wire.
        return base64.b16encode(os.urandom(randint(2, 6))).lower()  # nosec

    def append_to_stream(self, packet: Packet):
        session = self.storage.session(packet.session_code)
        if not session and (packet.contains_data or packet.order != 0):
            raise ValueError("Client must reinitialize: no session")

        elif not session:
            session = Session(streams={})
            stream = Stream(total_pkts=packet.out_of, has_data=packet.contains_data)
            session.streams[packet.stream_code] = stream
            logger.debug("Creating new session: {}", session)

        stream = session.streams.get(packet.stream_code)
        logger.debug("Stream in session: {}", stream)
        if not stream:
            stream = Stream(total_pkts=packet.out_of, has_data=packet.contains_data)
            session.streams[packet.stream_code] = stream
            logger.debug("Creating new stream: {}", stream)

        logger.debug("Stream {}", stream)

        if stream.has_data and not packet.contains_data:
            raise ValueError("Client must reinitialize: packet type conflict")

        logger.debug("Packet {}", packet)
        if stream.pkts[packet.order] is not None:
            raise ValueError("Client must reinitialize: duplicate packet")

        if len(stream.pkts) != packet.out_of:
            raise ValueError("Packet overflow")

        session.streams[packet.stream_code].pkts[packet.order] = packet.data
        logger.debug("Persisting session: {}", session)
        self.storage.update(packet.session_code, session)

    def parse_message(self, stream_code: str, session_code: str, has_data: bool):
        session = self.storage.session(session_code)
        if not session:
            raise ValueError("Client must reinitialize: no session")

        stream = session.streams.get(stream_code)
        if not stream:
            raise ValueError("Client must reinitialize: no stream")

        if len(stream.pkts) != stream.total_pkts:
            raise ValueError("Client must reinitialize: missing packets")

        message = assemble_message(session, stream_code, has_data)
        logger.debug("Assembled message: {}", message)
        self.clean_up_stream(stream_code, session_code)
        return message
