import json
from pathlib import Path
from typing import Dict, Optional

from loguru import logger
from tinydb import TinyDB, where

from server.adapters.sessions_storage import SessionsStorage
from server.schemas import Session


class TinyDBSessionStorage(SessionsStorage):
    def __init__(self, db_path: Path):
        if not db_path.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self.path = db_path
        self.db = TinyDB(db_path)

    def all_sessions(self) -> Dict[str, Session]:
        all_data = self.db.all()
        logger.debug("All data: {}", all_data)
        parsed = {s["code"]: Session.parse_obj(s["session"]) for s in all_data}
        logger.debug("Parsed: {}", parsed)
        return parsed

    def session(self, session_code: str) -> Optional[Session]:
        if session_code not in self.all_sessions():
            return None
        return Session.parse_obj(
            self.db.search(where("code") == session_code)[0]["session"]  # type: ignore
        )

    def update(self, session_code: str, session: Session) -> None:
        if session_code in self.all_sessions():
            self.db.update({"session": json.loads(session.json())}, where("code") == session_code)
            logger.debug("Updating session {}, {}", session_code, session)
            return
        logger.debug("Inserting session {}, {}", session_code, session)
        self.db.insert(
            {
                "code": session_code,
                "session": json.loads(session.json()),
            }
        )  # type: ignore

    def knows(self, session_code: str) -> bool:
        return session_code in self.all_sessions()
