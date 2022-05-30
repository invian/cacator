from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from loguru import logger

from server.schemas import Session
from shared.aes import decrypt_message
from shared.utils import decode_query, int_to_bytes


def assemble_message(session: Session, stream_code: str, has_data: bool) -> str | None:
    """
    Determine if a message has been completely received.
    If it has been, reassemble and decrypt it.
    """
    if not session:
        raise IndexError("No session for data message. Client must reinitialize.")

    full_message: List[bytes] = []
    # Message completely received. Reassemble packets in order.
    logger.debug("Message completely received. Reassembling packets in order.")
    for packet in session.streams[stream_code].pkts:
        if packet is None:
            logger.error("Missing packet in stream {}", stream_code)
            return None

        logger.debug("PACKET: {}", packet)
        logger.debug("PACKET ENC: {}", packet.encode())

        # Data packets are AES encrypted strings.
        # Non-data packets are plaintext integers/longs.

        full_message.append(packet.encode())

        # Mark the stream for expiry. We can't delete the stream
        # once we're done with it because the client may be
        # repeating requests multiple times, so we need a way to
        # keep track of streams we've completed. If we deleted
        # the stream from memory, the repeat requests would
        # only create the stream again.
        #
        # Mark the stream for deletion 90 seconds from now, which
        # should give the client enough time to receive our response
        # which will cause it to stop sending retries.
        session.streams[stream_code].expiry = datetime.utcnow() + timedelta(seconds=90)

    message = b"".join(full_message)
    return parse_assembled(message, has_data, session.key, session.iv)


def parse_assembled(
    message: bytes,
    has_data: bool,
    key: Optional[int],
    iv: Optional[int],
) -> Optional[str]:
    logger.debug("MESSAGE: {}", message)
    message = decode_query(message)

    logger.debug("Decoded message {}", message)

    if has_data:
        message = message.split(b"|", 1)[1]  # Remove the first part of the message
        # The first part here is the typecode. It's irrelevant without answering to the client.

    logger.debug("Message decoded: {}", message)
    if has_data:
        if not key or not iv:
            logger.error("Session has no key or iv. Can't decrypt message")
            return None
        logger.debug("Decrypting message. Session data: {}", message)
        message = decrypt_message(
            message,
            int_to_bytes(key),
            int_to_bytes(iv),
        )
        logger.debug("Decrypted data message: {}", message)

    decoded = message.decode()
    logger.debug("Message decoded: {}", decoded)
    return decoded
