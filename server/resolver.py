from ipaddress import IPv4Address

from dnslib import AAAA, QTYPE, RR, DNSRecord
from dnslib.server import BaseResolver
from loguru import logger

from server.records.records import STATIC_RECORDS
from server.schemas import Packet
from server.server import Server


class BeaconResolver(BaseResolver):
    def __init__(self, server: Server):
        self.server = server

    def resolve(self, request: DNSRecord, handler):
        if static_reply := self._static_resolve(request):
            return static_reply

        reply = request.reply()
        source_ip = IPv4Address(handler.client_address[0])
        packet = Packet.from_dns_query(request.q, source_ip)
        for ip in self.server.resolve(packet):
            reply.add_answer(
                RR(
                    request.q.qname,
                    request.q.qtype,
                    ttl=60,
                    rdata=AAAA(str(ip)),
                )
            )
        return reply

    def _static_resolve(self, request):
        reply = request.reply()
        # If a static record exists for this query, respond and stop processing.
        try:
            # First check if we have any records for this name
            static_answers = [
                record
                for record in STATIC_RECORDS
                if str(request.q.qname)[:-1] == record["question"]
            ]

            if static_answers:
                logger.debug(
                    "Static resolver: have domain {}. Checking we have an answer for type {}.",
                    request.q.qname,
                    request.q.qtype,
                    QTYPE[request.q.qtype],
                )

                # Next check if we have any records of the requested type for this name
                # If there is no match, this will throw an IndexError
                static_answer = [
                    record for record in static_answers if record["type"] == QTYPE[request.q.qtype]
                ][0]

                logger.debug(
                    "Static resolver: have answer, {}",
                    static_answer["type"],
                    static_answer,
                )
                reply.add_answer(
                    RR(
                        static_answer["question"],
                        QTYPE.reverse[static_answer["type"]],
                        ttl=60,
                        rdata=static_answer["answer"],
                    )
                )

                if static_answer["type"] in ["NS", "SOA"]:
                    logger.debug(
                        "Static resolver: client is asking for NS or SOA. If we have an NS answer, it will be an additional record."  # noqa: E501
                    )
                    additional_answer = [
                        record
                        for record in STATIC_RECORDS
                        if "ns." + static_answer["question"] in record["question"]
                        if record["type"] == "A"
                    ][0]
                    if additional_answer:
                        logger.debug("Static resolver: added additional record.")
                        reply.add_ar(
                            RR(
                                additional_answer["question"],
                                QTYPE.reverse[additional_answer["type"]],
                                ttl=60,
                                rdata=additional_answer["answer"],
                            )
                        )

                return reply
            return None
        except IndexError:
            # If we have the requested name but not the
            # requested type (MX, A, AAAA, ...) return empty reply
            # NXDomain here would cause the client to think
            # we don't have the requested name in any form
            logger.debug("Static resolver: have domain, but type mismatch. Sending empty reply.")
            return reply
