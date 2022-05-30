from datetime import timedelta
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from server.adapters.fake import FakeSessionStorage
from server.adapters.sqlite import SQLiteSessionsStorage
from server.schemas import Session, Stream


@given(st.builds(Session))
def test_session_write(session: Session):
    session_code = "test"
    fake_repo = FakeSessionStorage()
    path = Path("tests/tmp/test.db")
    if path.exists():
        path.unlink()
    tiny_repo = SQLiteSessionsStorage(path)

    fake_repo.update(session_code, session)
    tiny_repo.update(session_code, session)

    assert fake_repo.all_sessions() == tiny_repo.all_sessions()


@given(st.builds(Session))
def test_session_read(session: Session):
    session_code = "test"
    fake_repo = FakeSessionStorage()
    path = Path("tests/tmp/test.db")
    if path.exists():
        path.unlink()
    tiny_repo = SQLiteSessionsStorage(path)

    fake_repo.update(session_code, session)
    tiny_repo.update(session_code, session)

    assert fake_repo.session(session_code) == tiny_repo.session(session_code)


@settings(deadline=timedelta(milliseconds=200))
@given(st.integers(min_value=1, max_value=50))
def test_stream_persistence(total: int):
    stream = Stream(total_pkts=total)
    session_code = "test"
    session = Session(streams={"aa": stream})

    path = Path("tests/tmp/test.db")
    if path.exists():
        path.unlink()

    repo = SQLiteSessionsStorage(path)
    repo.update(session_code, session)

    session = repo.session("test")
    assert session

    session.streams["aa"].pkts[0] = "hello"
    repo.update(session_code, session)

    session = repo.session("test")

    assert session
    assert session.streams["aa"].pkts[0] == "hello"
