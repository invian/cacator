from abc import ABC, abstractmethod
from typing import Dict, Optional

from server.schemas import Session


class SessionsStorage(ABC):
    @abstractmethod
    def all_sessions(self) -> Dict[str, Session]:
        pass

    @abstractmethod
    def session(self, session_code: str) -> Optional[Session]:
        raise NotImplementedError

    @abstractmethod
    def update(self, session_code: str, session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    def knows(self, session_code: str) -> bool:
        pass
