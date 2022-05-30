import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, Optional

from loguru import logger

from server.adapters.sessions_storage import SessionsStorage
from server.schemas import Session

SQL_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS sessions (
                        code text PRIMARY KEY,
                        session text NOT NULL
                    );"""


class SQLiteSessionsStorage(SessionsStorage):
    def __init__(self, db_path: Path):
        if not db_path.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self.path = str(db_path)

        with self.connection() as conn:
            conn.execute(SQL_CREATE_TABLE)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        yield conn
        conn.close()

    def all_sessions(self) -> Dict[str, Session]:
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM sessions")
            rows = cur.fetchall()
            logger.debug("All data: {}", rows)
            return {row[0]: Session.parse_raw(row[1]) for row in rows}

    def session(self, session_code: str) -> Optional[Session]:
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM sessions WHERE code=?", (session_code,))
            row = cur.fetchone()
            logger.debug("Got data: {}", row)
            if row is None:
                return None
            data = Session.parse_raw(row[1])
            logger.debug("Parsed: {}", data)
            logger.debug("")
            return data

    def update(self, session_code: str, session: Session) -> None:
        with self.connection() as conn:
            sql = """INSERT OR REPLACE INTO sessions (code, session)
                    VALUES (?, ?)"""
            cur = conn.cursor()
            session_data = session.json()
            cur.execute(sql, (session_code, session_data))
            conn.commit()

    def knows(self, session_code: str) -> bool:
        return session_code in self.all_sessions()
