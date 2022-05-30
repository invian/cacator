from loguru import logger

from server.schemas import Packet, Session, SessionInfo


def handle_dhe_initialization(session: Session, packet: Packet):
    logger.debug("Non-data packet received (Diffie-Hellman exchange)")
    # New session, new stream
    if not session:
        logger.debug("New session {}, new stream", session)
        session = Session(info=SessionInfo(source_ip=packet.source_ip))
