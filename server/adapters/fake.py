from typing import Dict, Optional

from server.adapters.sessions_storage import SessionsStorage
from server.schemas import Session


class FakeSessionStorage(SessionsStorage):
    def __init__(self):
        self.sessions = {}

    def all_sessions(self) -> Dict[str, Session]:
        return self.sessions

    def session(self, session_code: str) -> Optional[Session]:
        return self.sessions.get(session_code)

    def update(self, session_code: str, session: Session) -> None:
        self.sessions[session_code] = session

    def knows(self, session_code: str) -> bool:
        return session_code in self.sessions
